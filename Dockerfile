FROM nvidia/cuda:10.0-cudnn7-runtime-ubuntu18.04

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

ARG APP=flask-gunicorn
COPY $APP/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY $APP .

# To be overriden by user
COPY serve.py .

ENV BEDROCK_SERVER_PORT 8080
ENV BEDROCK_SERVER serve
ENV WORKERS 2

CMD ["./entrypoint.sh"]
