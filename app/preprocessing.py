"""
NLP Model Service to execute the model at the Data Science Project
"""
import json
import logging
import re
import string

import aiofiles
import nltk
from fastapi import Depends
from gensim.utils import simple_preprocess
from pydantic import NonNegativeInt
from sklearn.exceptions import FitFailedWarning, NotFittedError
from sklearn.feature_extraction.text import CountVectorizer

from app.core import config
from app.core.decorators import with_logging, benchmark

logger: logging.Logger = logging.getLogger(__name__)


def remove_emoji(text: str) -> str:
    """
    Remove emojis from a text
    :param text: The text to remove emojis from
    :type text: str
    :return: The input text with emojis removed.
    :rtype: str
    """
    emoji_pattern: re.Pattern[str] = re.compile(
        "[" + "\U0001f600-\U0001f64f"  # emoticons
        + "\U0001f300-\U0001f5ff"  # symbols & pictographs
        + "\U0001f680-\U0001f6ff"  # transport & map symbols
        + "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        + "\U0001f900-\U0001f9ff"  # Unicode 9.0 emojis
        + "\U0001f980-\U0001f9ff"  # Unicode 10.0 emojis
        + "\U0001fa80-\U0001faff"  # Unicode 11.0 emojis
        + "\U0001fbc0-\U0001fbc9"  # Unicode 12.0 emojis
        + "\U0001fcc0-\U0001fcc9"  # Unicode 13.0 emojis
        + "\U0001fcd0-\U0001fcd9"  # Unicode 14.0 emojis
        + "\U0001fdd0-\U0001fdd9"  # Unicode 15.0 emojis
          "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text)


def twitter_text_cleaning(text: str) -> str:
    """
    Clean a text message that might have @mentions, "#" symbol or URLs
    :param text: The text message to clean
    :type text: str
    :return: The cleaned text message without @mentions, "#" and URLs
    :rtype: str
    """
    text = text.lower()
    text = re.sub(r'@[A-Za-z0-9]+', '', text)
    text = re.sub(r'@[A-Za-zA-Z0-9]+', '', text)
    text = re.sub(r'@[A-Za-z0-9_]+', '', text)
    text = re.sub(r'@[A-Za-z]+', '', text)
    text = re.sub(r'@[-)]+', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r'https?\/\/\S+', '', text)
    text = re.sub(r'http?\/\/\S+', '', text)
    text = re.sub(r'https?\/\/.*[\r\n]*', '', text)
    text = re.sub(r'^https?\/\/.*[\r\n]*', '', text)
    text = re.sub(r'^https?:\/\/.*[\r\n]*', '', text)
    return text


def remove_punc(message) -> str:
    """
    Remove punctuation from the given message.
    :param message: Text message that might have punctuations
    :type message: str
    :return: Message without punctuations
    :rtype: str
    """
    return ''.join(
        [char for char in message if char not in string.punctuation])


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
        settings: config.Settings = Depends(config.get_settings)) -> list[str]:
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
    stopwords_file: dict = json.loads(content)
    exclude_words: list[str] = stopwords_file.get('spanish')
    stop_words: list[str] = nltk.corpus.stopwords.words('spanish')
    stop_words.extend(exclude_words)
    stop_words = list(set(stop_words))
    return stop_words


@with_logging
@benchmark
async def preprocess_tweet_text(
        tweet_text: str,
        settings: config.Settings = Depends(config.get_settings)) -> str:
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
        doc_term_matrix = token_counts_matrix.fit_transform(tweet.split('\n'))
        vocabulary: dict = token_counts_matrix.vocabulary_
        ngrams_count = dict(zip(vocabulary.keys(),
                                doc_term_matrix.sum(axis=0).tolist()[0]))
    except (FitFailedWarning, NotFittedError) as exc:
        logger.error(exc)
        raise exc
    logger.info("Vocabulary generated")
    return list(ngrams_count.items())
