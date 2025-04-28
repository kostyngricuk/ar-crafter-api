import { GENERATOR_URL } from "../constants.js";

export const generateModel = ({ image1_path, image2_path }) => fetch(`${GENERATOR_URL}/generate`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  body: JSON.stringify({
    image1_path,
    image2_path,
  })
});