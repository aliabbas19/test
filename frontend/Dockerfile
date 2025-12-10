FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Clear npm cache and install dependencies with retry logic
RUN npm cache clean --force && \
    npm install --legacy-peer-deps --prefer-offline --no-audit || \
    npm install --legacy-peer-deps --no-audit

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

