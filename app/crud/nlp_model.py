"""
This script provides the data access layer to perform CRUD operations
 on the NLP Model entity
"""
import json
import logging
from typing import Any, Callable, Optional

import snscrape.modules.twitter as sn_twitter
from pydantic import PositiveInt

from app.core.decorators import benchmark, with_logging
from app.crud.specification import TwitterBaseSpecification

logger: logging.Logger = logging.getLogger(__name__)


class NLPModelRepository:
    """
    Repository class for NLP Model
    """

    @with_logging
    @benchmark
    async def get_single_tweet(self, tweet_id: PositiveInt) -> dict[str, Any]:
        """
        Retrieve a single tweet by its id
        :param tweet_id: The unique identifier of the tweet
        :type tweet_id: PositiveInt
        :return: A dictionary containing the tweet information
        :rtype: dict[str, Any]
        """
        tweet_scraper: sn_twitter.TwitterTweetScraper = \
            sn_twitter.TwitterTweetScraper(
                tweet_id, mode=sn_twitter.TwitterTweetScraperMode.SINGLE)
        tweet_json_str: str = next(tweet_scraper.get_items()).json()
        logger.info("Scraped tweet with id: %s", tweet_id)
        tweet_dict: dict[str, Any] = json.loads(tweet_json_str)
        return tweet_dict

    @with_logging
    @benchmark
    async def get_tweets(
            self, twitter_specification: TwitterBaseSpecification,
            limit: PositiveInt = 10, func: Optional[Callable[[Any], Any]] = None
    ) -> list[dict[str, Any]]:
        """
        Retrieve a certain number of recent tweets based on a Twitter
         specification
        :param twitter_specification: The specification to use as
         filter
        :type twitter_specification: TwitterBaseSpecification
        :param limit: The number of tweets to search
        :type limit: PositiveInt
        :param func: A function to apply as default for decode json
        :type func: Callable[[Any], Any]
        :return: A list of raw tweets as dictionaries
        :rtype: list[dict[str, Any]]
        """
        return [
            json.loads(json.dumps(tweet.__dict__, default=func)) for idx,
            tweet in enumerate(
                sn_twitter.TwitterSearchScraper(
                    twitter_specification.apply()).get_items()) if idx < limit]


async def get_nlp_model_repository() -> NLPModelRepository:
    """
    Create an instance of the NLP model repository.
    :return: A NLPModelRepository instance
    :rtype: NLPModelRepository
    """
    return NLPModelRepository()
