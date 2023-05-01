"""
A module for tokenization in the app.utils.ml utils.text preprocessing package.
"""
import json
import logging

import aiofiles
import nltk
from fastapi import Depends
from gensim.utils import simple_preprocess

from app.core import config

logger: logging.Logger = logging.getLogger(__name__)


def remove_stopwords_and_tokenize(
        text: str, stop_words: list[str]) -> list[str]:
    """
    Removes stopwords from a string of text and tokenizes it
    :param text: The text to process
    :type text: str
    :param stop_words: A list of stopwords to remove
    :type stop_words: list[str]
    :return: A list of tokens without stopwords
    :rtype: list[str]
    """
    return [w for w in simple_preprocess(text) if
            w not in stop_words and len(w) >= 3]


async def get_stopwords(
        settings: config.Settings = Depends(config.get_settings)
) -> list[str]:
    """
    Get stopwords from file and NLTK
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :return: List of the stopwords
    :rtype: list[str]
    """
    async with aiofiles.open(
            settings.STOP_WORDS_FILE_PATH, encoding=settings.ENCODING) as file:
        content: str = await file.read()
        exclude_words: list[str] = json.loads(content).get("spanish")
    stop_words: list[str] = nltk.corpus.stopwords.words("spanish")
    stop_words.extend(exclude_words)
    return list(set(stop_words))
