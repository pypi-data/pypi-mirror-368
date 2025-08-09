from fastapi import FastAPI
from starlette.applications import Starlette
import logging
from typing_extensions import Annotated, Doc
from typing import Union


class FastAPIHandler:
    def __init__(
        self,
        app: Annotated[
            Union[FastAPI, Starlette],
            Doc(
                """
                instance of FastAPI.

                Read more in the
                [FastAPI site](https://fastapi.tiangolo.com/).
                """
            ),
        ],
        logger: logging.Logger = logging.getLogger(__name__)
    ) -> None:
        self.app = app
        self.logger = logger

    async def __call__(self, event, context):
        return await self.handler(event, context)

    async def handler(self, event, context):
        self.logger.info(f"Incoming event: {event}")

        # Извлечение пути из params.url (Yandex Cloud API Gateway)
        url_param = event.get("params", {}).get("url", "")
        path = "/" + url_param if url_param else "/"

        # Сборка query string
        query_params = event.get("queryStringParameters") or {}
        query_string = "&".join(f"{k}={v}" for k, v in query_params.items()).encode()

        headers = [
            (k.lower().encode(), v.encode())
            for k, v in (event.get("headers") or {}).items()
        ]

        # Подготовка ASGI scope
        scope = {
            "type": "http",
            "http_version": "1.1",
            "method": event.get("httpMethod", "GET"),
            "headers": headers,
            "path": path,
            "raw_path": path.encode(),
            "query_string": query_string,
            "server": ("0.0.0.0", 80),
            "client": ("0.0.0.0", 0),
            "scheme": "https",
        }

        # Тело запроса
        body = event.get("body") or ""
        if event.get("isBase64Encoded", False):
            import base64
            body_bytes = base64.b64decode(body)
        else:
            body_bytes = body.encode()

        # Подготовка ответа
        response_body = b""
        status_code = 200
        response_headers = {}

        async def receive():
            return {"type": "http.request", "body": body_bytes, "more_body": False}

        async def send(message):
            nonlocal response_body, status_code, response_headers
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = {
                    k.decode(): v.decode() for k, v in message["headers"]
                }
            elif message["type"] == "http.response.body":
                response_body += message.get("body", b"")

        await self.app(scope, receive, send)

        return {
            "statusCode": status_code,
            "body": response_body.decode("utf-8"),
            "headers": response_headers,
        }
