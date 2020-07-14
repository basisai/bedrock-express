# Bedrock Express

Bedrock Express is a collection of standard model server images that are ready to be deployed on Bedrock. They enable users to deploy models without writing a full API server. Apart from reducing boilerplate, our standard images also meet the following requirements.

- Each image is performance optimised for a specific server and ML framework.
- All images expose the same environment variables and entrypoint script so users can switch from one image to another without changing `serve.py`.
- All servers are instrumented with the latest [bdrk](https://pypi.org/project/bdrk/) client library for prediction logging and metrics.

## User Guide

Users will need to define a `Model` class in `serve.py` to tell the server how to load and call your model. For example,

```python
class Model:
    def __init__(self):
        with open("/artefact/model.pkl", "rb") as f:
            self.model = pickle.load(f)

    def predict(self, features: List[float]) -> List[List[float]]:
        return self.model.predict_proba([features])
```

Optionally, custom `pre_process` and `post_process` functions may be defined to transform the HTTP requests and responses for your model. By default, the following definitions are used.

```python
import json


def pre_process(http_body: AnyStr) -> List[float]:
    array = json.loads(http_body)
    return [float(x) for x in array]


def post_process(scores: List[List[float]]) -> List[List[float]]:
    return scores
```

A complete example be be found in this repository's [serve.py](serve.py).

## Available Images

### flask-gunicorn

Standard model server image using flask-gunicorn stack.

### fastapi-gunicorn

Standard model server image using fastapi-gunicorn stack.
