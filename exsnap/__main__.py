import asyncio
import json
from typing import TextIO

import click


# Snapchat does not want to make it easy for you to request your data.

@click.command()
@click.argument("-i", default="./memories_history.json", type=click.File())
@click.argument("-o", default="./", type=click.Path(file_okay=False, writable=True))
def exsnap(*, _i: TextIO, _o: str):
    loop = asyncio.get_event_loop()
    # We will use asyncio so we can benefit from it for web requests
    loop.run_until_complete(run(_i, _o))

async def run(memories_json: TextIO, output_directory: str):
    # Snapchat gives us links that we need to POST to in order to get a real URL we can GET on to download media
    memory_requests = [memory["Download Link"] for memory in json.loads(memories_json.read())["Saved Media"]]
    print(memory_requests)


if __name__ == "__main__":
    exsnap()
