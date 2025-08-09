from __future__ import annotations

import aiohttp


class UploadsNamespace:
    def __init__(self, client):
        self.client = client

    async def upload(self, file_bytes, filename: str, type="composer"):
        data = aiohttp.FormData()
        data.add_field("type", type)
        data.add_field("file", file_bytes, filename=filename)
        return await self.client.post("uploads.json", data=data)

    # --- Undocumented/Admin Endpoints ---
    async def upload_avatar(self, user_id: int, file_bytes, filename: str):
        data = aiohttp.FormData()
        data.add_field("file", file_bytes, filename=filename)
        return await self.client.post(f"users/{user_id}/avatar.json", data=data)
