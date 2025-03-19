# Use a Python 3.10 base image
FROM python:3.10

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends --fix-missing \
    chromium \
    chromium-driver \
    xvfb \
    xauth \
    fonts-liberation \
    fonts-ipafont-gothic \
    fonts-wqy-zenhei \
    fonts-thai-tlwg \
    fonts-kacst \
    fonts-freefont-ttf

# Set environment variables
ENV TZ=UTC \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    DISPLAY=:99

# Set the working directory
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --trusted-host pypi.org --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app 

EXPOSE 8000

# CMD ["uvicorn", "fastapi", "run", "python", "main.py", "--port", "8000"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]