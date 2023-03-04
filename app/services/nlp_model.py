"""
NLP Model Service to execute the model at the Data Science Project
"""
import logging
from datetime import datetime

import joblib
import pandas as pd
from fastapi import Depends
from pydantic import NonNegativeInt

from app.core import config
from app.core.decorators import with_logging, benchmark
from app.crud.nlp_model import get_nlp_model_repository, NLPModelRepository
from app.preprocessing import preprocess_tweet_text, get_ngram_counts

logger: logging.Logger = logging.getLogger(__name__)


class NLPService:
    """
    NLP Model service class.
    """

    def __init__(
            self, nlp_model_repo: NLPModelRepository,
            model_file_path: str = "model.joblib"):
        self.nlp_model_repo: NLPModelRepository = nlp_model_repo
        self.model = self.load_model(model_file_path)
        # model type hint: object from sklearn

    @with_logging
    @benchmark
    def load_model(self, model_file_path: str):
        """
        Load the model
        :param model_file_path: The path to the model file
        :type model_file_path: str
        :return: The loaded model
        :rtype:
        """
        self.model = joblib.load(model_file_path)
        logger.info("Model loaded")
        return self.model

    async def create_analysis_dict(
            self, tweet: dict,
            settings: config.Settings = Depends(config.get_settings)) -> dict:
        """
        Create the analysis dictionary base object
        :param tweet: The Tweet object from Twitter
        :type tweet: dict
        :param settings: Dependency method for cached setting object
        :type settings: config.Settings
        :return: The Analysis base object
        :rtype: dict
        """
        preprocessed_text: str = await preprocess_tweet_text(
            tweet.get('raw_content'), settings)
        vocabulary: list[tuple[str, NonNegativeInt]] = await get_ngram_counts(
            preprocessed_text, settings)
        ngrams: list[str] = []
        counts: list[NonNegativeInt] = []
        for item in vocabulary:
            ngrams.append(item[0])
            counts.append(item[1])
        hour: NonNegativeInt = datetime.strptime(
            tweet.get("date"), "%Y-%m-%d %H:%M:%S").hour
        logger.info("Data for testing, ready")
        return {
            'preprocessed_text': preprocessed_text, 'ngram': ngrams,
            'count': counts, 'hour': hour}

    @with_logging
    @benchmark
    async def classify_tweet(self, data: dict) -> bool:
        """
        Classify tweet as if its content is about national insecurity or not.
        :param data: Analysis object as dictionary
        :type data: dict
        :return: Target classified
        :rtype:bool
        """
        analysis_df: pd.DataFrame = pd.DataFrame.from_dict(data)
        predicted_sentiment: NonNegativeInt = self.model.predict(
            analysis_df)[0]
        logger.info("Sentiment classified: %s", predicted_sentiment)
        return bool(predicted_sentiment)


async def get_nlp_model_service(
        nlp_model_repo: NLPModelRepository = Depends(
            get_nlp_model_repository)
) -> NLPService:
    """
    Get an instance of the NLP model service with the given repository.
    :param nlp_model_repo: Model repository object for SNScraper
    :type nlp_model_repo: NLPModelRepository
    :return: NLP Model Service instance with repository associated
    :rtype: NLPService
    """
    return NLPService(nlp_model_repo)
