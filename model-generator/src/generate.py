import time
import numpy as np
import cv2
import open3d as o3d
import os
import logging
from scipy.spatial.transform import Rotation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_model(image1_path, image2_path, model_path):
    """
    Generate a 3D model from two images using Structure from Motion techniques.
    
    Args:
        image1_path (str): Absolute path to first image
        image2_path (str): Absolute path to second image
        model_path (str): Absolute path where 3D model will be saved
    
    Returns:
        bool: True if model was successfully generated, False otherwise
    """
    logger.info(f"Starting 3D model generation from {image1_path} and {image2_path}")
    
    try:
        # 1. Load and preprocess images
        img1 = cv2.imread(image1_path)
        img2 = cv2.imread(image2_path)

        logger.info(f"Loaded images: {image1_path}, {image2_path}")
        
        if img1 is None or img2 is None:
            logger.error("Failed to load input images")
            return False
        
        # Convert to grayscale for feature detection
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # 2. Extract features using SIFT
        sift = cv2.SIFT_create()
        kp1, des1 = sift.detectAndCompute(gray1, None)
        kp2, des2 = sift.detectAndCompute(gray2, None)
        
        logger.info(f"Detected {len(kp1)} and {len(kp2)} keypoints in the images")
        
        # 3. Match features
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)
        
        # Apply ratio test to get good matches
        good_matches = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good_matches.append(m)
        
        logger.info(f"Found {len(good_matches)} good feature matches")
        
        if len(good_matches) < 5:
            logger.error("Not enough good matches found between images")
            return False
        
        # 4. Calculate camera matrices
        # Get points from matches
        pts1 = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        pts2 = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        
        # Assume a simple camera model with focal length = 1000
        # and principal point at the center of the image
        h, w = gray1.shape
        K = np.array([
            [1000, 0, w/2],
            [0, 1000, h/2],
            [0, 0, 1]
        ])
        
        # Find the essential matrix
        E, mask = cv2.findEssentialMat(pts1, pts2, K, method=cv2.RANSAC, prob=0.999, threshold=1.0)
        inliers = mask.ravel() == 1
        
        # Recover relative camera poses
        _, R, t, _ = cv2.recoverPose(E, pts1, pts2, K, mask=mask)
        
        logger.info("Camera poses estimated")
        
        # 5. Triangulate points to get 3D coordinates
        # First camera projection matrix (identity rotation and zero translation)
        P1 = np.hstack((np.eye(3, 3), np.zeros((3, 1))))
        P1 = K @ P1
        
        # Second camera projection matrix (using R and t)
        P2 = np.hstack((R, t))
        P2 = K @ P2
        
        # Triangulate
        pts1_inliers = pts1[inliers]
        pts2_inliers = pts2[inliers]
        
        pts1_norm = cv2.undistortPoints(pts1_inliers, K, None)
        pts2_norm = cv2.undistortPoints(pts2_inliers, K, None)
        
        points_4d = cv2.triangulatePoints(P1, P2, pts1_norm, pts2_norm)
        points_3d = points_4d[:3, :] / points_4d[3, :]
        points_3d = points_3d.T
        
        logger.info(f"Generated {points_3d.shape[0]} 3D points")
        
        # 6. Create point cloud
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points_3d)
        
        # Estimate normals
        pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        
        # 7. Create mesh using Poisson reconstruction
        logger.info("Creating mesh from point cloud")
        mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            pcd, depth=8, width=0, scale=1.1, linear_fit=False)
        
        # Remove low-density vertices
        vertices_to_remove = densities < np.quantile(densities, 0.1)
        mesh.remove_vertices_by_mask(vertices_to_remove)
        
        # Ensure model_path directory exists
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # 8. Save the mesh
        o3d.io.write_triangle_mesh(model_path, mesh)
        logger.info(f"3D model saved to {model_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error generating 3D model: {str(e)}")
        return False