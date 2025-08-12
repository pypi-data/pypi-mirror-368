"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

from singer_sdk.testing import get_tap_test_class

from tap_forem.tap import TapForem

SAMPLE_CONFIG = {
    "tag": "sentry",
}

TestTapForem = get_tap_test_class(TapForem, config=SAMPLE_CONFIG)
