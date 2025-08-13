from __future__ import annotations

import os
from typing import Any, Dict, Optional, Type, TypeVar, Union

import httpx
import time
from .errors import ApiError, OlyptikError
from .models import (
    Crawl,
    CrawlResult,
    PaginationResult,
    StartCrawlPayload,
)

T = TypeVar("T")


DEFAULT_TIMEOUT = 15.0


class BaseClient:
    def __init__(self, api_key: str, endpoint: Optional[str] = None, timeout: float = DEFAULT_TIMEOUT):
        self.endpoint = endpoint or os.getenv("OLYPTIK_ENDPOINT", "https://api.olyptik.io")
        self.api_key = api_key
        self.timeout = timeout

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "olyptik-python-sdk/0.1.0 (+https://www.olyptik.io)",
            "Accept": "application/json",
        }


class Olyptik(BaseClient):
    def __init__(self, api_key: str, endpoint: Optional[str] = None, timeout: float = DEFAULT_TIMEOUT):
        super().__init__(api_key=api_key, endpoint=endpoint, timeout=timeout)
        self._client = httpx.Client(timeout=timeout)

    def _handle(self, res: httpx.Response) -> Any:
        if res.status_code >= 400:
            # try json first
            try:
                data = res.json()
                message = data.get("message") or res.text
            except Exception:
                data = None
                message = res.text
            raise ApiError(res.status_code, message, data)
        if res.headers.get("content-type", "").startswith("application/json"):
            return res.json()
        return res.text

    def _request(self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None) -> httpx.Response:
        url = f"{self.endpoint}{path}"
        attempts = 0
        max_attempts = 3
        backoff = 0.5
        while True:
            attempts += 1
            try:
                res = self._client.request(method, url, params=params, json=json, headers=self.headers)
            except httpx.HTTPError as e:
                if attempts >= max_attempts:
                    raise OlyptikError(str(e))
                time.sleep(backoff)
                backoff *= 2
                continue
            if res.status_code in (429, 500, 502, 503):
                if attempts >= max_attempts:
                    return res
                time.sleep(backoff)
                backoff *= 2
                continue
            return res

    def run_crawl(self, payload: Union[Dict[str, Any], StartCrawlPayload]) -> Crawl:
        if isinstance(payload, StartCrawlPayload):
            payload = payload.__dict__
        res = self._request("POST", "/crawls", json=payload)
        data = self._handle(res)
        return Crawl(**data)

    def get_crawl(self, crawl_id: str) -> Crawl:
        res = self._request("GET", f"/crawls/{crawl_id}")
        data = self._handle(res)
        return Crawl(**data)

    def get_crawls(self, page: int = 0) -> PaginationResult[Crawl]:
        res = self._request("GET", "/crawls", params={"page": page})
        data = self._handle(res)
        return PaginationResult[Crawl](**data)  # type: ignore[arg-type]

    def abort_crawl(self, crawl_id: str) -> Crawl:
        res = self._request("PATCH", f"/crawls/{crawl_id}/abort")
        data = self._handle(res)
        return Crawl(**data)

    def get_crawl_results(self, crawl_id: str, page: int = 0, limit: int = 50) -> PaginationResult[CrawlResult]:
        res = self._request("GET", f"/crawls-results/{crawl_id}", params={"page": page, "limit": limit})
        data = self._handle(res)
        return PaginationResult[CrawlResult](**data)  # type: ignore[arg-type]

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "Olyptik":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.close()


class AsyncOlyptik(BaseClient):
    def __init__(self, api_key: str, endpoint: Optional[str] = None, timeout: float = DEFAULT_TIMEOUT):
        super().__init__(api_key=api_key, endpoint=endpoint, timeout=timeout)
        self._client = httpx.AsyncClient(timeout=timeout)

    def _handle(self, res: httpx.Response) -> Any:
        if res.status_code >= 400:
            try:
                data = res.json()
                message = data.get("message") or res.text
            except Exception:
                data = None
                message = res.text
            raise ApiError(res.status_code, message, data)
        if res.headers.get("content-type", "").startswith("application/json"):
            return res.json()
        return res.text

    async def _request(self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None) -> httpx.Response:
        url = f"{self.endpoint}{path}"
        attempts = 0
        max_attempts = 3
        backoff = 0.5
        while True:
            attempts += 1
            try:
                res = await self._client.request(method, url, params=params, json=json, headers=self.headers)
            except httpx.HTTPError as e:
                if attempts >= max_attempts:
                    raise OlyptikError(str(e))
                await _asleep(backoff)
                backoff *= 2
                continue
            if res.status_code in (429, 500, 502, 503):
                if attempts >= max_attempts:
                    return res
                await _asleep(backoff)
                backoff *= 2
                continue
            return res

    async def run_crawl(self, payload: Union[Dict[str, Any], StartCrawlPayload]) -> Crawl:
        if isinstance(payload, StartCrawlPayload):
            payload = payload.__dict__
        res = await self._request("POST", "/crawls", json=payload)
        data = self._handle(res)
        return Crawl(**data)

    async def get_crawl(self, crawl_id: str) -> Crawl:
        res = await self._request("GET", f"/crawls/{crawl_id}")
        data = self._handle(res)
        return Crawl(**data)

    async def get_crawls(self, page: int = 0) -> PaginationResult[Crawl]:
        res = await self._request("GET", "/crawls", params={"page": page})
        data = self._handle(res)
        return PaginationResult[Crawl](**data)  # type: ignore[arg-type]

    async def abort_crawl(self, crawl_id: str) -> Crawl:
        res = await self._request("PATCH", f"/crawls/{crawl_id}/abort")
        data = self._handle(res)
        return Crawl(**data)

    async def get_crawl_results(self, crawl_id: str, page: int = 0, limit: int = 50) -> PaginationResult[CrawlResult]:
        res = await self._request("GET", f"/crawls-results/{crawl_id}", params={"page": page, "limit": limit})
        data = self._handle(res)
        return PaginationResult[CrawlResult](**data)  # type: ignore[arg-type]

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncOlyptik":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        await self.aclose()


async def _asleep(seconds: float) -> None:
    # local import to avoid adding asyncio at module import time
    import asyncio

    await asyncio.sleep(seconds)


