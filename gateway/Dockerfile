# Minimal nginx API Gateway Docker image
FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose HTTP port
EXPOSE 80

# Run nginx in foreground (required for Docker)
CMD ["nginx", "-g", "daemon off;"]
