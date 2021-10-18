ARG BASE=python:3.8.12
FROM ${BASE}

WORKDIR /app

ARG APP=flask-gunicorn
COPY $APP/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY $APP .

# Install cloud tools
ARG CLOUD_SDK_VERSION=360.0.0-0
ARG AWS_CLI_VERSION=1.20.63
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update -y && \
    apt-get install -y google-cloud-sdk=${CLOUD_SDK_VERSION} google-cloud-sdk-app-engine-python=${CLOUD_SDK_VERSION} && \
    gcloud --version && \
    pip install awscli==${AWS_CLI_VERSION} && \
    aws --version

ENV BEDROCK_SERVER_PORT 8080
ENV BEDROCK_SERVER serve
ENV WORKERS 2
ENV LOG_LEVEL INFO

# Add default model file for convenience
COPY tests/lightgbm/model-server/serve.py example_serve.py

CMD ["./entrypoint.sh"]
