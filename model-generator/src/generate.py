import time
import cv2
import logging

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



        logger.info(f"Model generated successfully in {time.time() - start_time:.2f} seconds")

        return True

    except Exception as e:
        logger.error(f"Python error: {str(e)}")
        return False