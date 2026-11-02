# Stage 1: Build React SPA
FROM node:24-alpine AS frontend-build

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Stage 2: Production Nginx serving SPA + reverse-proxying API
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Remove default nginx configs - BOTH files needed
RUN rm /etc/nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Copy compiled frontend SPA assets
COPY --from=frontend-build /app/dist /usr/share/nginx/html

# Create directory for static/media files and set permissions
RUN mkdir -p /usr/share/nginx/html/static && \
    mkdir -p /usr/share/nginx/html/media && \
    chown -R nginx:nginx /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/nginx-status/ || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
