FROM node:20-alpine AS builder

WORKDIR /app

COPY ./frontend/package.json ./

RUN yarn install

COPY ./frontend/ ./
RUN yarn run build

CMD ["yarn","run","start"]