FROM node:16-alpine

WORKDIR /frontend

COPY package*.json ./

RUN npm install

COPY . .

ENV PORT=8081

CMD ["npm", "run", "serve"]