# Frontend Dockerfile
FROM node:18

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

COPY frontend ./

RUN npm run build

CMD ["npm", "start"]

EXPOSE 3000
