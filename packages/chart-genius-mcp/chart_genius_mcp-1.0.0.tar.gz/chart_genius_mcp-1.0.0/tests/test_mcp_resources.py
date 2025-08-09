import json
import pytest

from chart_genius_mcp.server import ChartGeniusServer


@pytest.mark.asyncio
async def test_list_and_read_resources():
    server = ChartGeniusServer()

    # List templates
    lst = await server._list_resource_templates_handler()  # type: ignore[attr-defined]
    uris = {item["uriTemplate"] for item in lst}
    assert "dataset:sample/sales_small" in uris
    assert "theme:modern" in uris

    # Read dataset
    res = await server._read_resource_handler("dataset:sample/sales_small")  # type: ignore[attr-defined]
    payload = json.loads(res["resource"]["text"])
    assert payload["columns"] == ["month", "sales"]
    assert len(payload["rows"]) >= 3

    # Read theme
    res2 = await server._read_resource_handler("theme:dark")  # type: ignore[attr-defined]
    payload2 = json.loads(res2["resource"]["text"])
    assert payload2["name"] == "dark" 