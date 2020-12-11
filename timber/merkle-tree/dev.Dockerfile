FROM node:11.15

WORKDIR /app

COPY ./package.json ./package-lock.json ./
RUN npm install

EXPOSE 80
CMD npm run dev
