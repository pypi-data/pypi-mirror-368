#!/usr/bin/env python3
"""
HTTP Request Fuzzy Hashing CLI Tool

Usage:
    python -m hrfh raw_request.txt
    python -m hrfh -                    # Read from stdin
    echo "GET / HTTP/1.1\nHost: example.com" | python -m hrfh -
    python -m hrfh --help
"""
from __future__ import annotations

import sys
from pathlib import Path

import structlog
import typer
from http_parse import parse

from hrfh.models import HTTPRequest


app = typer.Typer(
    name='hrfh',
    help='HTTP Request Fuzzy Hashing Tool',
    add_completion=False,
)

logger = structlog.get_logger(__name__)


def parse_raw_http_request(raw_data: str) -> HTTPRequest | None:
    """Parse raw HTTP request string into HTTPRequest object using http_parse library"""
    try:
        # Use http_parse library to parse the request
        parsed = parse(raw_data)

        # Convert headers from dict to list of tuples
        headers = [(k, v) for k, v in parsed.headers.items()]

        # Get body as bytes
        body = parsed.body.encode('utf-8') if parsed.body else b''

        logger.info(
            'HTTP request parsed successfully',
            method=parsed.method,
            version=parsed.http_version,
            headers_count=len(headers),
            body_length=len(body),
        )

        return HTTPRequest(
            method=parsed.method,
            version=parsed.http_version,
            headers=headers,
            body=body,
        )

    except Exception as e:
        logger.error(
            'Failed to parse HTTP request',
            error=str(e), exc_info=True,
        )
        return None


@app.command()
def main(
    input_file: str = typer.Argument(
        ...,
        help='Input file path or "-" for stdin',
    ),
    show_masked: bool = typer.Option(
        False,
        '--show-masked',
        '-s',
        help='Show the masked request before hashing',
    ),
    hash_algorithm: str = typer.Option(
        'sha256',
        '--hash-algorithm',
        '-a',
        help='Hash algorithm to use (sha256 or md5)',
    ),
):
    """HTTP Request Fuzzy Hashing Tool

    Parse raw HTTP requests from file or stdin and generate fuzzy hashes.

    Examples:
        python -m hrfh raw_request.txt
        python -m hrfh -                    # Read from stdin
        echo "GET / HTTP/1.1\\nHost: example.com" | python -m hrfh -
        python -m hrfh --show-masked raw_request.txt
    """

    logger.info(
        'Starting HTTP request fuzzy hashing',
        input_file=input_file,
        show_masked=show_masked,
        hash_algorithm=hash_algorithm,
    )

    # Read input from file or stdin
    if input_file == '-':
        # Read from stdin
        logger.info('Reading HTTP request from stdin')
        if sys.stdin.isatty():
            typer.echo(
                'Enter raw HTTP request (press Ctrl+D when done):', err=True,
            )

        try:
            raw_input = sys.stdin.read()
        except KeyboardInterrupt:
            logger.warning('Operation cancelled by user')
            typer.echo('\nOperation cancelled', err=True)
            raise typer.Exit(1)
    else:
        # Read from file
        logger.info('Reading HTTP request from file', file_path=input_file)
        file_path = Path(input_file)
        if not file_path.exists():
            logger.error('Input file not found', file_path=input_file)
            typer.echo(f"Error: File '{input_file}' not found", err=True)
            raise typer.Exit(1)

        if not file_path.is_file():
            logger.error('Input path is not a file', file_path=input_file)
            typer.echo(f"Error: '{input_file}' is not a file", err=True)
            raise typer.Exit(1)

        try:
            raw_input = file_path.read_text(encoding='utf-8')
            logger.info('File read successfully', file_size=len(raw_input))
        except Exception as e:
            logger.error(
                'Failed to read input file',
                file_path=input_file, error=str(e), exc_info=True,
            )
            typer.echo(f"Error reading file '{input_file}': {e}", err=True)
            raise typer.Exit(1)

    if not raw_input.strip():
        logger.warning('No input content provided')
        typer.echo('No input provided', err=True)
        raise typer.Exit(1)

    # Parse the HTTP request
    request = parse_raw_http_request(raw_input)
    if not request:
        logger.error('Failed to parse HTTP request')
        typer.echo('Failed to parse HTTP request', err=True)
        raise typer.Exit(1)

    # Show masked request if requested
    if show_masked:
        logger.info('Displaying masked request')
        typer.echo('=== Masked Request ===')
        typer.echo(request.masked)
        typer.echo()

    # Generate fuzzy hash
    logger.info('Generating fuzzy hash', algorithm=hash_algorithm)
    if hash_algorithm == 'md5':
        import hashlib

        def md5_hash(data):
            return hashlib.md5(data.encode('utf-8')).hexdigest()
        fuzzy_hash = request.fuzzy_hash(hasher=md5_hash)
    else:
        fuzzy_hash = request.fuzzy_hash()

    logger.info(
        'Fuzzy hash generated successfully',
        method=request.method,
        version=request.version,
        headers_count=len(request.headers),
        body_length=len(request.body),
        hash_algorithm=hash_algorithm,
        fuzzy_hash=fuzzy_hash,
    )


if __name__ == '__main__':
    app()
