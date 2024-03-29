"""
Analysis router module for API endpoints.
This module handles the routing for analysis-related API endpoints,
 including creating, reading, and updating analyses.
"""
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, status
from fastapi.exceptions import HTTPException
from pydantic import NonNegativeInt, PositiveInt

from app.api.deps import CurrentUser
from app.core import config
from app.core.security.exceptions import ServiceException
from app.crud.specification import TwitterUsernameSpecification
from app.schemas.analysis import Analysis, AnalysisCreate
from app.services.analysis import ServiceAnalysis
from app.services.nlp_model import ServiceNLP

logger: logging.Logger = logging.getLogger(__name__)
# pylint: disable=unused-argument
router: APIRouter = APIRouter(prefix="/analyses", tags=["analyses"])


@router.post("/{tweet_id}", response_model=Analysis,
             status_code=status.HTTP_201_CREATED)
async def create_analysis(
        analysis_service: ServiceAnalysis,
        nlp_service: ServiceNLP,
        current_user: CurrentUser,
        settings: Annotated[config.Settings, Depends(config.get_settings)],
        tweet_id: PositiveInt = Path(
            ..., title="Tweet ID",
            description="ID of the tweet to be analysed",
            example=1627759518904885248)
) -> Analysis:
    """
    Creates a sentiment analysis for a tweet specified by its ID.
    - `:param tweet_id:` **Path Parameter that identifies the tweet to be
     analyzed**
    - `:type tweet_id:` **PositiveInt**
    - `:return:` **Analysis created with id, tweet_id, analysis_name, accuracy,
     precision, recall, f1_score, roc_auc, computing_time, relationship
      with Analysis: analysis_id and its creation timestamp**
    - `:rtype:` **Analysis**
    \f
    :param analysis_service: Dependency method for Analysis service object
    :type analysis_service: ServiceAnalysis
    :param nlp_service: Dependency method for NLP model service object
    :type nlp_service: ServiceNLP
    :param current_user: Dependency method for authorization by current user
    :type current_user: CurrentUser
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    """
    analysis_performed: dict[str, Any] = {
        "tweet_id": tweet_id,
        "content": "text for tweet",
        "tweet_username": current_user.username,
        "user_id": current_user.id, "target": 1}
    # TODO: Use the following commented code for analysis_performed
    # tweet: dict[str, Any] = await nlp_service.nlp_model_repo.get_single_tweet(
    #     tweet_id)
    # analysis_obj: dict[str, Any] = await nlp_service.create_analysis_dict(
    #     tweet, settings)
    # target: bool = await nlp_service.classify_tweet(analysis_obj)
    # analysis_performed: dict[str, Any] = {
    #     "tweet_id": analysis_obj.get("tweet_id"),
    #     "content": analysis_obj.get("preprocessed_text"),
    #     "tweet_username": tweet.get("user").get("username"),
    #     "user_id": current_user.id, "target": target}
    analysis: AnalysisCreate = AnalysisCreate(**analysis_performed)
    try:
        created_analysis: Analysis = await analysis_service.register_analysis(
            analysis)
    except ServiceException as serv_exc:
        logger.error(serv_exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error at creating analysis.\n{str(serv_exc)}"
        ) from serv_exc
    return created_analysis


@router.post("/batch/{username}", response_model=list[Analysis],
             status_code=status.HTTP_201_CREATED)
