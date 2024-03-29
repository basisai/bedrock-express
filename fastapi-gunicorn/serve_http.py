from dataclasses import replace
from datetime import datetime
from importlib import import_module
from logging import getLogger
from os import getenv
from typing import Optional
from uuid import UUID

from bedrock_client.bedrock.model import BaseModel
from boxkite.monitoring.context import PredictionContext
from boxkite.monitoring.registry import is_single_value
from boxkite.monitoring.service import ModelMonitoringService
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

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

app = FastAPI()


# Using middleware decorator causes tests to get stuck
async def middleware(request: Request):
    if not hasattr(request.app, "model"):
        request.app.model = ModelClass()
    if not hasattr(request.app, "monitor"):
        request.app.monitor = ModelMonitoringService()


@app.post("/")
@app.post("/predict")
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
    pid = request.app.monitor.log_prediction(
        request_body=request_data, features=features, output=score
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
        if request.app.model.config.log_top_score
        else [i for i in range(len(score))]
    )
    for i in samples:
        if isinstance(score[i], dict):
            label, _ = max(score[i].items(), key=lambda p: p[1])
            request.app.monitor._live_metrics.observe(
                replace(pred, features=features[i], output=label)
            )
        elif not is_single_value(features[i]):
            request.app.monitor._live_metrics.observe(
                replace(pred, features=features[i], output=score[i])
            )

    return request.app.model.post_process(score=score, prediction_id=pid)


@app.post("/explain/")
@app.post("/explain/<target>")
def explain(target: Optional[str] = None):
    return JSONResponse(
        content={
            "type": "InternalServerError",
            "reason": "Model does not implement 'explain' method",
        },
        status_code=501,
    )


@app.get("/metrics")
async def get_metrics(request: Request):
    """Returns real time feature values recorded by Prometheus"""
    await middleware(request)

    body, content_type = request.app.monitor.export_http(
        params=dict(request.query_params), headers=request.headers
    )
    return Response(body, media_type=content_type)
