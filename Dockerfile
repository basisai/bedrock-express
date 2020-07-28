FROM nvidia/cuda:10.0-cudnn7-runtime-ubuntu18.04

WORKDIR /app

# Install python3.8 and pip
RUN echo "deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu bionic main" >> /etc/apt/sources.list \
    && echo "deb-src http://ppa.launchpad.net/deadsnakes/ppa/ubuntu bionic main" >> /etc/apt/sources.list \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F23C5A6CF475977595C89F51BA6932366A755776 \
    && apt-get update && apt-get install -y \
    libgomp1 \
    python3.8 \
    python3-distutils \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s python3.8 /usr/bin/python \
    && (curl https://bootstrap.pypa.io/get-pip.py | python)

ARG APP=flask-gunicorn
COPY $APP/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY $APP .

# To be overriden by user
COPY serve.py .

ENV BEDROCK_SERVER_PORT 8080
ENV BEDROCK_SERVER serve
ENV WORKERS 2

CMD ["./entrypoint.sh"]
