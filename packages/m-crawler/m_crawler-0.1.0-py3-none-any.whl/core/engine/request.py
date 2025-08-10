from typing import Any, Callable, Optional, Sequence
from playwright.sync_api import Page

from core.engine.abstract_request import AbstractRequest


class PlayWeightRequest(AbstractRequest):
    __slots__ = ("url", "headers", "params", "download", "actions")

    def __init__(
        self,
        url: str,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        download: bool = False,
        actions: Sequence[Callable[[Page], Any]] = [],
    ) -> None:
        super().__init__(url, headers, params)
        self.download = download
        self.actions: Sequence[Callable[[Page], Any]] = actions
