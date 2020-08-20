from importlib import import_module
from os import getenv

from bedrock_client.bedrock.metrics.registry import is_single_value
from bedrock_client.bedrock.metrics.service import ModelMonitoringService
from bedrock_client.bedrock.model import BaseModel
from flask import Flask, Response, current_app, request

serve = import_module(getenv("BEDROCK_SERVER", "serve"))
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
    if isinstance(score, dict):
        pid = current_app.monitor.log_class_probability(
            request_body=request.data, features=features, output=score
        )
    elif is_single_value(score):
        pid = current_app.monitor.log_prediction(
            request_body=request.data, features=features, output=score
        )
    elif all(is_single_value(s) for s in score):
        samples = (
            # Get the index of top score
            [max(enumerate(score), key=lambda p: p[1])[0]]
            if current_app.model.config.log_top_score
            else None
        )
        pid = current_app.monitor.log_sample_probability(
            request_body=request.data, features=features, output=score, samples=samples
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
