"""
A module for ngram counting in the app.utils.ml utils.ngram counting package.
"""
import logging
from typing import Any

from fastapi import Depends
from pydantic import NonNegativeInt
from sklearn.exceptions import FitFailedWarning, NotFittedError
from sklearn.feature_extraction.text import CountVectorizer

from app.core import config
from app.utils.ml_utils.text_preprocessing.tokenization import get_stopwords

logger: logging.Logger = logging.getLogger(__name__)


async def get_ngram_counts(
        tweet: str, settings: config.Settings = Depends(config.get_settings)
) -> list[tuple[str, NonNegativeInt]]:
    """
    Calculates the count of n-grams in a tweet
    :param tweet: The tweet to process
    :type tweet: str
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :return: A list with the count of each n-gram together as a tuple.
    :rtype: list[tuple[str, NonNegativeInt]]
    """
    stop_words: list[str] = await get_stopwords(settings)
    token_counts_matrix: CountVectorizer = CountVectorizer(
        stop_words=stop_words, ngram_range=(1, 3))
    try:
        doc_term_matrix = token_counts_matrix.fit_transform(tweet.split("\n"))
        vocabulary: dict[str, Any] = token_counts_matrix.vocabulary_
        ngrams_count = dict(zip(vocabulary.keys(),
                                doc_term_matrix.sum(axis=0).tolist()[0]))
    except (FitFailedWarning, NotFittedError) as exc:
        logger.error(exc)
        raise exc
    logger.info("Vocabulary generated")
    return list(ngrams_count.items())
