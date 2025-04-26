import dotenv from 'dotenv';

const NODE_ENV = process.env.NODE_ENV || 'local';
dotenv.config({ path: `./.env.${NODE_ENV}` });

export const HOST = process.env.HOST || 'localhost';
export const PORT = process.env.PORT || 3000;
export const GENERATOR_URL = process.env.GENERATOR_URL || `${HOST}:5000`;