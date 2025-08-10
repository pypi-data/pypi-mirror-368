import io
import json
import os
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
import stlog

from stlog_fastapi_middlewares.context import LogContextMiddleware


app = FastAPI()
logger = stlog.getLogger("test")
app.add_middleware(
    LogContextMiddleware,
    logger=logger,
    add_kvs={"foo": "bar"},
    add_pid=True,
    add_request_id=True,
    headers_to_kvs={"x-test-id": "test_id"},
    envs_to_kvs={"FOO2": "foo2"},
)
client = TestClient(app)


@app.get("/foo")
async def foo():
    logger.info("hello world")
    return {"hello", "world"}


@pytest.fixture
def modified_env():
    environ_copy = {}
    for key, value in os.environ.items():
        environ_copy[key] = value
    os.environ["FOO2"] = "bar2"
    yield
    for key, value in environ_copy.items():
        os.environ[key] = value


def test_context(log_output: io.StringIO, modified_env):
    response = client.get("/foo", headers={"x-test-id": "test-123"})
    assert response.status_code == 200
    decoded = json.loads(log_output.getvalue())
    print(json.dumps(decoded, indent=4))
    assert decoded["message"] == "hello world"
    assert decoded["foo"] == "bar"
    assert decoded["foo2"] == "bar2"
    assert decoded["pid"] > 0
    assert len(decoded["request_id"]) > 10
    assert decoded["test_id"] == "test-123"
