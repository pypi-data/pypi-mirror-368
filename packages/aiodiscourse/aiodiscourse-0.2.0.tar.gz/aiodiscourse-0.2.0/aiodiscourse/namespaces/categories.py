from __future__ import annotations


class CategoriesNamespace:
    def __init__(self, client):
        self.client = client

    async def get(self, category_id: int):
        return await self.client.get(
            f"c/{category_id}/show.json",
        )

    async def list(self):
        return await self.client.get("categories.json")

    # --- Undocumented/Admin Endpoints ---
    async def create(self, name: str,
                     color: str = "49A3DF",
                     text_color: str = "FFFFFF"):
        return await self.client.post(
            "categories.json", json={"name": name, "color": color,
                                     "text_color": text_color},
        )
