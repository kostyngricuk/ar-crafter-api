import { GENERATOR_URL } from "../constants.js";

export const generateModel = (images) => fetch(`${GENERATOR_URL}/model/create`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    image1: images[0].data.toString('base64'),
    image2: images[1].data.toString('base64'),
  })
});