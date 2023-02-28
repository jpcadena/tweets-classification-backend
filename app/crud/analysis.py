"""
Analysis CRUD script
"""
import logging
from typing import Optional

from fastapi import Depends
from pydantic import PositiveInt, NonNegativeInt
from sqlalchemy import select, Select, ScalarResult
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.filter import IndexFilter, get_index_filter
from app.crud.specification import IdSpecification
from app.db.session import get_session
from app.models import Analysis
from app.schemas.analysis import AnalysisCreate


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

        :param _id:
        :type _id: IdSpecification
        :return:
        :rtype: Analysis
        """
        return await self.index_filter.filter(_id, self.session, self.model)

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
        except NoResultFound as nrf_exc:
            logging.error(nrf_exc)
            raise nrf_exc
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
            logging.error(
                "Database Error for analysis with id: %s.\n%s",
                analysis_create.id, sa_exc)
            raise sa_exc
        created_analysis: Analysis = await self.read_by_id(IdSpecification(
            analysis_create.id))
        return created_analysis


async def get_analysis_repository(
        session: AsyncSession = Depends(get_session)
) -> AnalysisRepository:
    """
    Get an instance of the analysis repository with the given session.
    :param session: Session object for database connectio n
    :type session: AsyncSession
    :return: AnalysisRepository instance with session associated
    :rtype: AnalysisRepository
    """
    return AnalysisRepository(session, await get_index_filter())
