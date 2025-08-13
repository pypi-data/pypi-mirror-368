from __future__ import annotations

import http.client
import io
import socket

from hrfh.models import HTTPRequest
from hrfh.models import HTTPResponse


class FakeSocket(socket.socket):
    def __init__(self, bytes_stream):
        # Call parent constructor with required parameters
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self._file = bytes_stream

    def makefile(self, *args, **kwargs):
        return self._file


def create_http_response_from_bytes(data: bytes) -> HTTPResponse:
    response_stream = FakeSocket(io.BytesIO(data))
    response = http.client.HTTPResponse(response_stream)
    response.begin()

    # Convert version to string type
    version_str = str(response.version)
    if response.version == 10:
        version_str = 'HTTP/1.0'
    elif response.version == 11:
        version_str = 'HTTP/1.1'

    return HTTPResponse(
        ip='1.1.1.1',
        port=80,
        version=version_str,
        status_code=response.status,
        status_reason=response.reason,
        # NOTE: the order of headers will be lost if we insist to use response.getheaders()
        headers=response.getheaders(),
        body=response.read(),
    )


def create_http_response_from_json(data: dict):
    # Ensure ip is string type
    ip = data.get('ip', '')
    if ip is None:
        ip = ''

    # Convert headers from dict to list of tuples if needed
    headers = data.get('headers', [])
    if isinstance(headers, dict):
        headers = list(headers.items())

    # Convert body to bytes if it's a string
    body = data.get('body', b'')
    if isinstance(body, str):
        body = body.encode('utf-8')

    return HTTPResponse(
        ip=ip,
        port=data.get('port', 80),
        status_code=data.get('status_code', 200),
        status_reason=data.get('status_reason', 'OK'),
        headers=headers,
        body=body,
    )


def create_http_request_from_json(data: dict):
    # Ensure ip is string type
    ip = data.get('ip', '')
    if ip is None:
        ip = ''

    # Convert headers from dict to list of tuples if needed
    headers = data.get('headers', [])
    if isinstance(headers, dict):
        headers = list(headers.items())

    # Convert body to bytes if it's a string
    body = data.get('body', b'')
    if isinstance(body, str):
        body = body.encode('utf-8')

    return HTTPRequest(
        ip=ip,
        port=data.get('port', 80),
        method=data.get('method', 'GET'),
        version=data.get('version', 'HTTP/1.1'),
        headers=headers,
        body=body,
    )
