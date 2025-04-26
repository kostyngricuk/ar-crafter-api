import time
import cv2
import logging

import numpy as np
import open3d as o3d

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_model(image1_path, image2_path, model_path):
    logger.info(f"Starting 3D model generation from {image1_path} and {image2_path}")
    start_time = time.time()

    try:
        # 1. Load and preprocess images
        img1 = cv2.imread(image1_path)
        img2 = cv2.imread(image2_path)

        logger.info(f"Loaded images: {image1_path}, {image2_path}")

        if img1 is None or img2 is None:
            logger.error("Failed to load input images")
            return False

        # Step 1: Image Alignment/Correspondence Finding
        img1_cv = np.array(img1)
        img2_cv = np.array(img2)

        # Placeholder: Use OpenCV for feature detection and matching (hypothetical)
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(img1_cv, None)
        kp2, des2 = orb.detectAndCompute(img2_cv, None)

        # Placeholder: Use OpenCV for feature matching (hypothetical)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)

        #Placeholder: Image alignment
        logger.info("Image alignment/correspondence finding complete.")

        # Step 2: Depth Estimation
        # Placeholder: Use stereo matching to get a disparity map (hypothetical)
        stereo = cv2.StereoSGBM_create(minDisparity=0, numDisparities=16, blockSize=15)
        disparity = stereo.compute(img1_cv, img2_cv)
        logger.info("Depth estimation complete.")

        # Step 3: Point Cloud Generation
        # Camera parameters - these would ideally come from camera calibration
        # but for now let's set some reasonable defaults
        height, width = img1_cv.shape[:2]
        focal_length = 0.8 * width  # Approximation
        cx, cy = width / 2, height / 2  # Principal point at image center
        baseline = 0.1  # Distance between cameras in meters (adjust for scale)

        # Create 3D points from disparity map
        points = []
        colors = []

        for v in range(height):
            for u in range(width):
              disp = disparity[v, u]
              if disp > 0:
                  # Convert from disparity to depth
                  z = (focal_length * baseline) / disp
                  # Back-project to 3D space
                  x = (u - cx) * z / focal_length
                  y = (v - cy) * z / focal_length

                  # Don't add points that are too far away (likely noise)
                  if z < 10:  # Arbitrary cutoff
                    points.append([x, y, z])
                    colors.append(img1_cv[v, u] / 255.0)  # Normalize color values

        # Create point cloud using NumPy
        point_cloud = np.array(points, dtype=np.float64)
        # Convert colors to the required format (RGBA with values from 0 to 1)
        point_colors = np.zeros((len(colors), 4), dtype=np.float64)
        for i, color in enumerate(colors):
            if len(color) == 3:
                point_colors[i, :3] = color
                point_colors[i, 3] = 1.0  # Alpha channel set to 1
            else:
                point_colors[i] = color

        # Create a new mesh from the point cloud
        if len(point_cloud) > 0:
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(point_cloud)

            mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd)

            #mesh.textures = ...

            o3d.io.write_triangle_mesh(model_path, mesh)

            logger.info(f"Model generated successfully in {time.time() - start_time:.2f} seconds")
            return True
        else:
            logger.error("No valid points generated for point cloud")
            return False

    except Exception as e:
        logger.error(f"Python error: {str(e)}")
        return False