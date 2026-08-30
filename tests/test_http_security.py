from __future__ import annotations

import asyncio
from pathlib import Path

from mnemosyne.services.api_server import app
from starlette.types import Message, Scope


ROOT = Path(__file__).resolve().parents[1]
LOCAL_ORIGINS = {
    "http://127.0.0.1:8765",
    "http://localhost:8765",
}


def _source(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _cors_preflight(
    origin: str,
    method: str = "GET",
    request_headers: str | None = None,
) -> tuple[int, dict[str, str]]:
    messages: list[Message] = []
    request_sent = False

    async def receive() -> Message:
        nonlocal request_sent
        if not request_sent:
            request_sent = True
            return {"type": "http.request", "body": b"", "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message: Message) -> None:
        messages.append(message)

    headers = [
        (b"host", b"127.0.0.1:8765"),
        (b"origin", origin.encode("ascii")),
        (b"access-control-request-method", method.encode("ascii")),
    ]
    if request_headers:
        headers.append((b"access-control-request-headers", request_headers.encode("ascii")))

    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "OPTIONS",
        "scheme": "http",
        "path": "/health",
        "raw_path": b"/health",
        "query_string": b"",
        "root_path": "",
        "headers": headers,
        "client": ("127.0.0.1", 50000),
        "server": ("127.0.0.1", 8765),
    }
    asyncio.run(app(scope, receive, send))

    start = next(message for message in messages if message["type"] == "http.response.start")
    response_headers = {
        key.decode("latin-1").lower(): value.decode("latin-1")
        for key, value in start["headers"]
    }
    return start["status"], response_headers


def test_default_server_entrypoints_bind_only_to_loopback() -> None:
    for relative_path in (
        "scripts/run-dev.sh",
        "bin/mnemosyne",
        "packaging/systemd/mnemosyne.service",
    ):
        source = _source(relative_path)
        assert "0.0.0.0" not in source
        assert "--host" in source
        assert "127.0.0.1" in source


def test_cors_allows_only_explicit_local_dashboard_origins() -> None:
    # The dashboard and API are local-only. Keep the browser allowlist exact so
    # arbitrary websites cannot read or mutate a user's local memory service.
    for origin in LOCAL_ORIGINS:
        status, headers = _cors_preflight(origin)
        assert status == 200
        assert headers.get("access-control-allow-origin") == origin

    status, untrusted_headers = _cors_preflight("https://attacker.example")
    assert status == 400
    assert "access-control-allow-origin" not in untrusted_headers


def test_cors_rejects_unapproved_methods_and_headers() -> None:
    status, _ = _cors_preflight("http://127.0.0.1:8765", method="DELETE")
    assert status == 400

    status, _ = _cors_preflight(
        "http://127.0.0.1:8765",
        method="POST",
        request_headers="X-API-Key",
    )
    assert status == 400

    status, headers = _cors_preflight(
        "http://127.0.0.1:8765",
        method="POST",
        request_headers="Content-Type",
    )
    assert status == 200
    assert headers.get("access-control-allow-origin") == "http://127.0.0.1:8765"


def test_dashboard_is_served_from_loopback_instead_of_a_file_origin() -> None:
    # file:// pages send an opaque `null` Origin. Allowing that would expose the
    # local API to unrelated sandboxed documents, so the CLI must open the copy
    # served by the loopback API instead.
    cli = _source("bin/mnemosyne")
    api = _source("mnemosyne/services/api_server.py")

    assert '"http://127.0.0.1:8765/dashboard"' in cli
    assert ".as_uri()" not in cli
    assert '@app.get("/dashboard"' in api


def test_dashboard_does_not_render_memory_or_skill_data_as_html() -> None:
    dashboard = _source("dashboard/mnemosyne-panels.html")

    assert ".innerHTML" not in dashboard
    assert "m.content}</" not in dashboard
    assert "s.name}</" not in dashboard
    assert "s.description}</" not in dashboard

    # Persisted values must flow through textContent on explicit DOM nodes.
    assert "domain.textContent" in dashboard
    assert "content.textContent" in dashboard
    assert "name.textContent" in dashboard
    assert "description.textContent" in dashboard
