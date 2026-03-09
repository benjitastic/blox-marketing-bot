FROM n8nio/n8n:latest

USER root

# Install Python and dependencies
RUN apk add --no-cache python3 py3-pip chromium chromium-chromedriver \
    nss freetype harfbuzz ca-certificates ttf-freefont

# Install Python packages
RUN pip3 install playwright flask --break-system-packages

# Tell Playwright to use the system Chromium we just installed
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin
ENV CHROMIUM_PATH=/usr/bin/chromium-browser

# Copy your scripts into the image
COPY reddit_poster.py /scripts/reddit_poster.py
COPY post_comment.py /scripts/post_comment.py

USER node