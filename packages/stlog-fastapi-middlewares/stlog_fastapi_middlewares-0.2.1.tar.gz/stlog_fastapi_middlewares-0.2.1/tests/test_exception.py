import io
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient
import stlog

from stlog_fastapi_middlewares.exception import CustomExceptionHandlingMiddleware


app = FastAPI()
logger = stlog.getLogger("test")
app.add_middleware(CustomExceptionHandlingMiddleware, logger=logger)
client = TestClient(app)


@app.get("/exception")
async def exception():
    raise Exception("test")


def test_exception(log_output: io.StringIO):
    response = client.get("/exception")
    assert response.status_code == 500
    print(log_output.getvalue())
    decoded = json.loads(log_output.getvalue())
    assert decoded["message"] == "an exception occurred"
    assert decoded["level"] == "ERROR"
    assert "Traceback" in decoded["exc_info"]
    assert decoded["source"]["lineno"] > 0
