FROM selenium/standalone-chrome:latest
USER seluser
WORKDIR /home/seluser
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]
