FROM node:18-slim

WORKDIR /app

COPY package*.json ./
COPY yarn.lock ./

RUN yarn install

EXPOSE 3000

CMD ["yarn", "dev"]
