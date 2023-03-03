"""
Analysis CRUD script
"""
import logging
from typing import Optional

from pydantic import PositiveInt, NonNegativeInt
from sqlalchemy import select, Select, ScalarResult
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.exceptions import DatabaseException
from app.crud.filter import IndexFilter, get_index_filter
from app.crud.specification import IdSpecification
from app.db.session import get_session
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisCreate

logger: logging.Logger = logging.getLogger(__name__)


class AnalysisRepository:
    """
    Analysis repository class
    """

    def __init__(self, session: AsyncSession, index_filter: IndexFilter):
        self.session: AsyncSession = session
        self.index_filter: IndexFilter = index_filter
        self.model: Analysis = Analysis

    async def read_by_id(self, _id: IdSpecification) -> Optional[Analysis]:
        """
        Read the analysis by given id
        :param _id:
        :type _id: IdSpecification
        :return:
        :rtype: Analysis
        """
        try:
            analysis: Analysis = await self.index_filter.filter(
                _id, self.session, self.model)
        except SQLAlchemyError as db_exc:
            raise DatabaseException(
                f'Error at reading analysis with id: {_id.value}.'
                f'\n{str(db_exc)}') from db_exc
        return analysis

    async def read_analyses(
            self, offset: NonNegativeInt, limit: PositiveInt,
    ) -> Optional[list[Analysis]]:
        """
        Read analyses information from table
        :param offset: Offset from where to start returning analyses
        :type offset: NonNegativeInt
        :param limit: Limit the number of results from query
        :type limit: PositiveInt
        :return: Analyses information
        :rtype: list[Analysis]
        """
        stmt: Select = select(self.model).offset(offset).limit(limit)
        try:
            results: ScalarResult = await self.session.scalars(stmt)
            analyses: list[Analysis] = results.all()
        except SQLAlchemyError as sa_exc:
            logger.error(sa_exc)
            raise DatabaseException(
                f'Error at reading analyses.\n{str(sa_exc)}') from sa_exc
        return analyses

    async def create_analysis(
            self, analysis: AnalysisCreate) -> Optional[Analysis]:
        """
        Create analysis into the database
        :param analysis: Request object representing the analysis
        :type analysis: AnalysisCreate or AnalysisSuperCreate
        :return: Response object representing the created analysis in the
         database
        :rtype: Analysis
        """
        analysis_create: Analysis = Analysis(**analysis.dict())
        try:
            self.session.add(analysis_create)
            await self.session.commit()
        except SQLAlchemyError as sa_exc:
            logger.error(sa_exc)
            raise DatabaseException(
                f"Error at creating analysis with {analysis_create.id}"
            ) from sa_exc
        try:
            created_analysis: Analysis = await self.read_by_id(IdSpecification(
                analysis_create.id))
        except SQLAlchemyError as db_exc:
            raise DatabaseException(str(db_exc)) from db_exc
        return created_analysis


async def get_analysis_repository() -> AnalysisRepository:
    """
    Get an instance of the analysis repository with the given session.
    :return: AnalysisRepository instance with session associated
    :rtype: AnalysisRepository
    """
    return AnalysisRepository(await get_session(), await get_index_filter())
