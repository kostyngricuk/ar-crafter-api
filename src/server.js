import express from 'express';
import fileUpload from 'express-fileupload';

import { generateModel } from './services/generator.js';
import { HOST, PORT } from './constants.js';

const app = express();

app.use(fileUpload({
  // Configure file uploads with maximum file size 10MB
  limits: { fileSize: 10 * 1024 * 1024 },

  // Temporarily store uploaded files to disk, rather than buffering in memory
  useTempFiles: true,
  tempFileDir: '/tmp/'
}));

app.get('/', (req, res) => {
  res.send('AR Crafter API');
});

app.post('/model/create', async (req, res) => {
  try {
    const images = req.files.images;
    if (!images || images.length < 2) {
      return res.status(400).send('Two images are required');
    }

    const generatorResponse = await generateModel(images);
    if (generatorResponse.status !== 200) {
      return res.status(500).send('Error generating 3D model');
    }

    // Send .glb back
    res.set('Content-Type', 'model/gltf-binary');
    res.send(Buffer.from(generatorResponse.data, 'base64'));

  } catch (error) {
    console.error(error);
    res.status(500).send(error.response.data || 'Internal Server Error');
  }
});

app.listen(PORT, () => {
  console.info(`Server running: http://${HOST}:${PORT}`);
});
