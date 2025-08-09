import pytest
from aiodiscourse import AsyncDiscourseClient


@pytest.mark.asyncio
async def test_categories(monkeypatch):
    async with AsyncDiscourseClient('http://demo', 'KEY', 'admin') as c:
        monkeypatch.setattr(c, 'get', lambda *a, **k: {'ok': True})
        ns = c.categories;
        assert hasattr(ns, '__init__')


@pytest.mark.skip(reason="Undocumented/admin endpoints not run by default")
@pytest.mark.asyncio
async def test_categories_undocumented(monkeypatch):
    async with AsyncDiscourseClient(
            "https://demo.discourse.org", "KEY", "admin",
    ) as client:
        async def fake_post(endpoint, json=None):
            return {"ok": True, "ns": "categories"}

        monkeypatch.setattr(client, "post", fake_post)
        ns_obj = getattr(client, "categories")
        for m in dir(ns_obj):
            if not m.startswith("_") and m not in ("list_latest", "iter_latest",
                                                   "get", "create", "list",
                                                   "query", "iter_results",
                                                   "iter_directory"):
                method = getattr(ns_obj, m)
                if callable(method):
                    resp = await method(1)
                    assert resp.get("ok") is True
                    break
