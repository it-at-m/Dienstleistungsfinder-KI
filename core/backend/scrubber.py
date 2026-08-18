import asyncio
import warnings
from logging import Logger
from os import getenv

from envtools import getenv_with_exception
from errors import ScrubberTimeoutException
from httpx import AsyncClient, TimeoutException
from logtools import getLogger

logger: Logger = getLogger()

SCRUBBER_ENABLED = getenv("SCRUBBER_ENABLED", "false").lower() == "true"  # Default is false

if SCRUBBER_ENABLED:
    SCRUBBER_ENDPOINT = getenv_with_exception("SCRUBBER_ENDPOINT")
    SCRUBBER_TIMEOUT = int(getenv("SCRUBBER_TIMEOUT", 10))  # Default is 10 seconds
    client = AsyncClient(base_url=SCRUBBER_ENDPOINT, timeout=SCRUBBER_TIMEOUT)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        try:
            # run the blocking API in a thread so it doesn't block asyncio
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, client.get, "/healthz")
        except Exception as e:
            logger.error(f"Failed to connect to scrubber service with error:\n{e}\nExiting.")
            exit(-1)


async def scrub_input(text: str) -> str:
    """
    Scrub the input text using the scrubber service.

    Args:
        text (str): The input text to be scrubbed.

    Returns:
        str: The scrubbed text.
    """
    if SCRUBBER_ENABLED:
        try:
            response = await client.post("/replace", json={"text": text})
            return response.json()["text"]
        except TimeoutException as e:
            logger.error(f"Scrubber request timed out with error:\n{e}")
            raise ScrubberTimeoutException()
    else:
        return text
