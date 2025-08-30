# EXACT COPY of the ONE successful build - node:18-slim approach
FROM node:18-slim

# Install Python, browsers and dependencies - EXACT copy from working build
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    firefox-esr \
    chromium \
    chromium-driver \
    wget \
    xvfb \
    x11-utils \
    dbus-x11 \
    && rm -rf /var/lib/apt/lists/*

# Install geckodriver - EXACT copy from working build
RUN wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz \
    && tar -xzf /tmp/geckodriver.tar.gz -C /usr/bin \
    && chmod +x /usr/bin/geckodriver \
    && rm /tmp/geckodriver.tar.gz

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

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE $PORT

# Start the application
CMD ["node", "server.js"]