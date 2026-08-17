from logging import Logger
from os import getenv
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langfuse import Langfuse
from langfuse.model import TextPromptClient
from logtools import getLogger

logger: Logger = getLogger()


def setup_langfuse(VERSION: str) -> tuple[Langfuse, ChatPromptTemplate, ChatPromptTemplate, float | None]:
    """
    Set up the langfuse context

    Returns:
        tuple[LangfuseDecorator, Langfuse, ChatPromptTemplate, float | None]: The langfuse context, langfuse client, prompt template, and temperature.


    Corresponding Environment Variables:
        LANGFUSE_PUBLIC_KEY: The public key for the langfuse API.
        LANGFUSE_SECRET_KEY: The secret key for the langfuse API.
        LANGFUSE_HOST: The host for the
        LANGFUSE_PROMPT_NAME: the name of the prompt
        LANGFUSE_PROMPT_LABEL: the label of the prompt (production or dev)
    """
    logger.info("Setting up langfuse.")
    LANGFUSE_PUBLIC_KEY = getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY = getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST = getenv("LANGFUSE_HOST")
    LANGFUSE_ANSWER_PROMPT_NAME = getenv("LANGFUSE_ANSWER_PROMPT_NAME")
    LANGFUSE_QUERY_PROMPT_NAME = getenv("LANGFUSE_QUERY_PROMPT_NAME")
    LANGFUSE_PROMPT_LABEL = getenv("LANGFUSE_PROMPT_LABEL", "production")

    # Set up the langfuse client needed for scoring existing traces over the low-level API
    langfuse = Langfuse(public_key=LANGFUSE_PUBLIC_KEY, secret_key=LANGFUSE_SECRET_KEY, host=LANGFUSE_HOST, release=VERSION)
    temperature: float = float(getenv("LLM_TEMPERATURE", 0.0))
    try:
        langfuse.auth_check()
        logger.info("Langfuse auth check successful.")
    except Exception as e:
        logger.error(f"Langfuse auth check failed with the following error {e}. ")

    if LANGFUSE_ANSWER_PROMPT_NAME is None:
        raise ValueError("LANGFUSE_ANSWER_PROMPT_NAME is not set, not able to retrieve prompt.")

    if LANGFUSE_QUERY_PROMPT_NAME is None:
        raise ValueError("LANGFUSE_QUERY_PROMPT_NAME is not set, not able to retrieve prompt.")

    else:
        langfuse_answer_prompt: TextPromptClient = langfuse.get_prompt(name=LANGFUSE_ANSWER_PROMPT_NAME, label=LANGFUSE_PROMPT_LABEL)
        langfuse_query_prompt: TextPromptClient = langfuse.get_prompt(name=LANGFUSE_QUERY_PROMPT_NAME, label=LANGFUSE_PROMPT_LABEL)

        lf_temperature: Any | None = langfuse_answer_prompt.config.get("temperature", None)
        temperature = float(lf_temperature) if lf_temperature is not None else temperature

        answer_prompt_template = ChatPromptTemplate.from_messages(langfuse_answer_prompt.get_langchain_prompt())
        query_prompt_template = ChatPromptTemplate.from_messages(langfuse_query_prompt.get_langchain_prompt())

        answer_prompt_template.metadata = {"langfuse_prompt": langfuse_answer_prompt}
        query_prompt_template.metadata = {"langfuse_prompt": langfuse_query_prompt}

    return langfuse, answer_prompt_template, query_prompt_template, temperature
