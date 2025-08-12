"""Forem tap class."""

from __future__ import annotations

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_forem.streams import Articles, Comments

__all__ = ["TapForem"]

STREAM_TYPES = [
    Articles,
    Comments,
]


class TapForem(Tap):
    """Singer tap for the Forem API."""

    name = "tap-forem"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="The Forem API key.",
        ),
        th.Property(
            "tag",
            th.StringType,
            required=True,
            description="Tag for filter articles by.",
        ),
        th.Property(
            "api_url",
            th.StringType,
            default="https://dev.to/api/",
            description="The url for the API service.",
        ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
