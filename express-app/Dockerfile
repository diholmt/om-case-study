# Use official Node.js LTS image
FROM node:18-alpine

# Set working directory inside container
WORKDIR /app

# Copy package.json (and package-lock.json if it exists)
COPY package*.json ./

# Install dependencies (use npm install instead of npm ci)
RUN npm install --only=production

# Copy application code
COPY express.js .

# Expose the port the app runs on
EXPOSE 4567

# Command to run the application
CMD ["node", "express.js"]