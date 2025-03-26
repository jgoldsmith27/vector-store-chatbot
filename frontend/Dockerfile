# Use Node.js as the base image
FROM node:18-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (for caching purposes)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the project files into the container
COPY . .

# Build the React app for production
RUN npm run build

# Serve the app using a simple static server (e.g., serve)
RUN npm install -g serve

# Expose the port that the React app will run on
EXPOSE 3000

# Start the React app
CMD ["serve", "-s", "build", "-l", "3000", "--no-clipboard"]

