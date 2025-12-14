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

# Set API URL for production at BUILD time
# ARG is available during build, ENV is for runtime
ARG VITE_API_URL=""
ENV VITE_API_URL=${VITE_API_URL}

# Build application with the environment variable
RUN VITE_API_URL="" npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

