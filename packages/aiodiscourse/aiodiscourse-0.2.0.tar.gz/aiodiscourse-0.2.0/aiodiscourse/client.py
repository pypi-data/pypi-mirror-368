import aiohttp, asyncio, sys
from typing import Any, Dict, Optional, AsyncIterator
from .exceptions import DiscourseAPIError

try:
    import orjson

    def _fast_json_load(data: bytes):
        return orjson.loads(data)

except ImportError:
    import json

    def _fast_json_load(data: bytes):
        return json.loads(data)

if sys.version_info < (3, 13):
    raise RuntimeError("aiodiscourse requires Python 3.13+")


class AsyncDiscourseClient:
    def __init__(self, base_url: str,
                 api_key: str,
                 api_username: str,
                 timeout: int = 30):
        if not base_url.endswith('/'):
            base_url += '/'
        # self.base_url = base_url + 'api/'
        self.base_url = base_url
        self.headers = {'Api-Key': api_key, 'Api-Username': api_username,
                        'Accept': 'application/json'}
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        from .namespaces import (
            topics, posts, users, categories, search,
            groups, tags, notifications, uploads, admin,
        )
        self.topics = topics.TopicsNamespace(self)
        self.posts = posts.PostsNamespace(self)
        self.users = users.UsersNamespace(self)
        self.categories = categories.CategoriesNamespace(self)
        self.search = search.SearchNamespace(self)
        self.groups = groups.GroupsNamespace(self)
        self.tags = tags.TagsNamespace(self)
        self.notifications = notifications.NotificationsNamespace(self)
        self.uploads = uploads.UploadsNamespace(self)
        self.admin = admin.AdminNamespace(self)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
        )
        return self

    async def __aexit__(self, *a):
        if self.session:
            await self.session.close()

    async def _request(self, method: str, endpoint: str, params=None, json=None,
                       data=None):
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            )

        url = endpoint if endpoint.startswith(
            "http",
        ) else f"{self.base_url}{endpoint.lstrip('/')}"
        async with self.session.request(
                method,
                url,
                headers=self.headers,
                params=params,
                json=json,
                data=data,
        ) as resp:
            raw = await resp.read()

            # Raise on HTTP error
            if resp.status >= 400:
                raise DiscourseAPIError(
                    f"HTTP {resp.status} {method} {url}: {raw.decode(errors='ignore')}",
                )

            # Handle empty response
            if not raw.strip():
                return {"status": resp.status, "empty": True}

            # Parse JSON body
            try:
                return _fast_json_load(raw)
            except Exception as e:
                raise DiscourseAPIError(
                    f"Failed to parse response from {method} {url}: {e}",
                )

    async def get(self, endpoint, params=None):
        return await self._request('GET', endpoint, params=params)

    async def post(self, endpoint, json=None, data=None):
        return await self._request('POST', endpoint, json=json, data=data)

    async def put(self, endpoint, json=None, data=None):
        return await self._request('PUT', endpoint, json=json, data=data)

    async def delete(self, endpoint, params=None):
        return await self._request('DELETE', endpoint, params=params)

    async def iter_paginated(self, endpoint: str, result_key: str,
                             params: Dict[str, Any] = None,
                             max_pages: int = None, concurrency: int = 3) -> \
    AsyncIterator[Dict[str, Any]]:
        page, next_url = 1, endpoint
        while next_url:
            urls = []
            for _ in range(concurrency):
                if not next_url:
                    break
                resp = await self.get(
                    next_url, params=params if page == 1 else None,
                )
                data = resp.get('topic_list') or resp
                if result_key in data:
                    for item in data[result_key]:
                        yield item
                next_url = data.get('load_more_topics') or data.get(
                    'load_more_users',
                ) or data.get('next_page')
                page += 1
                if max_pages and page > max_pages:
                    return
                if next_url:
                    urls.append(next_url)
            if not urls:
                break
            async with asyncio.TaskGroup() as tg:
                tasks = [tg.create_task(self.get(u)) for u in urls]
                for t in tasks:
                    resp = await t
                    data = resp.get('topic_list') or resp
                    if result_key in data:
                        for item in data[result_key]:
                            yield item
                    next_url = data.get('load_more_topics') or data.get(
                        'load_more_users',
                    ) or data.get('next_page')
                    if max_pages and page >= max_pages:
                        next_url = None
