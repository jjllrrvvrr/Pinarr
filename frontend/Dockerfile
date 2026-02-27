# Dockerfile for the Vue.js frontend

# Stage 1: Build the Vue.js application
FROM node:20-alpine as build-stage

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

# Build avec l'URL API depuis une variable d'environnement (défaut: localhost:9994)
ARG VITE_API_URL=http://localhost:9994
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:stable-alpine as production-stage

COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]