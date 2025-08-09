from __future__ import annotations


class TagsNamespace:
    def __init__(self, client): self.client = client

    async def get(self, tag: str):
        return await self.client.get(
            f"tags/{tag}.json",
        )

    async def list(self):
        return await self.client.get("tags.json")

    # --- Undocumented/Admin Endpoints ---
    async def create_group(self, name: str,
                           **kwargs):
        return await self.client.post(
            "tag_groups.json", json={"tag_group": {"name": name, **kwargs}},
        )

    async def update_group(self, group_id: int,
                           **kwargs):
        return await self.client.put(
            f"tag_groups/{group_id}.json", json={"tag_group": kwargs},
        )
