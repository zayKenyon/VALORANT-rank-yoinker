FROM nginx:alpine

# Copy static dashboard page to Nginx default folder as index.html
COPY dashboard.html /usr/share/nginx/html/index.html

# Copy assets folder if it exists (for map splashes and backgrounds)
COPY assets /usr/share/nginx/html/assets

# Expose default HTTP port
EXPOSE 80
