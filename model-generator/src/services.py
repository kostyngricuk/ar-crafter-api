import os
import uuid
import time
from datetime import datetime
import base64

from generate import generate_model

def create_path(format='jpg'):
    file_id = uuid.uuid4().hex[:10]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), '../output')
    os.makedirs(output_dir, exist_ok=True)

    return os.path.join(output_dir, f"{file_id}_{timestamp}.{format}")

def get_encoded_model(image1, image2):
    image1_path = create_path('jpg')
    image2_path = create_path('jpg')
    model_path = create_path('glb')

    # Decode base64 images and save them to temporary files
    with open(image1_path, 'wb') as f:
        f.write(base64.b64decode(image1))
    with open(image2_path, 'wb') as f:
        f.write(base64.b64decode(image2))

    res = None

    try:
        start_time = time.time()
        print("3D model generation - START")

        generate_model(image1_path, image2_path, model_path)

        print(f"3D model generation - COMPLETED in {time.time() - start_time:.2f} seconds")

        with open(model_path, 'rb') as f:
            glb_data = f.read()

        res = base64.b64encode(glb_data).decode('utf-8')

    except Exception as e:
        print(f"Error during 3D model generation: {str(e)}")

    finally:
         # Clean up temp files
        os.remove(image1_path)
        os.remove(image2_path)
        if os.path.exists(model_path):
          os.remove(model_path)

        return res