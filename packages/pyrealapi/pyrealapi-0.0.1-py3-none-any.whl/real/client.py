from __future__ import annotations

import httpx


class Client:
    def __init__(self, **httpx_kwargs):
        self._http = httpx.Client(base_url="https://api.real.vg", **httpx_kwargs)


