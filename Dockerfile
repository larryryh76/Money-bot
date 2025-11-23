FROM selenium/standalone-chrome:latest

# Switch to root for pip install
USER root

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Switch back to seluser for security
USER seluser

CMD ["python", "bot.py"]
