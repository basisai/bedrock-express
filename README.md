# Bedrock Express

Bedrock Express is a collection of standard model server images that are ready to be deployed on Bedrock. They enable users to deploy models without writing a full API server. Apart from reducing boilerplate, our standard images also meet the following requirements:

- Each image is performance optimised for a specific server and ML framework.
- All images expose the same environment variables and entrypoint script so users can switch to a new base image without changing `serve.py`.
- All servers are instrumented with the latest [bdrk](https://pypi.org/project/bdrk/) client library for prediction logging and metrics.

## Quick Start

### Churn Prediction Example

See [bedrock-express-churn-prediction](https://github.com/basisai/bedrock-express-churn-prediction) for a completed example.

### Creating a Model Server

Users will need to define a model class in `serve.py` file to tell the server how to load and call your model for inference. Our [bdrk](https://pypi.org/project/bdrk/) library provides the `BaseModel` that you should inherit from. For example,

```python
import pickle
from typing import List

from bedrock_client.bedrock.model import BaseModel


class Model(BaseModel):
    def __init__(self):
        with open("/artefact/model.pkl", "rb") as f:
            self.model = pickle.load(f)

    def predict(self, features: List[List[float]]) -> List[float]:
        return self.model.predict_proba(features)[:, 0].tolist()


if __name__ == "__main__":
    Model().validate("[[1]]")
```

To verify that it works locally, you may call `model.validate()` after instantiating the model class.

### Deploying on Bedrock

To deploy your model on Bedrock, you will need to create a `bedrock.hcl` file with the following configuration.

```hcl
// Refer to https://docs.basis-ai.com/getting-started/writing-files/bedrock.hcl for more details.
version = "1.0"

serve {
    image = "basisai/express-flask:v0.0.3"
    install = [
        "pip install -r requirements.txt",
    ]
    script = [
        {sh = [
            "/app/entrypoint.sh"
        ]}
    ]

    parameters {
        BEDROCK_SERVER = "serve"
    }
}
```

The [basisai/express-flask](https://hub.docker.com/r/basisai/express-flask) image is hosted on docker hub and should be accessible from your workload environment on Bedrock.

The `install` stanza specifies how to install additional dependencies that your server might need, eg. torchvision or tensorflow. Most valid bash commands will work.

The `script` stanza specifies an entrypoint for your server. This file is predefined in all Bedrock Express images and users generally don't need to change it.

The `parameters` stanza allows you to define additional environment variables to be injected into the server containers. You may override the special `BEDROCK_SERVER` environment variable to tell the entrypoint to load a different module than the default `serve.py`.

## User Guide

### Pre-process & Post-process

Optionally, custom `pre_process` and `post_process` functions may be defined to transform the HTTP requests and responses for your model. By default, the following definitions are used by `BaseModel` class.

```python
import json
from typing import Any, AnyStr, BinaryIO List, Mapping, Optional, Union


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

The `prediction_id` in the response body allows you to look up a specific request at a later time.

### Configuration

If you have exported the feature distribution that your model is trained on to `/artefact/histogram.prom`, Bedrock Express will automatically instrument your server for tracking its production distribution. You may control whether to track all predictions or only those with top scores by overriding `self.config` attribute. For example,

```python
import pickle

from bedrock_client.bedrock.model.base import BaseModel, ExpressConfig


class Model(BaseModel):
    def __init__(self):
        self.config = ExpressConfig(log_top_score=False)
        with open("/artefact/model.pkl", "rb") as f:
            self.model = pickle.load(f)
```

## Supported Model Flavours

Bedrock Express supports ML models trained using most mainstream frameworks, such as sklearn, pytorch, and tensorflow. More specifically, we run e2e tests on the following model flavours before each change.

1. [LightGBM](tests/lightgbm/model-server/serve.py)
2. [torchvision](tests/torchvision/model-server/serve.py)
3. [pytorch-transformers](tests/transformers/model-server/serve.py)
4. [tensorflow](tests/tf-vision/model-server/serve.py)
5. [tensorflow-transformers](tests/tf-transformers/model-server/serve.py)

For complete examples on creating model servers for these flavours, you may refer to individual `serve.py` files in [tests](tests) directory.

If you have requests for supporting a specific flavour, please file an issue on this repository.

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
