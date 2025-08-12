"""REST client handling, including ForemStream base class."""

from __future__ import annotations

import typing as t

from singer_sdk.authenticators import APIKeyAuthenticator
from singer_sdk.pagination import BasePageNumberPaginator
from singer_sdk.streams import RESTStream

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context


class ForemStream(RESTStream[int]):
    """Forem stream class."""

    records_jsonpath = "$[*]"

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["api_url"]  # type: ignore[no-any-return]

    @property
    def authenticator(self) -> APIKeyAuthenticator:
        """Return a new authenticator object."""
        return APIKeyAuthenticator.create_for_stream(
            self,
            key="api-key",
            value=self.config["api_key"],
            location="header",
        )

    @property
    def http_headers(self) -> dict[str, str]:
        """Return the http headers needed."""
        return {
            "User-Agent": f"{self.tap_name}/{self._tap.plugin_version}",
            "Accept": "application/vnd.forem.api-v1+json",
        }


class PaginatedForemStream(ForemStream):
    """Forem stream with pagination."""

    def get_new_paginator(self) -> BasePageNumberPaginator:
        """Get a fresh paginator.

        Returns:
            A new paginator for the Forem API.
        """
        return BasePageNumberPaginator(1)

    def get_url_params(
        self,
        context: Context | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ANN401
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        return {
            "page": next_page_token,
            "per_page": self._page_size,
        }
