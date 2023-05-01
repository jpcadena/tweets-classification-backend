"""
Analysis Service to handle business logic
"""
from typing import Optional, Annotated, Type

from fastapi import Depends
from pydantic import PositiveInt, NonNegativeInt

from app.core.security.exceptions import DatabaseException, ServiceException
from app.crud.analysis import AnalysisRepository, get_analysis_repository
from app.crud.specification import IdSpecification
from app.models.analysis import Analysis as AnalysisDB
from app.schemas.analysis import AnalysisCreate, Analysis
from app.services import model_to_response


class AnalysisService:
    """
    Analysis service class.
    """

    def __init__(self, analysis_repo: AnalysisRepository):
        self.analysis_repo: AnalysisRepository = analysis_repo

    async def get_analysis_by_id(self, analysis_id: PositiveInt) -> Analysis:
        """
        Get analysis information with the correct schema for response
        :param analysis_id: Unique identifier of the analysis
        :type analysis_id: PositiveInt
        :return: Analysis information
        :rtype: Analysis
        """
        try:
            analysis: AnalysisDB = await self.analysis_repo.read_by_id(
                IdSpecification(analysis_id))
        except DatabaseException as db_exc:
            raise ServiceException(str(db_exc)) from db_exc
        return await model_to_response(analysis, Analysis)

    async def register_analysis(self, analysis: AnalysisCreate) -> Analysis:
        """
        Create analysis into the database
        :param analysis: Request object representing the analysis
        :type analysis: AnalysisCreate or AnalysisSuperCreate
        :return: Response object representing the created analysis in the
         database
        :rtype: AnalysisCreateResponse or exception
        """
        try:
            created_analysis: AnalysisDB = await self.analysis_repo. \
                create_analysis(analysis)
        except DatabaseException as db_exc:
            raise ServiceException(str(db_exc)) from db_exc
        return await model_to_response(created_analysis, Analysis)

    async def get_analyses(
            self, offset: NonNegativeInt, limit: PositiveInt
    ) -> Optional[list[Analysis]]:
        """
        Read analyses information from table
        :param offset: Offset from where to start returning analyses
        :type offset: NonNegativeInt
        :param limit: Limit the number of results from query
        :type limit: PositiveInt
        :return: Analysis information
        :rtype: AnalysisResponse
        """
        try:
            analyses: list[
                AnalysisDB] = await self.analysis_repo.read_analyses(
                offset, limit)
        except DatabaseException as db_exc:
            raise ServiceException(str(db_exc)) from db_exc
        found_analyses: list[Analysis] = [
            await model_to_response(analysis, Analysis)
            for analysis in analyses]
        return found_analyses


async def get_analysis_service(
        analysis_repo: AnalysisRepository = Depends(
            get_analysis_repository)
) -> AnalysisService:
    """
    Get an instance of the analysis service with the given repository.
    :param analysis_repo: Analysis repository object for database connection
    :type analysis_repo: AnalysisRepository
    :return: AnalysisService instance with repository associated
    :rtype: AnalysisService
    """
    return AnalysisService(analysis_repo)


ServiceAnalysis: Type[AnalysisService] = Annotated[
    AnalysisService, Depends(get_analysis_service)]
