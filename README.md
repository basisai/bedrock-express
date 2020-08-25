# Bedrock Express

Bedrock Express is a collection of standard model server images that are ready to be deployed on Bedrock. They enable users to deploy models without writing a full API server. Apart from reducing boilerplate, our standard images also meet the following requirements:

- Each image is performance optimised for a specific server and ML framework.
- All images expose the same environment variables and entrypoint script so users can switch to a new base image without changing `serve.py`.
- All servers are instrumented with the latest [bdrk](https://pypi.org/project/bdrk/) client library for prediction logging and metrics.

## User Guide

### Server

Users will need to define a model class in `serve.py` to tell the server how to load and call your model. Our [bdrk](https://pypi.org/project/bdrk/) library provides the `BaseModel` that you should inherit from. For example,

```python
from bedrock_client.bedrock.model import BaseModel


class Model(BaseModel):
    def __init__(self):
        with open("/artefact/model.pkl", "rb") as f:
            self.model = pickle.load(f)

    def predict(self, features: List[List[float]]) -> List[float]:
        return self.model.predict_proba(features)[:, 0].tolist()
```

To verify that it works locally, you may call `model.validate()` after instantiation.

### Pre-process

Optionally, custom `pre_process` and `post_process` functions may be defined to transform the HTTP requests and responses for your model. By default, the following definitions are used.

```python
import json


class BaseModel:
    def pre_process(
        self, http_body: AnyStr, files: Optional[Mapping[str, BinaryIO]] = None
    ) -> List[List[float]]:
        samples = json.loads(http_body)
        return [[float(x) for x in s] for s in samples]

    def post_process(
        self, score: Union[List[float], List[Mapping[str, float]]], prediction_id: str
    ) -> Union[AnyStr, Mapping[str, Any]]:
        return {"result": score, "prediction_id": prediction_id}
```

### Config

If you have exported the training distribution of your model to `/artefact/histogram.prom`, Bedrock Express will automatically instrument your server for tracking its production distribution. You may control whether to track all predictions or only those with top scores by overriding `self.config` attribute.

```python
from bedrock_client.bedrock.model.base import BaseModel, ExpressConfig


class Model(BaseModel):
    def __init__(self):
        self.config = ExpressConfig(log_top_score=False)

    def predict(self, features):
        return self.model.predict_proba(features)[:, 0].tolist()
```

For complete examples, you may refer to the serve.py files in [tests](tests) directory. We support the following model flavours.

1. [LightGBM](tests/lightgbm/model-server/serve.py)
2. [torchvision](tests/torchvision/model-server/serve.py)
3. [pytorch-transformers](tests/transformers/model-server/serve.py)
4. [tensorflow](tests/tf-vision/model-server/serve.py)
5. [tensorflow-transformers](tests/tf-transformers/model-server/serve.py)

## Available Images

### flask-gunicorn

Standard model server image using flask-gunicorn stack. Requires

- Python 3.6+

### fastapi-gunicorn

Standard model server image using fastapi-gunicorn stack. Requires

- Python 3.6+

## Developer Guide

### Build

The root [Dockerfile](Dockerfile) is shared by all Python based images. Simply provide the `APP` build arg using the current directory as your docker build command. For example,

```bash
# To build the flask-gunicorn stack
docker build --build-arg APP=flask-gunicorn . -t flask-gunicorn

# To build the fastapi-gunicorn stack
docker build --build-arg APP=fastapi-gunicorn . -t fastapi-gunicorn
```

### Test

To run tests for all server and framework flavours, simply run `./test.sh` from the repo directory.

Individual images can be tested using `docker-compose` from the current directory by setting the `APP` and `MODEL` environment variables. For example,

```bash
# To test the flask-gunicorn stack with lightgbm model
APP=flask-gunicorn MODEL=lightgbm docker-compose -f tests/docker-compose.yml up --build --abort-on-container-exit --always-recreate-deps

# To test the fastapi-gunicorn stack with lightgbm model
APP=fastapi-gunicorn MODEL=lightgbm docker-compose -f tests/docker-compose.yml up --build --abort-on-container-exit --always-recreate-deps
```
