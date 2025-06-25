FROM node:20
WORKDIR /app
COPY package.json .
RUN npm install -g npm@11.4.2
RUN npm cache clean --force
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]