#!/usr/bin/env python3
"""Verify that Actions can resolve and download a private wiki attachment."""

from __future__ import annotations

import os

from sync_wiki import download_wiki_image


TEST_IMAGE = (
    "https://github.com/user-attachments/assets/"
    "81efc8cb-a734-47bc-8901-4d9cab13034b"
)


def main() -> None:
    token = os.environ.get("BGA_WIKI_READ_TOKEN", "")
    if not token:
        raise RuntimeError("BGA_WIKI_READ_TOKEN is not configured.")

    image_bytes, content_type = download_wiki_image(TEST_IMAGE, token)
    if len(image_bytes) < 1000:
        raise RuntimeError("GitHub returned an unexpectedly small attachment response.")
    print(
        "Automatic private wiki image import succeeded "
        f"({len(image_bytes):,} bytes, {content_type or 'unknown content type'})."
    )


if __name__ == "__main__":
    main()
