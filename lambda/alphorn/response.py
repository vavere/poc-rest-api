import json

class Response:
    _cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": True,
    }

    def __init__(self, cors=True, headers=None):
        self._cors = cors
        self._headers = headers

    @property
    def headers(self):
        out = {}
        if self._headers:
            out.update(self._headers)
        if self._cors:
            out.update(self._cors_headers)
        return out

    def __call__(self, body=None, status_code=200):
        return {
            "isBase64Encoded": False,
            "statusCode": status_code,
            "headers": self.headers,
            "body": json.dumps(body) if body is not None else None,
        }

