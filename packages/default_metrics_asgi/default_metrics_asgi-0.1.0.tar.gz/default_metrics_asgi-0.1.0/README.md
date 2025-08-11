# default_metrics_fastapi [![test](https://github.com/kquiet/python_default_metrics_asgi/actions/workflows/test.yml/badge.svg)](https://github.com/kquiet/python_default_metrics_asgi/actions/workflows/test.yml) [![PyPI version](https://img.shields.io/pypi/v/default_metrics_asgi.svg?color=blue)](https://pypi.org/project/default_metrics_asgi/)

A helper package for collecting default Prometheus metrics in ASGI applications (such as FastAPI, Starlette, etc.).

## Features

- **Automatic request/response metrics**: Tracks request counts, response codes, exceptions, durations, and in-progress requests.
- **Prometheus-compatible**: Exposes metrics in Prometheus text format.
- **Configurable exception logging**: Optionally logs unhandled exceptions at the middleware level.
- **ASGI compatible**: Works with FastAPI, Starlette, and other ASGI frameworks.

## Usage

```python
from fastapi import FastAPI
from default_metrics_asgi import PrometheusMiddleware, metrics

app = FastAPI()
app.add_middleware(PrometheusMiddleware)  # log_exceptions=True by default
app.add_route("/metrics", metrics)

@app.get("/")
async def root():
    return {"message": "Hello, world!"}
```

### Optional: Disable Middleware Exception Logging

```python
app.add_middleware(PrometheusMiddleware, log_exceptions=False)
```

## Metrics Collected

- `api_app_info`: Application info (gauge)
- `api_requests_total`: Total number of requests received by method and path (counter)
- `api_responses_total`: Total number of responses sent by method, path, and status code (counter)
- `api_requests_duration_seconds`: Histogram of request processing time by method and path (histogram)
- `api_exceptions_total`: Total number of exceptions raised by method, path, and exception type (counter)
- `api_requests_in_progress`: Number of requests currently being processed by method and path (gauge)

## Exporting Metrics

Visit `/metrics` endpoint to see the Prometheus metrics.

## License

[MIT License](https://github.com/kquiet/python_default_logging/blob/main/LICENSE)