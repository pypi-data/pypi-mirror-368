from __future__ import annotations


class GroupsNamespace:
    def __init__(self, client):
        self.client = client

    async def create(self, name: str, **kwargs):
        return await self.client.post(
            "groups.json", json={"group": {"name": name, **kwargs}},
        )

    async def get(self, group_id: int):
        return await self.client.get(
            f"groups/{group_id}.json",
        )

    async def list(self):
        return await self.client.get("groups.json")

    # --- Undocumented/Admin Endpoints ---
    async def add_user(self, group_id: int,
                       username: str): return await self.client.post(
        f"groups/{group_id}/members.json", json={"usernames": username},
    )

    async def remove_user(self, group_id: int,
                          username: str): return await self.client.delete(
        f"groups/{group_id}/members.json", params={"username": username},
    )
