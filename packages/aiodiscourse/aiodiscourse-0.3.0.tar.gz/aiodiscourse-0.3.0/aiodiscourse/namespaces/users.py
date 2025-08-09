from __future__ import annotations


class UsersNamespace:
    def __init__(self, client):
        self.client = client

    # --- Documented Endpoints ---
    async def get(self, username: str):
        return await self.client.get(f"users/{username}.json")

    async def create(self,
                     email: str,
                     username: str,
                     name: str = None,
                     password: str = None,
                     active: bool = True,
                     approved: bool = True,
                     **kwargs):
        """
        Create a new user. Admins can bypass email confirmation by setting
        active=True and approved=True.
        """
        payload = {
            "email": email,
            "username": username,
            "active": active,
            "approved": approved,
        }
        if name:
            payload["name"] = name
        if password:
            payload["password"] = password
        payload.update(kwargs)
        return await self.client.post("users.json", json=payload)

    async def iter_directory(self,
                             order="days_visited",
                             period="all",
                             max_pages=None,
                             concurrency=3):
        params = {"order": order, "period": period}
        async for user in self.client.iter_paginated(
                "directory_items.json", "directory_items", params=params,
                max_pages=max_pages, concurrency=concurrency,
        ):
            yield user

    # --- Undocumented/Admin Endpoints ---
    async def deactivate(self, user_id: int):
        return await self.client.put(f"admin/users/{user_id}/deactivate")

    async def suspend(self, user_id: int, reason: str, duration_days: int):
        return await self.client.put(
            f"admin/users/{user_id}/suspend",
            json={"suspend_until": duration_days, "reason": reason},
        )
