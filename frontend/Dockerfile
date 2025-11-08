### Build stage
FROM node:16 AS build

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy frontend source
COPY . ./

# Build the app
RUN npm run build

### Production stage - nginx
FROM nginx:alpine

# Copy built frontend
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx config if present
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
