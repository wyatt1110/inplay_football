# Use Node.js LTS version with Python support
FROM node:18-alpine

# Install Python, Chrome, and dependencies for scraping
RUN apk add --no-cache \
    python3 \
    py3-pip \
    chromium \
    chromium-chromedriver \
    && ln -sf python3 /usr/bin/python

# Create virtual environment and install Python dependencies
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip

# Add virtual environment to PATH
ENV PATH="/opt/venv/bin:$PATH"

# Set Chrome binary path for Selenium
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV CHROME_PATH=/usr/bin/chromium-browser

# Set working directory
WORKDIR /app

# Create logs directory
RUN mkdir -p logs

# Copy package files
COPY package*.json ./
COPY requirements.txt ./

# Install Python dependencies
RUN pip install -r requirements.txt

# Install Node.js dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S scraper -u 1001

# Set ownership
RUN chown -R scraper:nodejs /app
USER scraper

# Expose port dynamically (Railway sets PORT env var)
EXPOSE $PORT

# Start the application
CMD ["npm", "start"]
