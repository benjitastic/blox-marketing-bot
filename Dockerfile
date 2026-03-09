# Use a proper Debian base so we have apt-get
FROM node:20-bullseye-slim

USER root

# Install Python, Chromium, and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    chromium \
    libglib2.0-0 \
    libnss3 \
    libfontconfig1 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install n8n globally
RUN npm install -g n8n

# Install Python packages via venv to avoid system pip restrictions
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install playwright

# Tell Playwright to use system Chromium instead of downloading its own
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin
ENV CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium

# Copy scripts
COPY reddit_poster.py /scripts/reddit_poster.py
COPY post_comment.py /scripts/post_comment.py

# n8n data directory
RUN mkdir -p /home/node/.n8n && chown -R node:node /home/node
WORKDIR /home/node

EXPOSE 5678

USER node

CMD ["n8n", "start"]