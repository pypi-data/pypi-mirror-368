from __future__ import annotations


class PostsNamespace:
    def __init__(self, client):
        self.client = client

    async def create(self,
                     topic_id: int,
                     raw: str,
                     reply_to_post_number: int | None = None):
        """
        Create a new post in a topic.
        If reply_to_post_number is provided, this will be a reply to that post.
        """
        payload = {
            "topic_id": topic_id,
            "raw": raw
        }
        if reply_to_post_number is not None:
            payload["reply_to_post_number"] = reply_to_post_number

        return await self.client.post("posts.json", json=payload)

    async def delete(self, post_id: int):
        """Delete a post by its ID."""
        return await self.client.delete(f"posts/{post_id}.json")

    async def get(self, post_id: int):
        """Get a post by its ID."""
        return await self.client.get(f"posts/{post_id}.json")

    async def reply(self, topic_id: int, post_id: int, raw: str):
        """
        Reply to a specific post.

        :param topic_id: ID of the topic to reply in
        :param raw: The content of the reply
        :param post_id: (Optional) The post number to reply to
        """
        payload = {
            "topic_id": topic_id,
            "raw": raw,
            "reply_to_post_number": post_id,
        }

        return await self.client.post("/posts", json=payload)

    async def update(self, post_id: int, raw: str):
        return await self.client.put(
            f"posts/{post_id}.json",
            json={"post": {"raw": raw}},
        )

    # --- Undocumented/Admin Endpoints ---
    async def bookmark(self, post_id: int):
        return await self.client.post(
            "post_actions.json", json={"id": post_id,
                                       "post_action_type_id": 3},
        )

    async def like(self, post_id: int):
        return await self.client.post(
            "post_actions.json",
            json={"id": post_id, "post_action_type_id": 2},
        )
