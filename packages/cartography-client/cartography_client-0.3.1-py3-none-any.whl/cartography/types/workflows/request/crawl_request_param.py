# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, TypedDict

__all__ = ["CrawlRequestParam"]


class CrawlRequestParam(TypedDict, total=False):
    bucket_name: Required[str]

    crawl_id: Required[str]

    engines: Required[Iterable[Dict[str, object]]]

    url: Required[str]

    absolute_only: bool

    batch_size: int

    depth: int

    keep_external: bool

    max_urls: int

    max_workers: int

    visit_external: bool
