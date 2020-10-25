from dataclasses import replace
from datetime import datetime
from importlib import import_module
from logging import getLogger
from os import getenv
from uuid import UUID

from bedrock_client.bedrock.metrics.context import PredictionContext
from bedrock_client.bedrock.metrics.registry import is_single_value
from bedrock_client.bedrock.metrics.service import ModelMonitoringService
from bedrock_client.bedrock.model import BaseModel
from flask import Flask, Response, current_app, request

logger = getLogger()
try:
    serve = import_module(getenv("BEDROCK_SERVER", "serve"))
except ModuleNotFoundError as exc:
    logger.info(f"Loading example_serve.py since BEDROCK_SERVER is not found: {exc}")
    serve = import_module("example_serve")

for key in dir(serve):
    model = getattr(serve, key)
    if isinstance(model, type) and model != BaseModel and issubclass(model, BaseModel):
        ModelClass = model
        break
else:
    raise NotImplementedError("Model class not found")

app = Flask(__name__)


@app.before_first_request
def init_background_threads():
    """Global objects with daemon threads will be stopped by gunicorn --preload flag.
    So instantiate the model monitoring service here instead.
    """
    current_app.model = ModelClass()
    current_app.monitor = ModelMonitoringService()


@app.route("/", methods=["POST"])
def predict():
    # User code to load features
    features = current_app.model.pre_process(http_body=request.data, files=request.files)

    # Compute the probability of the first class (True)
    score = current_app.model.predict(features=features)

    # Log before post_process to allow custom result type
    pid = current_app.monitor.log_prediction(
        request_body=request.data, features=features, output=score
    )

    # Track multiple sample metrics separately
    server_id, timestamp, entity_id = pid.split("/")
    pred = PredictionContext(
        # Dummy values will be replaced later
        request_body="",
        features=[],
        output=0,
        entity_id=UUID(entity_id),
        server_id=server_id,
        created_at=datetime.fromisoformat(timestamp),
    )
    samples = (
        # Get the index of top score
        [max(enumerate(score), key=lambda p: p[1])[0]]
        if current_app.model.config.log_top_score
        else [i for i in range(len(score))]
    )
    for i in samples:
        if isinstance(score[i], dict):
            label, _ = max(score[i].items(), key=lambda p: p[1])
            current_app.monitor._live_metrics.observe(
                replace(pred, features=features[i], output=label)
            )
        elif not is_single_value(features[i]):
            current_app.monitor._live_metrics.observe(
                replace(pred, features=features[i], output=score[i])
            )

    return current_app.model.post_process(score=score, prediction_id=pid)


@app.route("/metrics", methods=["GET"])
def get_metrics():
    """Returns real time feature values recorded by Prometheus
    """
    body, content_type = current_app.monitor.export_http(
        params=request.args.to_dict(flat=False), headers=request.headers,
    )
    return Response(body, content_type=content_type)


if __name__ == "__main__":
    """Starts the Http server"""
    app.run()
