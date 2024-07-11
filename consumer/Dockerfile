FROM python:3.8
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY kafka_consumer.py .
CMD ["python", "kafka_consumer.py"]
VOLUME /app/insights