import asyncio
import json
from os.path import basename
from typing import TextIO, List

import aiofiles
import click
from aiohttp import ClientSession
from alive_progress import alive_bar


# Snapchat does not want to make it easy for you to request your data.

@click.command()
@click.argument("-i", default="./memories_history.json", type=click.File())
@click.argument("-o", default="./", type=click.Path(file_okay=False, writable=True))
def exsnap(*, _i: TextIO, _o: str):
    loop = asyncio.get_event_loop()
    # We will use asyncio so we can benefit from it for web requests
    loop.run_until_complete(run(_i, _o))


async def get_cdn_urls(download_links: List[str]) -> List[str]:
    tasks = []
    concurrency = asyncio.Semaphore(100)

    # https://pawelmhm.github.io/asyncio/python/aiohttp/2016/04/22/asyncio-aiohttp.html
    with alive_bar(len(download_links), "Gathering CDN URLs") as bar:
        async with ClientSession() as session:
            async def bounded_post(url):
                async with concurrency, session.post(url) as response:
                    bar()
                    return await response.text()

            for link in download_links:
                task = asyncio.ensure_future(bounded_post(link))
                tasks.append(task)

            responses = await asyncio.gather(*tasks)

    return list(responses)


async def download_files(cdn_links: List[str], output_directory: str):
    tasks = []
    concurrency = asyncio.Semaphore(3)

    with alive_bar(len(cdn_links), "Downloading Memories") as bar:
        async with ClientSession() as session:
            async def bounded_download(url):
                filename = basename(url.split("?")[0])
                async with concurrency, session.get(url) as response, aiofiles.open(filename, mode="wb") as out_file:
                    bar()
                    await out_file.write(await response.read())

            for link in cdn_links:
                task = asyncio.ensure_future(bounded_download(link))
                tasks.append(task)

            await asyncio.gather(*tasks)


async def run(memories_json: TextIO, output_directory: str):
    # Snapchat gives us links that we need to POST to in order to get a real URL we can GET on to download media
    download_links = [memory["Download Link"] for memory in json.loads(memories_json.read())["Saved Media"]]
    cdn_links = await get_cdn_urls(download_links)
    await download_files(cdn_links, output_directory)


if __name__ == "__main__":
    exsnap()
