FROM nginx:1.21-alpine

# Create directory for SSL certificates
RUN mkdir -p /etc/nginx/ssl

# generate certificates
RUN apk add --no-cache openssl && \
    openssl req -x509 -nodes -days 365 \
    -subj "/CN=${MY_IP}" \
    -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/cert.key \
    -out /etc/nginx/ssl/cert.crt

# Copy SSL certificates
# COPY cert.crt /etc/nginx/ssl/
# COPY cert.key /etc/nginx/ssl/

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf 