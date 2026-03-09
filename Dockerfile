FROM n8nio/n8n:latest

USER root

# Install Python and Chromium (Debian-based, so apt-get not apk)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    chromium \
    chromium-driver \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxss1 \
    libasound2 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install playwright flask --break-system-packages

# Tell Playwright to use the system Chromium
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin
ENV CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium

# Copy scripts
COPY reddit_poster.py /scripts/reddit_poster.py
COPY post_comment.py /scripts/post_comment.py

USER node