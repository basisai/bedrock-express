from importlib import import_module
from os import getenv
import json

from bedrock_client.bedrock.metrics.service import ModelMonitoringService
from fastapi import FastAPI, Request, Response

serve = import_module(getenv("BEDROCK_SERVER", "serve"))
model = serve.Model()

app = FastAPI()


@app.middleware("http")
async def init_background_threads(request: Request, call_next):
    if not hasattr(request.app, "monitor"):
        request.app.monitor = ModelMonitoringService()
    response = await call_next(request)
    return response


@app.post("/")
async def predict(request: Request):
    request_json = await request.body()
    # User code to load features
    features = (
        serve.pre_process(request_json)
        if hasattr(serve, "pre_process")
        else [float(x) for x in request_json]
    )

    # Compute the probability of the first class (True)
    score = model.predict(features)

    if hasattr(serve, "post_process"):
        score = serve.post_process(score)

    pid = request.app.monitor.log_prediction(
        request_body=request_json, features=features, output=score,
    )

    return str({"result": score, "prediction_id": pid})


@app.get("/metrics")
def get_metrics(request: Request):
    """Returns real time feature values recorded by Prometheus
    """
    body, content_type = request.app.monitor.export_http(
        params=dict(request.query_params), headers=request.headers,
    )
    return Response(body, media_type=content_type)

