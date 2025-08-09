import asyncio
import sys

try:
    import click
except ImportError:
    print("The CLI requires the optional 'cli' dependencies. Try: pip install "
          "aiodiscourse[cli]")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from aiodiscourse import AsyncDiscourseClient


@click.group()
@click.option("--url", envvar="DISCOURSE_URL", help="Discourse base URL", required=True)
@click.option("--api-key", envvar="DISCOURSE_APIKEY", help="Discourse API key", required=True)
@click.option("--api-username", envvar="DISCOURSE_API_USERNAME", help="Discourse API username", required=True)
@click.pass_context
def cli(ctx, url, api_key, api_username):
    """CLI for interacting with the aiodiscourse module."""
    # If any are missing, Click will show a friendly "Missing option" error before this runs.
    ctx.obj = AsyncDiscourseClient(base_url=url, api_key=api_key, api_username=api_username)


@cli.command()
@click.argument("topic_id", type=int)
@click.pass_obj
def get_topic(client: AsyncDiscourseClient, topic_id):
    """Fetch and display a topic by ID."""
    async def _get():
        topic = await client.topics.get(topic_id)
        click.echo(topic)
    asyncio.run(_get())

@cli.command("close-topic")
@click.argument("topic_id", type=int)
@click.pass_obj
def close_topic(client: AsyncDiscourseClient, topic_id):
    """Close a topic by its ID."""
    async def _close():
        result = await client.topics.close(topic_id,
                                           **{'message': 'Closed topic.'}
                                           )
        print(result)
        if result.get("success") == "OK":
            click.echo(f"✅ Topic {topic_id} closed.")
        else:
            click.echo(f"⚠️ Failed to close topic {topic_id}: {result}")
    asyncio.run(_close())