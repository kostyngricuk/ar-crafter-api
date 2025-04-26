import { GENERATOR_URL } from "../constants.js";

export const generateModel = (images) => fetch(`${GENERATOR_URL}/generate`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  body: JSON.stringify({
    image1_path: images[0].tempFilePath,
    image2_path: images[1].tempFilePath,
  })
});