# Use Node.js 18 with Python support
FROM node:18-slim

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python command
RUN ln -sf python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY requirements.txt ./

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE $PORT

# Start the application
CMD ["node", "server.js"]