async def create_multiple_analysis(
        analysis_service: ServiceAnalysis,
        nlp_service: ServiceNLP,
        current_user: CurrentUser,
        settings: Annotated[config.Settings, Depends(config.get_settings)],
        username: str = Path(
            ..., title="Twitter username",
            description="Username whose tweets are to be analysed",
            min_length=4, max_length=15, example="LassoGuillermo"),
        number_tweets: PositiveInt = Query(
            ..., title="Number of tweets",
            description=
            "Number of recent tweets to be analysed for the user")
) -> list[Analysis]:
    """
    Creates sentiment analyses for multiple tweets of a specified
     Twitter user.
    - `:param username:` **Path Parameter that identifies Twitter
     username whose tweets are to be analysed**
    - `:param number_tweets:` **Query parameter for the quantity of recent
    tweets to analyse for the given user**
    - `:type number_tweets:` **PositiveInt**
    - `:return:` **Analysis created with id, tweet_id, analysis_name, accuracy,
     precision, recall, f1_score, roc_auc, computing_time, relationship
      with Analysis: analysis_id and its creation timestamp**
    - `:rtype:` **list[Analysis]**
    \f
    :param analysis_service: Dependency method for Analysis service object
    :type analysis_service: ServiceAnalysis
    :param nlp_service: Dependency method for NLP model service object
    :type nlp_service: ServiceNLP
    :param current_user: Dependency method for authorization by current user
    :type current_user: CurrentUser
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    """
    # pylint: disable=too-many-arguments
    tweets: list[dict[str, Any]] = await nlp_service.nlp_model_repo.get_tweets(
        TwitterUsernameSpecification(username), number_tweets)
    analyses: list[Analysis] = []
    for tweet in tweets:
        analysis_obj: dict[str, Any] = await nlp_service.create_analysis_dict(
            tweet, settings)
        target: bool = await nlp_service.classify_tweet(analysis_obj)
        analysis_performed: dict[str, Any] = {
            "tweet_id": analysis_obj.get("tweet_id"),
            "content": analysis_obj.get("preprocessed_text"),
            "tweet_username": tweet.get("user").get("username"),
            "user_id": current_user.id, "target": target}
        analysis: AnalysisCreate = AnalysisCreate(**analysis_performed)
        try:
            created_analysis: Analysis = await analysis_service. \
                register_analysis(analysis)
        except ServiceException as serv_exc:
            logger.error(serv_exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error at creating analysis.\n{str(serv_exc)}"
            ) from serv_exc
        analyses.append(created_analysis)
    return analyses


@router.get("/{analysis_id}", response_model=Analysis)
async def get_analysis(
        analysis_service: ServiceAnalysis,
        current_user: CurrentUser,
        analysis_id: PositiveInt = Path(
            ..., title="AnalysisCreate ID",
            description="ID of the Analysis to be retrieved", example=1)
) -> Analysis:
    """
    Retrieves a specific Analysis by its ID.
    - `:param analysis_id:` **Path Parameter of Analysis ID to search**
    - `:type analysis_id:` **PydanticObjectId**
    - `:return:` **Found Analysis from logged-in user with id, tweet_id,
     analysis_name, accuracy, precision, recall, f1_score, roc_auc,
      computing_time, analysis_id and its creation timestamp**
    - `:rtype:` **Analysis**
    \f
    :param analysis_service: Dependency method for Analysis service object
    :type analysis_service: ServiceAnalysis
    :param current_user: Dependency method for authorization by current user
    :type current_user: CurrentUser
    """
    found_analysis: Analysis = await analysis_service. \
        get_analysis_by_id(analysis_id)
    if not found_analysis:
        error_msg = f"Analysis with ID {analysis_id} not found in the system."
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
    return found_analysis


@router.get("", response_model=list[Analysis])
async def get_analyses(
        analysis_service: ServiceAnalysis, current_user: CurrentUser,
        skip: NonNegativeInt = Query(
            default=0, title="Skip", description="Number of analyses to skip",
            example=0),
        limit: PositiveInt = Query(
            default=100, title="Limit",
            description="Maximum number of analyses to return", example=100)
) -> list[Analysis]:
    """
    Retrieves all Analyses, with pagination.
    - `:param skip:` **Number of analyses to skip**
    - `:type skip:` **NonNegativeInt**
    - `:param limit:` **Maximum number of analyses to return**
    - `:type limit:` **PositiveInt**
    - `:return:` **All analyses from logged-in user with id, tweet_id,
     analysis_name, accuracy, precision, recall, f1_score, roc_auc,
      computing_time, analysis_id and its creation timestamp**
    - `:rtype:` **list[Analysis]**
    \f
    :param analysis_service: Dependency method for Analysis Service
    :type analysis_service: ServiceAnalysis
    :param current_user: Dependency method for authorization by current user
    :type current_user: CurrentUser
    """
    analyses: list[Analysis] = await analysis_service.get_analyses(skip, limit)
    if not analyses:
        error_msg = "This user has no analyses in the system."
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
    return analyses
