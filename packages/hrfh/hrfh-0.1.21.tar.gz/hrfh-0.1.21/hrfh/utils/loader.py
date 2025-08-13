from __future__ import annotations

import glob
import json
from collections.abc import Generator

from hrfh.models import HTTPRequest
from hrfh.models import HTTPResponse
from hrfh.utils.parser import create_http_request_from_json
from hrfh.utils.parser import create_http_response_from_bytes
from hrfh.utils.parser import create_http_response_from_json


def yield_http_response_from_json(
    folder, limit=4,
) -> Generator[HTTPResponse]:
    for index, path in enumerate(glob.glob(f"{folder}/**/*.json", recursive=True)):
        with open(path) as f:
            if index > limit:
                break
            yield create_http_response_from_json(json.load(f))


def yield_http_request_from_json(folder, limit=4) -> Generator[HTTPRequest]:
    for index, path in enumerate(glob.glob(f"{folder}/**/*.json", recursive=True)):
        with open(path) as f:
            if index > limit:
                break
            yield create_http_request_from_json(json.load(f))


def yield_http_response_from_plain(
    folder, limit=4,
) -> Generator[HTTPResponse]:
    for index, path in enumerate(glob.glob(f"{folder}/**/*.txt", recursive=True)):
        with open(path, mode='rb') as f:
            if index > limit:
                break
            yield create_http_response_from_bytes(f.read())
