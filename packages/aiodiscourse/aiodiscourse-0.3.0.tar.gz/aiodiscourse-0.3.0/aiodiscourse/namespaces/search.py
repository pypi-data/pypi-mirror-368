from __future__ import annotations


class SearchNamespace:
    def __init__(self, client):
        self.client = client

    async def iter_results(self, q: str, max_pages=None, concurrency=3):
        params = {"q": q}
        async for topic in self.client.iter_paginated(
                "search.json", "topics", params=params, max_pages=max_pages,
                concurrency=concurrency,
        ):
            yield topic

    async def query(self, q: str):
        return await self.client.get("search.json", params={"q": q})

    # --- Undocumented/Admin Endpoints ---
    async def advanced(self, q: str, search_context=None):
        params = {"q": q}
        if search_context:
            params.update(search_context)
        return await self.client.get("search.json", params=params)
