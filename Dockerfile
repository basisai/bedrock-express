ARG BASE=python:3.8.7
FROM ${BASE}

WORKDIR /app

ARG APP=flask-gunicorn
COPY $APP/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY $APP .

ENV BEDROCK_SERVER_PORT 8080
ENV BEDROCK_SERVER serve
ENV WORKERS 2
ENV LOG_LEVEL INFO

# Add default model file for convenience
COPY tests/lightgbm/model-server/serve.py example_serve.py

CMD ["./entrypoint.sh"]
