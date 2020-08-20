from importlib import import_module
from os import getenv

from bedrock_client.bedrock.metrics.registry import is_single_value
from bedrock_client.bedrock.metrics.service import ModelMonitoringService
from bedrock_client.bedrock.model import BaseModel
from fastapi import FastAPI, Request, Response

serve = import_module(getenv("BEDROCK_SERVER", "serve"))
for key in dir(serve):
    model = getattr(serve, key)
    if isinstance(model, type) and issubclass(model, BaseModel):
        ModelClass = model
        break
else:
    raise NotImplementedError("Model class not found")

app = FastAPI()


# Using middleware decorator causes tests to get stuck
async def middleware(request: Request):
    if not hasattr(request.app, "model"):
        request.app.model = ModelClass()
    if not hasattr(request.app, "monitor"):
        request.app.monitor = ModelMonitoringService()


@app.post("/")
async def predict(request: Request):
    await middleware(request)

    request_data = await request.body()
    request_form = await request.form()
    files = {k: v.file for k, v in request_form.items()}

    # User code to load features
    features = request.app.model.pre_process(http_body=request_data, files=files)

    # Compute the probability of the first class (True)
    score = request.app.model.predict(features=features)

    # Log before post_process to allow custom result type
    if isinstance(score, dict):
        pid = request.app.monitor.log_class_probability(
            request_body=request.data, features=features, output=score
        )
    elif is_single_value(score):
        pid = request.app.monitor.log_prediction(
            request_body=request.data, features=features, output=score
        )
    elif all(is_single_value(s) for s in score):
        samples = (
            # Get the index of top score
            [max(enumerate(score), key=lambda p: p[1])[0]]
            if request.app.model.config.log_top_score
            else None
        )
        pid = request.app.monitor.log_sample_probability(
            request_body=request.data, features=features, output=score, samples=samples
        )

    return request.app.model.post_process(score=score, prediction_id=pid)


@app.get("/metrics")
async def get_metrics(request: Request):
    """Returns real time feature values recorded by Prometheus
    """
    await middleware(request)

    body, content_type = request.app.monitor.export_http(
        params=dict(request.query_params), headers=request.headers,
    )
    return Response(body, media_type=content_type)
