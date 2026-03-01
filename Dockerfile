# Multi-stage Dockerfile for Pinarr
# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend Python
FROM python:3.10-slim AS backend
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./

# Stage 3: Final Nginx image
FROM nginx:alpine

# Install Python and dependencies for backend
RUN apk add --no-cache python3 py3-pip curl

# Copy frontend build
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html

# Copy backend
COPY --from=backend /app /app/backend
WORKDIR /app/backend

# Install Python dependencies in final image
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages || \
    pip3 install --no-cache-dir -r requirements.txt --user

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/api/ || exit 1

EXPOSE 80 8000

ENTRYPOINT ["/entrypoint.sh"]
