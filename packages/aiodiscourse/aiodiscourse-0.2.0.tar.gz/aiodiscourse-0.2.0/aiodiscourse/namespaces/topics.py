from __future__ import annotations

import arrow


class TopicsNamespace:
    def __init__(self, client):
        self.client = client

    async def archive(self, topic_id: int, **kwargs):
        """Archive a topic."""
        until = arrow.now().shift(years=+10).format("YYYY-MM-DD")
        kwargs.update({"until": until})
        return await self.update_status(
            topic_id, status="archived", enabled=True, **kwargs
            )

    async def bump(self, topic_id: int):
        return await self.client.post(
            f"t/{topic_id}/timer", json={"status_type": "bump"},
        )

    async def close(self, topic_id: int, **kwargs):
        """Close a topic."""
        return await self.update_status(
            topic_id, status="closed", enabled=True, **kwargs
            )

    async def create(self, title: str, raw: str, category_id: int = None,
                     **kwargs):
        payload = {"title": title, "raw": raw}
        if category_id:
            payload["category"] = category_id
        payload.update(kwargs)
        return await self.client.post("posts.json", json=payload)

    async def get(self, topic_id: int):
        return await self.client.get(f"t/{topic_id}.json")

    async def hide(self, topic_id: int, **kwargs):
        """Hide a topic (make invisible)."""
        return await self.update_status(
            topic_id, status="visible", enabled=False, **kwargs
            )

    async def iter_latest(self, max_pages=None, concurrency=3):
        async for topic in self.client.iter_paginated(
                "latest.json", "topics", max_pages=max_pages,
                concurrency=concurrency,
        ):
            yield topic

    async def list_latest(self):
        return await self.client.get("latest.json")

    async def pin(self, topic_id: int, **kwargs):
        """Pin a topic."""
        return await self.update_status(
            topic_id, status="pinned", enabled=True, **kwargs
            )

    async def reopen(self, topic_id: int, **kwargs):
        """Reopen a topic."""
        return await self.update_status(
            topic_id, status="closed", enabled=False, **kwargs
            )

    async def reply(self, topic_id: int, raw: str, reply_to_post_number: int | None = None):
        """
        Reply to a topic

        :param topic_id: ID of the topic to reply in
        :param raw: The content of the reply
        """
        payload = {
            "topic_id": topic_id,
            "raw": raw,
        }

        return await self.client.post("/posts", json=payload)

    async def unarchive(self, topic_id: int, **kwargs):
        """Unarchive a topic."""
        return await self.update_status(
            topic_id, status="archived", enabled=False, **kwargs
            )

    async def unhide(self, topic_id: int, **kwargs):
        """Unhide a topic (make visible)."""
        return await self.update_status(
            topic_id, status="visible", enabled=True, **kwargs
            )

    async def unpin(self, topic_id: int, **kwargs):
        """Unpin a topic."""
        return await self.update_status(
            topic_id, status="pinned", enabled=False, **kwargs
            )

    async def update_status(self, topic_id: int, status: str, enabled: bool,
                            **kwargs):
        """
        Update the status of a topic.

        :param topic_id: The ID of the topic.
        :param status: The status type to update ('closed' or 'archived').
        :param enabled: True to enable (close/archive), False to disable.
        :param kwargs: Optional additional parameters like `message`, `until`.
        """
        if isinstance(enabled, bool):
            enabled_str = "true" if enabled else "false"
        else:
            enabled_str = enabled.lower()

        payload = {
            "status": status,
            "enabled": enabled_str,
            **kwargs
        }
        print(payload)

        return await self.client.put(f"/t/{topic_id}/status.json", json=payload)
