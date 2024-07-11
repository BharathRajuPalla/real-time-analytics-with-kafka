# Use an official Python runtime as a parent image, specifically version 3.8.
FROM python:3.8

# Set the working directory to /app inside the container.
WORKDIR /app

# Copy the requirements.txt file from your host to the current working directory in the container.
COPY requirements.txt .

# Install any needed packages specified in requirements.txt using pip.
RUN pip install -r requirements.txt

# Copy the kafka_consumer.py application from your host to the current working directory in the container.
COPY kafka_consumer.py .

# Run kafka_consumer.py when the container launches.
CMD ["python", "kafka_consumer.py"]

# Define /app/insights as a mountable volume. Data stored here can persist and be shared.
VOLUME /app/insights
