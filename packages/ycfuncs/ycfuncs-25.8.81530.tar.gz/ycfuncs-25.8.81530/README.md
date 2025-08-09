# YcFuncs
Yandex Cloud Functions handler for FastAPI applications

## For what?
I was unable to launch applications written using the [FastAPI](https://fastapi.tiangolo.com/) framework in the form of [Yandex cloud functions](https://yandex.cloud/en/services/functions). So I had to develop an adapter to solve this problem.

## Example
```python
from fastapi import FastAPI
from ycfuncs import FastAPIHandler

# For local launch
app = FastAPI()


@app.get("/")
async def root():
    return 'Hello World!'

# Entry point for launch in Yandex cloud function 
handler = FastAPIHandler(app)
```

#### local launch
Install `uv sync` or `pip install -r requirements.txt`
Run in terminal `uv run fastapi dev --port=5004` or `uvicorn main:app --port=5004`

#### Yandex cloud functions launch
Set entry point to `main.handler`
[Request handler for a function in Python](https://yandex.cloud/en/docs/functions/lang/python/handler)

## Yandex Cloud ApiGateway
Now you can use Yandex Cloud ApiGateway like this:
```yaml
openapi: 3.0.0
info:
  title: Sample API
  version: 1.0.0
servers:
- url: https://yourdomain.apigw.yandexcloud.net
paths:
  /some-prefix/{url+}:
    x-yc-apigateway-any-method:
      x-yc-apigateway-integration:
        payload_format_version: '0.1'
        function_id: your-function-id
        tag: $latest
        type: cloud_functions
        service_account_id: your-service-account
      parameters:
        - name: url
          in: path
          description: path
          required: true
          schema:
            type: string
```
And check `curl -XGET https://yourdomain.apigw.yandexcloud.net/some-prefix/` - you should get "Hello World!".
In this case `{url+}` is your [APIRouter](https://fastapi.tiangolo.com/reference/apirouter/) endpoints.