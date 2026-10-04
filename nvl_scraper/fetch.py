"""Thin wrapper over Scrapling fetchers with automatic escalation.

Mode "http" uses the fast curl-based ``Fetcher``; "stealth" uses ``StealthyFetcher``
(real browser, Cloudflare solving). "auto" tries HTTP first and escalates to the
browser when the response is blocked or lacks the element we need.
"""

import logging

from scrapling.fetchers import Fetcher, StealthyFetcher

log = logging.getLogger(__name__)


class FetchError(RuntimeError):
    pass


def fetch_http(url: str, timeout: int = 40):
    return Fetcher.get(url, impersonate="chrome", timeout=timeout, stealthy_headers=True)


def fetch_browser(url: str, wait_selector: str | None = None, capture_xhr: str | None = None, timeout_ms: int = 90_000):
    kwargs = dict(
        headless=True,
        solve_cloudflare=True,
        network_idle=True,
        timeout=timeout_ms,
    )
    if wait_selector:
        kwargs["wait_selector"] = wait_selector
    if capture_xhr:
        kwargs["capture_xhr"] = capture_xhr
    return StealthyFetcher.fetch(url, **kwargs)


def fetch(url: str, mode: str = "auto", must_have: str | None = None, capture_xhr: str | None = None):
    """Fetch ``url`` and return a Scrapling Response.

    :param must_have: CSS selector that must exist for the page to count as valid.
    :param capture_xhr: regex of background API calls to capture (forces browser mode).
    """
    if capture_xhr:
        mode = "stealth"

    if mode in ("auto", "http"):
        try:
            page = fetch_http(url)
            if page.status == 200 and (not must_have or page.css(must_have)):
                return page
            log.info("HTTP fetch of %s not usable (status %s), escalating", url, page.status)
        except Exception as exc:  # network/TLS errors -> try browser
            log.info("HTTP fetch of %s failed: %s", url, exc)
        if mode == "http":
            raise FetchError(f"HTTP fetch failed for {url}")

    page = fetch_browser(url, wait_selector=must_have, capture_xhr=capture_xhr)
    if page.status != 200:
        raise FetchError(f"Browser fetch of {url} returned status {page.status}")
    return page
