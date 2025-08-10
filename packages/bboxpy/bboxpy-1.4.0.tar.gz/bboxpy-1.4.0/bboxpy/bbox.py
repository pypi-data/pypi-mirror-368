"""Bbox API."""

from __future__ import annotations

import inspect
from typing import Any

from . import api as Api
from .auth import BboxRequests
from .exceptions import AuthorizationError, BboxException


class Bbox(BboxRequests):
    """API Bouygues Bbox router."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize."""

        super().__init__(*args, **kwargs)
        self._load_modules()

    def _load_modules(self) -> None:
        """Instantiate modules."""
        for name, obj in Api.__dict__.items():
            if inspect.isclass(obj):
                setattr(self, name.lower(), obj(self.async_request))

    async def async_login(self) -> None:
        """Login."""
        try:
            await self.async_auth()
        except BboxException as error:
            raise AuthorizationError(error) from error

    async def async_logout(self) -> None:
        """Logout."""
        await self.async_request("logout", "post")

    async def async_get_summary(self) -> Any:
        """Get Bbox state summary."""
        return await self.async_request("summary")

    async def async_raw_request(
        self, path: str, *, method: str = "GET", payload: dict[str, Any] | None = None
    ) -> Any:
        """Request API."""
        return await self.async_request(method=method, path=path, data=payload)

    async def async_close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()

    async def __aenter__(self) -> Bbox:
        """Asynchronous enter."""
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit."""
        await self.async_close()
