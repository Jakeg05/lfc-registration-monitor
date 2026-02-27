# Stage 1: Build the React app
FROM node:18-alpine

WORKDIR /app

# Install dependencies first for caching
COPY package.json package-lock.json* ./
RUN npm install

# Copy source code
COPY . .

# Expose port (Vite default is 5173)
EXPOSE 5173

# Start development server
CMD ["npm", "run", "dev", "--", "--host"]
