# fastapi-gunicorn
Model server image using fastapi-uvicorn-gunicorn stack

## Note

- `fastapi` only runs on ASGI servers, so we need to use `uvicorn.workers.UvicornWorker` instead of `gthread` for the `gunicorn` worker class ; see [https://github.com/benoitc/gunicorn/issues/2154](https://github.com/benoitc/gunicorn/issues/2154)
