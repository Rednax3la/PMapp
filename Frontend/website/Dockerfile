# Stage 1: Build the Vue.js application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci --silent

# Pass build-time environment variables
ARG VUE_APP_API_URL=/api
ARG VUE_APP_STRIPE_PUBLISHABLE_KEY=""

ENV VUE_APP_API_URL=$VUE_APP_API_URL
ENV VUE_APP_STRIPE_PUBLISHABLE_KEY=$VUE_APP_STRIPE_PUBLISHABLE_KEY

# Copy source and build
COPY . .
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
