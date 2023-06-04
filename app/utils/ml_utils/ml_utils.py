"""
A module for ml utils in the app.utils.ml utils package.
"""
import logging

from fastapi import Depends

from app.core import config
from app.core.decorators import benchmark, with_logging
from app.utils.ml_utils.text_preprocessing.cleaning import (
    remove_emoji,
    remove_punc,
    twitter_text_cleaning,
)
from app.utils.ml_utils.text_preprocessing.tokenization import (
    get_stopwords,
    remove_stopwords_and_tokenize,
)

logger: logging.Logger = logging.getLogger(__name__)


@with_logging
@benchmark
async def preprocess_tweet_text(
        tweet_text: str,
        settings: config.Settings = Depends(config.get_settings)
) -> str:
    """
    Preprocess a tweet text
    :param tweet_text: Raw text to preprocess
    :type tweet_text: str
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :return: Preprocessed tweet text
    :rtype: str
    """
    stop_words: list[str] = await get_stopwords(settings)
    no_emojis: str = remove_emoji(tweet_text)
    cleaned: str = twitter_text_cleaning(no_emojis)
    wo_punctuation: str = remove_punc(cleaned)
    wo_punctuation_and_stopwords: list[str] = remove_stopwords_and_tokenize(
        wo_punctuation, stop_words)
    preprocessed_text: str = " ".join(wo_punctuation_and_stopwords)
    logger.info("Tweet preprocessed: %s", preprocessed_text)
    return preprocessed_text
