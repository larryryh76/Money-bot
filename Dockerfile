FROM python:3.12-slim

# Install deps (removed libgconf-2-4)
RUN apt-get update && apt-get install -y wget gnupg unzip curl libglib2.0-0 libnss3 libxss1 libasound2 xvfb

# Download and install Chrome GPG key (apt-key deprecated fix)
RUN wget -q -O /tmp/google-chrome.asc https://dl.google.com/linux/linux_signing_key.pub
RUN mv /tmp/google-chrome.asc /etc/apt/trusted.gpg.d/google-chrome.asc

# Add Chrome repo with signed-by
RUN echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/google-chrome.asc] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Install Chrome
RUN apt-get update && apt-get install -y google-chrome-stable

# Download matching ChromeDriver (from Chrome for Testing – offline-safe)
RUN CHROME_VERSION=$(google-chrome --version | cut -d ' ' -f3 | cut -d '.' -f1) && \
    wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}.0.0.0/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
