"""
NLP Model CRUD script
"""
import json
import logging
from typing import Callable, Any

import snscrape.modules.twitter as sn_twitter
from pydantic import PositiveInt

from app.core import logging_config
from app.core.decorators import with_logging, benchmark
from app.crud.specification import TwitterBaseSpecification

logging_config.setup_logging()
logger: logging.Logger = logging.getLogger(__name__)


class NLPModelRepository:
    """
    NLP Model repository class
    """

    @with_logging
    @benchmark
    async def get_single_tweet(self, tweet_id: PositiveInt) -> dict:
        """
        Retrieve a single tweet by its id
        :param tweet_id: Unique identifier of the tweet
        :type tweet_id: PositiveInt
        :return: Tweet information as a dictionary
        :rtype: dict
        """
        tweet_scraper: sn_twitter.TwitterTweetScraper = \
            sn_twitter.TwitterTweetScraper(
                tweet_id, mode=sn_twitter.TwitterTweetScraperMode.SINGLE)
        tweet_json_str: str = next(tweet_scraper.get_items()).json()
        logger.info("Scraped tweet with id: %s", tweet_id)
        tweet_dict: dict = json.loads(tweet_json_str)
        return tweet_dict

    @with_logging
    @benchmark
    async def get_tweets(
            self, twitter_specification: TwitterBaseSpecification,
            limit: PositiveInt = 10, func: Callable[[Any], Any] = None
    ) -> list[dict]:
        """
        Get certain number of recent tweets from Username based on its
        specification.
        :param twitter_specification: Specification to use as filter
        :type twitter_specification: TwitterBaseSpecification
        :param limit: number of tweets to search
        :type limit: PositiveInt
        :param func: Function to apply as default for decode json
        :type func: Callable[[Any], Any]
        :return: list of raw tweets as dictionaries
        :rtype: list[dict]
        """
        return [
            json.loads(json.dumps(tweet.__dict__, default=func)) for idx,
            tweet in enumerate(
                sn_twitter.TwitterSearchScraper(
                    twitter_specification.apply()).get_items()) if idx < limit]


async def get_nlp_model_repository() -> NLPModelRepository:
    """
    Get an instance of the NLP model repository.
    :return: NLP Model Repository instance
    :rtype: NLPModelRepository
    """
    return NLPModelRepository()
