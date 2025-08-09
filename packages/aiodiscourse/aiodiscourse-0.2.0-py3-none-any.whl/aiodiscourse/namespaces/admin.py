from __future__ import annotations


class AdminNamespace:
    def __init__(self, client):
        self.client = client

    async def approve_user(self, user_id: int):
        return await self.client.put(f"admin/users/{user_id}/approve")

    async def create_backup(self, with_uploads=False):
        return await self.client.post(
            "admin/backups.json", json={"with_uploads": with_uploads},
        )

    async def download_backup(self, filename: str, token: str):
        return await self.client.get(
            f"admin/backups/{filename}", params={"token": token},
        )

    async def get_user(self, user_id: int):
        return await self.client.get(f"admin/users/{user_id}.json")

    async def list_backups(self):
        return await self.client.get("admin/backups.json")

    async def list_badges(self):
        return await self.client.get("admin/badges.json")

    async def list_users(self, scope="active", page=0):
        return await self.client.get(
            f"admin/users/list/{scope}.json", params={"page": page},
        )

    async def list_user_actions(self, username: str, filter_by=None):
        params = {"username": username}
        if filter_by:
            params["filter"] = filter_by
        return await self.client.get("user_actions.json", params=params)

    # --- Undocumented/Admin Endpoints ---
    async def anonymize_user(self, user_id: int):
        return await self.client.put(f"admin/users/{user_id}/anonymize")

    async def grant_trust(self, user_id: int, level: int):
        return await self.client.put(
            f"admin/users/{user_id}/trust_level", json={"level": level},
        )

    async def set_site_setting(self, key: str, value: str | bool | int):
        return await self.client.put(
            f"admin/site_settings/{key}", json={key: value},
        )


