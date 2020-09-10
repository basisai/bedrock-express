ARG  PYTHON_VERSION=3.8.5
FROM python:${PYTHON_VERSION}

WORKDIR /app

ARG APP=flask-gunicorn
COPY $APP/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY $APP .

ENV BEDROCK_SERVER_PORT 8080
ENV BEDROCK_SERVER serve
ENV WORKERS 2

# Add default model file for convenience
COPY tests/lightgbm/model-server/serve.py example_serve.py

CMD ["./entrypoint.sh"]
