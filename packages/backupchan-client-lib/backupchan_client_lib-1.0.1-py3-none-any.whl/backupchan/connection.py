import requests
import json
from typing import Generator
from dataclasses import dataclass

@dataclass
class Response:
    json_body: dict | Generator[bytes, None, None] # is a generator when using get_stream
    status_code: int
    headers: dict

class Connection:
    def __init__(self, host: str, port: int, api_key: str):
        # TODO check these
        self.api_key = api_key

        if host.startswith("http://") or host.startswith("https://"):
            server_host = host.rstrip("/")
        else:
            server_host = f"http://{host.rstrip('/')}"
        self.base_url = f"{server_host}:{port}"

    def endpoint_url(self, endpoint: str) -> str:
        return f"{self.base_url}/api/{endpoint.rstrip('/')}"
    
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}

    def get(self, endpoint: str, raise_on_error=False) -> Response:
        response = requests.get(self.endpoint_url(endpoint), headers=self.headers())
        if raise_on_error:
            response.raise_for_status()
        return Response(response.json(), response.status_code, response.headers)

    def get_stream(self, endpoint: str, raise_on_error=False) -> Response:
        response = requests.get(self.endpoint_url(endpoint), headers=self.headers(), stream=True)
        if raise_on_error:
            response.raise_for_status()
        return Response(response.iter_content(chunk_size=8192), response.status_code, response.headers)

    def post(self, endpoint: str, data: dict, raise_on_error=False) -> Response:
        response = requests.post(self.endpoint_url(endpoint), headers=self.headers(), json=data)
        if raise_on_error:
            response.raise_for_status()
        return Response(response.json(), response.status_code, response.headers)

    def post_form(self, endpoint: str, data: dict, files: dict, raise_on_error=False) -> Response:
        response = requests.post(self.endpoint_url(endpoint), headers=self.headers(), data=data, files=files, stream=True)
        if raise_on_error:
            response.raise_for_status()
        return Response(response.json(), response.status_code, response.headers)

    def patch(self, endpoint: str, data: dict, raise_on_error=False) -> Response:
        response = requests.patch(self.endpoint_url(endpoint), headers=self.headers(), json=data)
        if raise_on_error:
            response.raise_for_status()
        return Response(response.json(), response.status_code, response.headers)

    def delete(self, endpoint: str, data: dict, raise_on_error=False) -> Response:
        response = requests.delete(self.endpoint_url(endpoint), headers=self.headers(), json=data)
        if raise_on_error:
            response.raise_for_status()
        return Response(response.json(), response.status_code, response.headers)
