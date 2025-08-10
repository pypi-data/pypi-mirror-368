import io
import json
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient
import stlog
from starlette.types import Scope

from stlog_fastapi_middlewares.access_log import AccessLogMiddleware


app = FastAPI()
logger = stlog.getLogger("test")
app.add_middleware(
    AccessLogMiddleware, logger=logger, add_response_headers={"x-test": "foo"}
)
client = TestClient(app)


def ignore_hook(scope: Scope) -> bool:
    print(scope.get("path"))
    return scope.get("path") == "/foo"


app_with_ignore_hook = FastAPI()
app_with_ignore_hook.add_middleware(
    AccessLogMiddleware,
    logger=logger,
    ignore_hook=ignore_hook,
)
client_with_ignore_hook = TestClient(app_with_ignore_hook)


@app.get("/foo")
async def foo(response: Response):
    response.headers["X-Test"] = "bar"
    return {"hello", "world"}


@app_with_ignore_hook.get("/foo")
async def foo2():
    return {"hello", "world"}


def test_access_log(log_output: io.StringIO):
    response = client.get("/foo")
    assert response.status_code == 200
    decoded = json.loads(log_output.getvalue())
    assert decoded["full_path"] == "/foo"
    assert decoded["status_code"] == 200
    assert decoded["method"] == "GET"
    assert decoded["level"] == "INFO"
    assert decoded["message"] == "access log"


def test_access_log_with_ignore_hook(log_output: io.StringIO):
    response = client_with_ignore_hook.get("/foo")
    assert response.status_code == 200
    assert len(log_output.getvalue()) == 0


def test_access_log_with_response_headers(log_output: io.StringIO):
    response = client.get("/foo", headers={"X-Test": "test"})
    assert response.status_code == 200
    decoded = json.loads(log_output.getvalue())
    assert decoded["foo"] == "bar"
