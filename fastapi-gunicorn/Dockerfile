FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app .

# To be overriden by user
COPY serve.py .

ENV BEDROCK_SERVER_PORT 8080
ENV BEDROCK_SERVER serve
ENV MODULE_NAME serve_http
ENV PORT 8080
ENV WORKER_CLASS uvicorn.workers.UvicornWorker
ENV WORKERS_PER_CORE 2
ENV GUNICORN_CONF /app/gunicorn_config.py
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV TIMEOUT 300

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
