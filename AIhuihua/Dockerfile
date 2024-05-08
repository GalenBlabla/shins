# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install fastapi uvicorn aiofiles pika websocket-client requests requests_toolbelt

# 安装 RabbitMQ 和其他必需的系统工具
RUN apt-get update && \
    apt-get install -y --no-install-recommends apt-utils gnupg curl wget && \
    wget -O- https://packages.rabbitmq.com/rabbitmq-release-signing-key.asc | apt-key add - && \
    echo "deb http://packages.rabbitmq.com/debian buster main" | tee /etc/apt/sources.list.d/rabbitmq.list && \
    apt-get update && \
    apt-get install -y rabbitmq-server && \
    rabbitmq-plugins enable rabbitmq_management

# Make port 80 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run main.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
