"""
Analysis router module for API endpoints.
"""
from fastapi import APIRouter, Depends, status, Path, Body, Query
from fastapi.exceptions import HTTPException
from pydantic import PositiveInt, NonNegativeInt

from app.api.deps import get_current_user
from app.core.security.exceptions import ServiceException
from app.schemas.analysis import Analysis, AnalysisCreate
from app.schemas.user import UserAuth
from app.services.analysis import AnalysisService, get_analysis_service

router: APIRouter = APIRouter(prefix='/analyses', tags=['analyses'])


@router.post('', response_model=Analysis,
             status_code=status.HTTP_201_CREATED)
async def create_analysis(
        analysis: AnalysisCreate = Body(
            ..., title='New analysis', description='New analysis to create'),
        analysis_service: AnalysisService = Depends(get_analysis_service),
        current_user: UserAuth = Depends(get_current_user)
) -> Analysis:
    """
    Create a new analysis into the system.
    - :param analysis: Body Object with tweet_id, analysis_name, accuracy,
     precision, recall, f1_score, roc_auc, computing_time and
      relationship with Analysis: analysis_id (OPTIONAL)
    - :type analysis: AnalysisCreate
    - :return: Analysis created with id, tweet_id, analysis_name, accuracy,
     precision, recall, f1_score, roc_auc, computing_time, relationship
      with Analysis: analysis_id and its creation timestamp
    - :rtype: Analysis
    \f
    :param analysis_service: Dependency method for Analysis service object
    :type analysis_service: AnalysisService
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    try:
        created_analysis: Analysis = await analysis_service.register_analysis(
            analysis)
    except ServiceException as serv_exc:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f'Error at creating analysis.\n{str(serv_exc)}'
        ) from serv_exc
    return created_analysis


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'AnalysisCreate with ID {analysis_id} '
                                   f'not found in the system.')
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
