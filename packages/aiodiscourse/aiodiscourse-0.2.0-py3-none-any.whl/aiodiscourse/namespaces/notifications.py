from __future__ import annotations


class NotificationsNamespace:
    def __init__(self, client): self.client = client

    async def list(self):
        return await self.client.get("notifications.json")

    async def mark_read(self, ids: list[int]):
        return await self.client.post(
            "notifications/mark-read.json", json={"notification_ids": ids},
        )

    # --- Undocumented/Admin Endpoints ---
    async def mute(self, topic_id: int):
        return await self.client.post(
            f"t/{topic_id}/notifications", json={"notification_level": 0},
        )
