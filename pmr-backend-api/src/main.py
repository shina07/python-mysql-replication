import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask
from starlette.types import Message

from common.logger import Logger


logger = Logger.getLogger(__name__)

app: FastAPI = FastAPI()


def add_cors_headers(response: JSONResponse):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


@asynccontextmanager
async def lifespan():
    """
    lifespan context manager
    """
    logger.info('lifespan start')

    yield

    logger.info('lifespan end')


def log_request(request, req_body, resp_body):
    # logging level 조절
    logger.info(f'req: ip={request.client.host} method={request.method} path={request.url.path} params={request.query_params} req_body={req_body.decode("utf-8")}')
    logger.info(f'resp: {resp_body.decode("utf-8")}')


async def set_body(request: Request, body: bytes):
    async def receive() -> Message:
        return {'type': 'http.request', 'body': body}
    request._receive = receive


@app.exception_handler(Exception)
async def exception_handler(request, exc: Exception):
    tb = traceback.extract_tb(exc.__traceback__)[-1]
    file_name = tb.filename
    line_number = tb.lineno
    logger.error(f"[Exception] in {file_name}, line {line_number}: {repr(exc)}")
    response = JSONResponse(dict(code=1, errMsg=repr(exc)), 200)
    return add_cors_headers(response)


@app.middleware("http")
async def http_middleware(request, call_next):

    req_body = await request.body()
    await set_body(request, req_body)
    response = await call_next(request)

    res_body = b''
    async for chunk in response.body_iterator:
        res_body += chunk

    task = BackgroundTask(log_request, request, req_body, res_body)
    return Response(
        content=res_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
        background=task
    )


@app.get("/healthcheck")
async def healthcheck() -> object:
    return {"status": "ok"}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8086, reload=True)
