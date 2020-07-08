FROM python:3.8.3

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app .

# To be overriden by user
COPY serve.py .

ENV BEDROCK_SERVER_PORT 8080
ENV BEDROCK_SERVER serve
ENV WORKERS 2

CMD ["./entrypoint.sh"]
