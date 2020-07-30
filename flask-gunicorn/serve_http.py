from importlib import import_module
from os import getenv

from bedrock_client.bedrock.metrics.service import ModelMonitoringService
from flask import Flask, Response, current_app, request

serve = import_module(getenv("BEDROCK_SERVER", "serve"))

app = Flask(__name__)


@app.before_first_request
def init_background_threads():
    """Global objects with daemon threads will be stopped by gunicorn --preload flag.
    So instantiate the model monitoring service here instead.
    """
    current_app.model = serve.Model()
    current_app.monitor = ModelMonitoringService()


@app.route("/", methods=["POST"])
def predict():
    # User code to load features
    features = (
        serve.pre_process(request.data, request.files)
        if hasattr(serve, "pre_process")
        else [float(x) for x in request.json]
    )

    # Compute the probability of the first class (True)
    score = current_app.model.predict(features)

    if hasattr(serve, "post_process"):
        score = serve.post_process(score)

    pid = current_app.monitor.log_prediction(
        request_body=request.json, features=features, output=score,
    )

    return {"result": score, "prediction_id": pid}


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
