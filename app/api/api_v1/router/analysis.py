"""
Analysis router module for API endpoints.
"""
from fastapi import APIRouter, Depends, status, Path, Query
from fastapi.exceptions import HTTPException
from pydantic import PositiveInt, NonNegativeInt

from app.api.deps import get_current_user
from app.core import config
from app.core.security.exceptions import ServiceException
from app.crud.specification import TwitterUsernameSpecification
from app.schemas.analysis import Analysis, AnalysisCreate
from app.schemas.user import UserAuth
from app.services.analysis import AnalysisService, get_analysis_service
from app.services.nlp_model import NLPService, get_nlp_model_service

router: APIRouter = APIRouter(prefix='/analyses', tags=['analyses'])


@router.post('/{tweet_id}', response_model=Analysis,
             status_code=status.HTTP_201_CREATED)
async def create_analysis(
        tweet_id: PositiveInt = Path(
            ..., title='Tweet ID',
            description='Tweet ID to predict sentiment',
            example=1627759518904885248),
        analysis_service: AnalysisService = Depends(get_analysis_service),
        nlp_service: NLPService = Depends(get_nlp_model_service),
        current_user: UserAuth = Depends(get_current_user),
        settings: config.Settings = Depends(config.get_settings)
) -> Analysis:
    """
    Create a new analysis into the system.
    - :param tweet_id: Path Parameter that identifies the tweet to be
     analyzed
    - :type tweet_id: PositiveInt
    - :return: Analysis created with id, tweet_id, analysis_name, accuracy,
     precision, recall, f1_score, roc_auc, computing_time, relationship
      with Analysis: analysis_id and its creation timestamp
    - :rtype: Analysis
    \f
    :param analysis_service: Dependency method for Analysis service object
    :type analysis_service: AnalysisService
    :param nlp_service: Dependency method for NLP model service object
    :type nlp_service: NLPService
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    """
    analysis_performed: dict = {
        'tweet_id': tweet_id,
        'content': 'text for tweet',
        'tweet_username': current_user.username,
        'user_id': current_user.id, 'target': 1}
    # TODO: Use the following commented code for analysis_performed
    # tweet: dict = await nlp_service.nlp_model_repo.get_single_tweet(tweet_id)
    # analysis_obj: dict = await nlp_service.create_analysis_dict(
    #     tweet, settings)
    # target: bool = await nlp_service.classify_tweet(analysis_obj)
    # analysis_performed: dict = {
    #     'tweet_id': analysis_obj.get('tweet_id'),
    #     'content': analysis_obj.get('preprocessed_text'),
    #     'tweet_username': tweet.get('user').get('username'),
    #     'user_id': current_user.id, 'target': target}
    analysis: AnalysisCreate = AnalysisCreate(**analysis_performed)
    try:
        created_analysis: Analysis = await analysis_service.register_analysis(
            analysis)
    except ServiceException as serv_exc:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f'Error at creating analysis.\n{str(serv_exc)}'
        ) from serv_exc
    return created_analysis


@router.post('/batch/{username}', response_model=list[Analysis],
             status_code=status.HTTP_201_CREATED)
async def create_multiple_analysis(
        username: str = Path(
            ..., title='Twitter username',
            description='Username to fetch tweets for analysis', min_length=4,
            max_length=15, example='LassoGuillermo'),
        number_tweets: PositiveInt = Query(
            ..., title='Number of tweets'
            , description='Quantity of recent tweets to analyse for the'
                          ' given user'),
        analysis_service: AnalysisService = Depends(get_analysis_service),
        nlp_service: NLPService = Depends(get_nlp_model_service),
        current_user: UserAuth = Depends(get_current_user),
        settings: config.Settings = Depends(config.get_settings)
) -> list[Analysis]:
    """
    Create multiple analyses into the system.
    - :param username: Path Parameter that identifies username to fetch
     tweets
    - :param number_tweets: Query parameter for the quantity of recent
    tweets to analyse for the given user
    - :type number_tweets: PositiveInt
    - :return: Analysis created with id, tweet_id, analysis_name, accuracy,
     precision, recall, f1_score, roc_auc, computing_time, relationship
      with Analysis: analysis_id and its creation timestamp
    - :rtype: list[Analysis]
    \f
    :param analysis_service: Dependency method for Analysis service object
    :type analysis_service: AnalysisService
    :param nlp_service: Dependency method for NLP model service object
    :type nlp_service: NLPService
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    """
    tweets: list[dict] = await nlp_service.nlp_model_repo.get_tweets(
        TwitterUsernameSpecification(username), number_tweets)
    analyses: list[Analysis] = []
    for tweet in tweets:
        analysis_obj: dict = await nlp_service.create_analysis_dict(
            tweet, settings)
        target: bool = await nlp_service.classify_tweet(analysis_obj)
        analysis_performed: dict = {
            'tweet_id': analysis_obj.get('tweet_id'),
            'content': analysis_obj.get('preprocessed_text'),
            'tweet_username': tweet.get('user').get('username'),
            'user_id': current_user.id, 'target': target}
        analysis: AnalysisCreate = AnalysisCreate(**analysis_performed)
        try:
            created_analysis: Analysis = await analysis_service. \
                register_analysis(analysis)
        except ServiceException as serv_exc:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f'Error at creating analysis.\n{str(serv_exc)}'
            ) from serv_exc
        analyses.append(created_analysis)
    return analyses


@router.get('/{analysis_id}', response_model=Analysis)
async def get_analysis(
        analysis_id: PositiveInt = Path(
            ..., title='AnalysisCreate ID',
            description='ID of the AnalysisCreate to searched', example=1),
        analysis_service: AnalysisService = Depends(get_analysis_service),
        current_user: UserAuth = Depends(get_current_user)
) -> Analysis:
    """
    Search for specific Analysis by ID from the system.
    - :param analysis_id: Path Parameter of Analysis ID to search
    - :type analysis_id: PydanticObjectId
    - :return: Found Analysis from logged-in user with id, tweet_id,
     analysis_name, accuracy, precision, recall, f1_score, roc_auc,
      computing_time, analysis_id and its creation timestamp
    - :rtype: Analysis
    \f
    :param analysis_service: Dependency method for Analysis service object
    :type analysis_service: AnalysisService
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    found_analysis: Analysis = await analysis_service. \
        get_analysis_by_id(analysis_id)
    if not found_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Analysis with ID {analysis_id} not found in the system.')
    return found_analysis


@router.get('', response_model=list[Analysis])
async def get_analyses(
        skip: NonNegativeInt = Query(
            0, title='Skip', description='Skip users', example=0),
        limit: PositiveInt = Query(
            100, title='Limit', description='Limit pagination', example=100),
        analysis_service: AnalysisService = Depends(get_analysis_service),
        current_user: UserAuth = Depends(get_current_user)) -> list[Analysis]:
    """
    Retrieve all analyses from the system.
    - :param skip: Offset from where to start returning analyses
    - :type skip: NonNegativeInt
    - :param limit: Limit the number of results from query
    - :type limit: PositiveInt
    - :return: All analyses from logged-in user with id, tweet_id,
     analysis_name, accuracy, precision, recall, f1_score, roc_auc,
      computing_time, analysis_id and its creation timestamp
    - :rtype: list[Analysis]
    \f
    :param analysis_service: Dependency method for Analysis Service
    :type analysis_service: AnalysisService
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    analyses: list[Analysis] = await analysis_service.get_analyses(skip, limit)
    if not analyses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='This user has no analyses in the system.')
    return analyses
