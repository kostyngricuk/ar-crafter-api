from fastapi import FastAPI, Response
import os
import logging
from pydantic import BaseModel

from services import get_model

app = FastAPI()

class ModelRequest(BaseModel):
  image1_path: str
  image2_path: str

@app.post('/')
async def generate(request: ModelRequest):
  image1_path = request.image1_path
  image2_path = request.image2_path

  content = get_model(image1_path, image2_path)

  return Response(content=content, media_type="model/gltf-binary")
