#Base image
FROM node:latest


# Set the working directory
WORKDIR /app/frontend

# Copy the package.json and package-lock.json
COPY package*.json ./

# install project dependencies
RUN npm install

# Copy the project files
COPY . .


