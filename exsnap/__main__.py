import asyncio
import json
from os.path import basename, join
from typing import TextIO, List

import aiofiles
import click
from aiohttp import ClientSession
from alive_progress import alive_bar

'''
Snapchat does not want to make it easy for you to request your data. Nobody should need to automate downloading
their data but here we are. Thank you Snapchat, very cool.

Thanks to https://pawelmhm.github.io/asyncio/python/aiohttp/2016/04/22/asyncio-aiohttp.html for the method of
using aiohttp.gather and a semaphore to download many things at once but with a bound on concurrency.
'''


@click.command()
@click.option("-i", default="./memories_history.json", type=click.File())
@click.option("-o", default="./", type=click.Path(file_okay=False, writable=True))
def exsnap(*, i: TextIO, o: str):
    loop = asyncio.get_event_loop()
    # We will use asyncio so we can benefit from it for web requests
    loop.run_until_complete(run(i, o))


async def get_cdn_urls(download_links: List[str]) -> List[str]:
    tasks = []
    # Limit concurrent requests to 100 for no good reason
    concurrency = asyncio.Semaphore(100)

    with alive_bar(len(download_links), "Gathering CDN URLs") as bar:
        async with ClientSession() as session:
            async def bounded_post(url):
                # When it is our turn, make a POST request and read the URL response
                async with concurrency, session.post(url) as response:
                    bar()
                    return await response.text()

            # For all download links in the memories_history.json
            for link in download_links:
                task = asyncio.ensure_future(bounded_post(link))
                tasks.append(task)

            # Wait for all the web requests to finish
            responses = await asyncio.gather(*tasks)

    # Return a list of all the CDN urls
    return list(responses)


async def download_files(cdn_links: List[str], output_directory: str):
    tasks = []
    # Limit concurrent downloads to 3 for no good reason
    concurrency = asyncio.Semaphore(3)

    with alive_bar(len(cdn_links), "Downloading Memories") as bar:
        async with ClientSession() as session:
            async def bounded_download(url):
                # Get the filename and path from the output_directory input and provided CDN url
                filename = join(output_directory, basename(url.split("?")[0]))
                # When it's our turn, download the file, and save it in the specified output directory
                async with concurrency, session.get(url) as response, aiofiles.open(filename, mode="wb") as out_file:
                    bar()
                    # Write the file using aiofiles
                    await out_file.write(await response.read())

            # Download all files form the CDN links provided
            for link in cdn_links:
                task = asyncio.ensure_future(bounded_download(link))
                tasks.append(task)

            # Wait for all the downloads to finish
            await asyncio.gather(*tasks)


async def run(memories_json: TextIO, output_directory: str):
    # Snapchat gives us links that we need to POST to in order to get a real URL we can GET on to download media
    download_links = [memory["Download Link"] for memory in json.loads(memories_json.read())["Saved Media"]]
    cdn_links = await get_cdn_urls(download_links)
    # Now that we finally have the needed links, download all the memory files
    await download_files(cdn_links, output_directory)


if __name__ == "__main__":
    exsnap()
