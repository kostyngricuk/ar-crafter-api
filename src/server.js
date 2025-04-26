import express from 'express';
import fileUpload from 'express-fileupload';
import cors from 'cors';

import { generateModel } from './services/generator.js';
import { HOST, PORT } from './constants.js';
import { webStreamToNodeReadable } from './utils.js';

const app = express();

// Enable CORS for all routes
app.use(cors({
  origin: '*', // Allow all origins
  methods: ['GET', 'POST'], // Allow GET and POST requests
  allowedHeaders: ['Content-Type', 'Authorization'] // Allow specific headers
}));

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

app.post('/model/generate', async (req, res) => {
  try {
    const images = req.files.images;
    if (!images || images.length < 2) {
      return res.status(400).send('Two images are required');
    }

    const generatorResponse = await generateModel(images);
    if (generatorResponse.status !== 200) {
      return res.status(500).send('Error generating model');
    }

    const nodeReadableStream = webStreamToNodeReadable(generatorResponse.body);

    // Send .glb back
    res.set('Content-Type', 'model/gltf-binary');
    nodeReadableStream.pipe(res);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Internal Server Error', error: error.message });
  }
});

app.listen(PORT, () => {
  console.info(`Server running: http://${HOST}:${PORT}`);
});
