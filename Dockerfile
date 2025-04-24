# Use a Python 3.10 base image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    curl \
    unzip \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxrandr2 \
    libgtk-3-0 \
    libgbm-dev \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install matching ChromeDriver
# RUN set -ex && \
#     CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1-3) && \
#     echo "Detected Chrome version: $CHROME_VERSION" && \
#     CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${135.0.7049.95}) && \
#     echo "Using ChromeDriver version: $CHROMEDRIVER_VERSION" && \
#     curl -sSL "https://chromedriver.storage.googleapis.com/${135.0.7049.95}/chromedriver_linux64.zip" -o /tmp/chromedriver.zip && \
#     unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
#     rm /tmp/chromedriver.zip && \
#     chmod +x /usr/local/bin/chromedriver

# Set environment variable for Chrome
ENV CHROME_BIN=/usr/bin/google-chrome

# Set work directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8080

# Start FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]

