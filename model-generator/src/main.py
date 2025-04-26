from fastapi import FastAPI, Response
import os
import uuid
from datetime import datetime

from generate import generate_model

is_test_mode = False
if os.getenv('TEST_MODE') == 'true':
    is_test_mode = True

def generate_file_path(format='jpg'):
    if is_test_mode:
        return os.path.join(os.path.dirname(__file__), '../models', 'testModel.glb')

    file_id = uuid.uuid4().hex[:10]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), '../output')
    os.makedirs(output_dir, exist_ok=True)

    return os.path.join(output_dir, f"{file_id}_{timestamp}.{format}")

def get_model(image1_path, image2_path):
    model_path = generate_file_path('glb')

    res = None

    try:
        if not is_test_mode:
            generate_model(image1_path, image2_path, model_path)

        with open(model_path, 'rb') as f:
            res = f.read()

    except Exception as e:
        print(f"Error during 3D model generation: {str(e)}")

    finally:
        # if os.path.exists(model_path) and not is_test_mode:
        #   os.remove(model_path)

        return res

app = FastAPI()

@app.post('/generate')
async def generate(request: dict):
  image1_path: str = request.get("image1_path", "")
  image2_path: str = request.get("image2_path", "")

  content: bytes = get_model(image1_path, image2_path)

  return Response(content=content, media_type="model/gltf-binary")
