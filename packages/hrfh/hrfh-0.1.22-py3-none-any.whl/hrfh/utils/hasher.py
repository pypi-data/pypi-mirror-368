from __future__ import annotations

import hashlib


def sha256sum(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()
