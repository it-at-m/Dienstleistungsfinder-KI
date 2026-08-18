import logging
import logging.config
import string
from os import getenv

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from httpx import Client, Response
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from src.data_models import ArticleInfo, CollectionArtifact
from src.logtools import getLogger

logger = getLogger()
base_url = "https://stadt.muenchen.de"
client: Client | None = None
collection: dict[str, dict[str, str | list[str]]] = {}


def get_links(url: str) -> list[tuple[str, str]]:
    """Retrieves all the links from the given URL.

    Parameters:
        url (str): The URL to retrieve links from.

    Returns:
        list[tuple[str, str]]: A list of tuples containing the URL as first and the link title as second element.
    """
    assert client is not None, "Client must be initialized before calling get_links"
    # Step 1: Send a GET request to the given URL
    response = client.get(url)

    # Step 2: Parse the HTML content of the response using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Step 3: Find all the <a> tags in the parsed HTML content
    links = soup.find_all("a")

    # Step 4: Extract the href attribute from each <a> tag and filter out None values
    return [(link.get("href"), link.get_text()) for link in links if link.get("href") is not None]  # type: ignore


def add_to_collection(article_id: int, article_title: str, keyword: str) -> None:
    """
    Adds an item to the collection.

    Parameters:
        article_id (int): The ID of the article.
        article_title (str): The title of the article.
        keyword (str): The keyword associated with the article.

    Returns:
        None
    """
    keyword = keyword.strip()  # Remove leading and trailing whitespaces

    if str(article_id) not in collection.keys():
        collection[str(article_id)] = {
            "name": article_title,
            "apiUrl": f"https://stadt.muenchen.de/service/rs/befi/services/{article_id}/description/",
            "keywords": [keyword],
        }
    else:
        collection[str(article_id)]["keywords"].append(keyword)  # type: ignore


def handle_301(response: Response) -> tuple[int | None, str]:  # type: ignore
    """
    Handle a 301 response by recursively following the redirected link and retrieving the article information.

    Args:
        response (Client): The initial response object containing the 301 redirect.

    Returns:
        tuple[int | None, str]: A tuple containing the article ID and title if successful, otherwise None and an empty string
    """
    # Step 1: Get the redirected link from the response headers
    referred_link = response.headers["location"]

    assert client is not None, "Client must be initialized before calling handle_301"
    # Step 2: Retrieve the article information from the redirected link
    article_response = client.get(referred_link)

    # Step 3: Check if the article response is successful
    if article_response.status_code == 200:
        # Step 4: Parse the HTML content of the article response
        soup = BeautifulSoup(article_response.text, "html.parser")

        # Step 5: Extract the article ID from the redirected link
        if article_id := get_id(response.headers["location"]):
            # Step 6: Extract the article title from the parsed HTML content
            title = soup.find("h1").text  # type: ignore
            # Step 7: Return the article ID and title
            return article_id, title
        else:
            return (None, "")
    elif article_response.status_code == 301:
        # Step 8: Handle the 301 response recursively
        return handle_301(article_response)


def get_id(link: str) -> int | None:
    """
    Extracts the article ID from the given link.

    Links have one of two formats:
    - /service/info/{article_name}/{id}/
    - /service/info/{article_name}/{id}/n0/

    Args:
        link (str): The link to extract the article ID from.

    Returns:
       int | None: The extracted article ID or None if the ID could not be parsed.
    """
    if link.endswith("/n0/"):
        article_id = link.split("/")[-3]
    else:
        article_id = link.split("/")[-2]

    try:
        return int(article_id)
    except ValueError:
        logger.warning(f"Could not parse article ID {article_id} to integer; skipping article")
        return None


def collect() -> list[ArticleInfo]:
    """
    Collects data from a list of page links.
    Returns:
        collection (list): A list of collected data.
    Raises:
        None.
    """
    logger.info("Starting data collection")
    # Step 1: Retrieve keyword links for each letter in the alphabet
    global client
    client = Client(base_url=base_url, proxy=getenv("HTTPS_PROXY", None))
    start_url = "/service/info/a-z/{letter}/"
    keyword_links: list[tuple[str, str]] = []
    for letter in string.ascii_lowercase:
        letter_links = get_links(start_url.format(letter=letter))
        keyword_links.extend(letter_links)

    # Step 2: Filter the keyword links to only include those that contain the prefix "/service/suche"
    keyword_links = [(link, keyword) for link, keyword in keyword_links if link.startswith("/service/suche")]

    # Step 3: Iterate over the filtered page links
    with logging_redirect_tqdm(loggers=[logger]):
        for link, keyword in tqdm(keyword_links):
            response = client.get(link)

            # Step 4: Handle response based on status code
            if response.status_code == 200:  # List of articles exists
                soup = BeautifulSoup(response.text, "html.parser")
                for tag in soup.findAll("div", {"class": "m-listing__list"}):  # type: ignore
                    for a in tag.findAll("a"):
                        if article_id := get_id(a.get("href")):
                            article_title = a.text
                            add_to_collection(article_id, article_title, keyword)
                        else:
                            continue
            elif response.status_code == 301:  # No article list, redirected to article
                article_id, title = handle_301(response)
                if article_id:
                    add_to_collection(article_id, title, keyword)
                else:
                    continue
            else:
                logging.warning(f"Error retrieving information: Status code {response.status_code} for link {link}")

    # Step 5: Build pydantic models from the collected data
    article_infos: list[ArticleInfo] = []
    for id, data in collection.items():
        data["id"] = id
        article_infos.append(ArticleInfo.model_validate(data))

    # Step 6: Sort the article infos by name
    article_infos = sorted(article_infos, key=lambda article: article.name)

    logger.info(
        f"Data collection completed with {len(article_infos)} articles (originally collected ids: {len(list(collection.keys()))})"
    )
    return article_infos


def main():
    """
    Entry point of the collection script.
    Runs the data collection process and saves the collection artifact.

    Environment variables:
        COLLECTION_FILENAME: Path to save the collection file (default: "artifacts/collection.json").
    """
    logger.info("Collection script started")
    load_dotenv()

    article_infos = collect()
    MIN_ARTICLES = int(getenv("DLF_INDEXER_MIN_ARTICLES", 800))

    if len(article_infos) < MIN_ARTICLES:
        logger.error(
            f"Too few articles collected: Got {len(article_infos)}, expected at least {MIN_ARTICLES}. Script aborting."
        )
        exit(-1)

    COLLECTION_FILENAME = getenv("COLLECTION_FILENAME", "artifacts/collection.json")
    logger.debug(f"Saving collection to {COLLECTION_FILENAME} (can be specified in COLLECTION_FILENAME)")

    with open(COLLECTION_FILENAME, "w", encoding="utf-8") as file:
        file.write(CollectionArtifact(article_infos=article_infos).model_dump_json(indent=2))

    logger.info(f"Collection artifact with {len(article_infos)} articles saved. Script finished.")


if __name__ == "__main__":
    main()
