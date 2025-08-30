# Use Node.js 18 with Python support
FROM node:18-slim

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python command
RUN ln -sf python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Create virtual environment
RUN python3 -m venv /opt/venv

# Add virtual environment to PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copy package files
COPY package*.json ./
COPY requirements.txt ./

# Install Python dependencies in virtual environment
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE $PORT

# Start the application
CMD ["node", "server.js"]
