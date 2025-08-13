from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field

from bs4 import BeautifulSoup

from hrfh.utils.hasher import sha256sum
from hrfh.utils.masker import custom_header_masker
from hrfh.utils.masker import custom_server_masker
from hrfh.utils.masker import mask_sentence
from hrfh.utils.masker import mask_word
from hrfh.utils.tokenizer import tokenize_html


@dataclass
class HTTPRequest:
    ip: str = ''
    port: int = 80
    version: str = 'HTTP/1.1'
    method: str = 'GET'
    headers: list[tuple[str, str]] = field(default_factory=list)
    body: bytes = b''
    _sentence_maskers: list[Callable] = field(
        default_factory=lambda: [mask_sentence],
    )
    _word_maskers: list[Callable] = field(default_factory=lambda: [mask_word])
    _header_masker: Callable = field(
        default_factory=lambda: custom_header_masker,
    )

    def __post_init__(self):
        self.masked: str = self._mask()

    def __repr__(self) -> str:
        return f"<HTTPRequest {self.ip}:{self.port} {self.method}>"

    def _mask(self) -> str:
        self.masked = self._preprocess()
        return self.masked

    def dump(self) -> str:
        lines = [f"{self.method} / {self.version}"]
        for key, value in self.headers:
            lines.append(f"{key}: {value}")
        lines.append('')
        lines.append(self.body.decode('utf-8'))
        return '\r\n'.join(lines)

    def _preprocess(self) -> str:
        header_lines = []
        for key, value in self.headers:
            key, value = self._header_masker(key, value)
            header_lines.append(f"{key}: {value}")
        lines = [f"{self.method} / {self.version}"]
        lines += sorted(header_lines)
        lines.append('')
        lines.append(self.body.decode('utf-8'))
        return '\r\n'.join(lines)

    def fuzzy_hash(self, hasher: Callable[[str], str] = sha256sum) -> str:
        return hasher(self.masked)


@dataclass
class HTTPResponse:
    ip: str = ''
    port: int = 80
    version: str = 'HTTP/1.1'
    status_code: int = 200
    status_reason: str = 'OK'
    headers: list[tuple[str, str]] = field(default_factory=list)
    body: bytes = b''
    _sentence_maskers: list[Callable] = field(
        default_factory=lambda: [mask_sentence],
    )
    _word_maskers: list[Callable] = field(default_factory=lambda: [mask_word])
    _server_masker: Callable = field(
        default_factory=lambda: custom_server_masker,
    )
    _header_masker: Callable = field(
        default_factory=lambda: custom_header_masker,
    )

    def __post_init__(self):
        if self.version == 10:
            self.version = 'HTTP/1.0'
        if self.version == 11:
            self.version = 'HTTP/1.1'
        self.masked: str = self._mask()

    def __repr__(self) -> str:
        return f"<HTTPResponse {self.ip}:{self.port} {self.status_code} {self.status_reason}>"

    def _mask(self) -> str:
        self.masked = self._preprocess()
        return self.masked

    def dump(self) -> str:
        lines = [f"{self.version} {self.status_code} {self.status_reason}"]
        for key, value in self.headers:
            lines.append(f"{key}: {value}")
        lines.append('')
        lines.append(self.body.decode('utf-8'))
        return '\r\n'.join(lines)

    def fuzzy_hash(self, hasher: Callable[[str], str] = sha256sum) -> str:
        return hasher(self.masked)

    def get_masked_tokenized_body(self) -> list[str]:
        soup = BeautifulSoup(self.body, 'html.parser')
        masked_html_tokens = []
        for token in tokenize_html(soup):
            if token.startswith('<') and token.endswith('>'):
                # append html tags
                masked_html_tokens.append(token)
            else:
                # append masked text content
                # TODO: handle random string in javascript by create a abstract syntax tree [1] for <script> tag
                # [1] https://github.com/tree-sitter/py-tree-sitter
                masked_sentence = token
                for masker in self._sentence_maskers:
                    masked_sentence = masker(
                        masked_sentence, word_maskers=self._word_maskers,
                    )
                masked_html_tokens.append(masked_sentence)
        return masked_html_tokens

    def _preprocess(self) -> str:
        header_lines = []
        strip_headers = [
            'expires',
            'date',
            'content-length',
            'location',
            'via',
            'last-modified',
        ]
        shoud_not_mask_headers = [
            'connection',
            'content-type',
            'content-encoding',
            'cache-control',
            'location',
        ]
        headers = self.headers
        for key, value in headers:
            if key.lower() == 'server':
                value = self._server_masker(value)
            elif key.lower() in strip_headers:
                value = 'REMOVED'
            elif key.lower() in shoud_not_mask_headers:
                value = value
            else:
                key, value = self._header_masker(
                    key, value, word_maskers=self._word_maskers,
                )
                # value = mask_sentence(value, word_maskers=self._word_maskers)
            header_lines.append(f"{key}: {value}")
        lines = [f"{self.version} {self.status_code} {self.status_reason}"]
        lines += sorted(header_lines)
        lines.append('')
        # Only add body tokens if body is not empty
        if self.body:
            lines += self.get_masked_tokenized_body()
        return '\r\n'.join(lines)
