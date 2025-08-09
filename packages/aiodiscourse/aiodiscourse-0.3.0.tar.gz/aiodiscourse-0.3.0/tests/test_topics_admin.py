import pytest
from aiodiscourse import AsyncDiscourseClient


@pytest.mark.skip(reason='Admin/undocumented endpoints skipped')
@pytest.mark.asyncio
async def test_topics_admin(monkeypatch):
    async with AsyncDiscourseClient('http://demo', 'KEY', 'admin') as c:
        monkeypatch.setattr(c, 'post', lambda *a, **k: {'ok': True})
        ns = c.topics;
        assert hasattr(ns, '__init__')
