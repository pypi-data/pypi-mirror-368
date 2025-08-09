import pytest
from aiodiscourse import AsyncDiscourseClient


@pytest.mark.asyncio
async def test_topics_list(monkeypatch, discourse_url, api_key, api_user):
    async def fake_list_latest(*args, **kwargs):
        return {'topic_list': []}

    async with AsyncDiscourseClient(discourse_url, api_key, api_user) as client:
        monkeypatch.setattr(client.topics, "list_latest", fake_list_latest)
        latest = await client.topics.list_latest()
        assert 'topic_list' in latest