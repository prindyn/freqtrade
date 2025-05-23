# Use a Node.js base image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and yarn.lock
COPY yarn.lock ./
COPY package.json ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application (already specified in docker-compose.yml, but good for documentation)
# CMD ["npm", "run", "serve"] 
# The command is run by docker-compose, so CMD is not strictly needed here but can be included for clarity
