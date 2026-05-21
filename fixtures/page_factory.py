import hashlib
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from playwright.sync_api import Browser, BrowserContext, Page


TRACE_DIR = Path(__file__).resolve().parent.parent / "test-results"


def _stop_tracing(context, request, tracing_option: str) -> None:
    """Stop tracing and persist the trace path on the current test item."""
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    test_name = request.node.name.split("[")[0]
    node_hash = hashlib.md5(request.node.nodeid.encode("utf-8")).hexdigest()[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    trace_path = TRACE_DIR / f"{test_name}_{node_hash}_{timestamp}.zip"
    context.tracing.stop(path=str(trace_path))
    request.node._trace_path = trace_path
    request.node._trace_mode = tracing_option


def _start_tracing_if_needed(context: BrowserContext, tracing_option: str) -> None:
    if tracing_option in ["on", "retain-on-failure"]:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)


def create_page_with_tracing(
    browser: Browser,
    request,
    browser_context_args: dict,
    storage_state: Optional[Path] = None,
) -> Iterator[Page]:
    """Create a Playwright page and apply the repository's tracing policy."""
    tracing_option = request.config.getoption("--trace-mode")

    context_kwargs = {**browser_context_args}
    if storage_state:
        context_kwargs["storage_state"] = str(storage_state)

    context = browser.new_context(**context_kwargs)
    page = context.new_page()

    _start_tracing_if_needed(context, tracing_option)

    yield page

    if tracing_option in ["on", "retain-on-failure"]:
        _stop_tracing(context, request, tracing_option)

    context.close()


def create_page_from_existing_context_with_tracing(
    context: BrowserContext,
    request,
) -> Iterator[Page]:
    """Create a page from an existing context and apply tracing policy."""
    tracing_option = request.config.getoption("--trace-mode")
    page = context.new_page()

    _start_tracing_if_needed(context, tracing_option)

    yield page

    if tracing_option in ["on", "retain-on-failure"]:
        _stop_tracing(context, request, tracing_option)

    page.close()
