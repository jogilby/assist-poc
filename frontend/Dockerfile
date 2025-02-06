# Frontend Dockerfile
FROM node:18

WORKDIR /frontend

COPY package.json package-lock.json ./
RUN npm install

COPY . .

RUN npm run build

CMD ["npm", "start"]

EXPOSE 3000
