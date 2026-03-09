# ---- Stage 1: Build ----
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# En production Docker, l'API est proxifiée par Nginx -> pas besoin d'URL absolue
ENV VITE_API_URL=""

RUN npm run build

# ---- Stage 2: Serve avec Nginx ----
FROM nginx:alpine

# Copie les fichiers buildés
COPY --from=builder /app/dist /usr/share/nginx/html

# Copie la config Nginx avec proxy vers le backend
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
