"""
This script contains CRUD operations for the Analysis model.
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
    Repository class for performing CRUD operations on Analysis objects
    """

    def __init__(self, session: AsyncSession, index_filter: IndexFilter):
        self.session: AsyncSession = session
        self.index_filter: IndexFilter = index_filter
        self.model: Analysis = Analysis

    async def read_by_id(self, _id: IdSpecification) -> Optional[Analysis]:
        """
        Fetch an Analysis object by its ID
        :param _id: The ID of the Analysis object to fetch
        :type _id: IdSpecification
        :return: The Analysis object, if found. Otherwise, return None
        :rtype: Optional[Analysis]
        """
        async with self.session as session:
            try:
                analysis: Analysis = await self.index_filter.filter(
                    _id, session, self.model)
            except SQLAlchemyError as db_exc:
                logger.error(db_exc)
                raise DatabaseException(
                    f"Error at reading analysis with id: {_id.value}."
                    f"\n{str(db_exc)}") from db_exc
            return analysis

    async def read_analyses(
            self, offset: NonNegativeInt, limit: PositiveInt,
    ) -> Optional[list[Analysis]]:
        """
        Fetch a list of Analysis objects within a certain range
        :param offset: The starting point from which to fetch the
         Analysis objects
        :type offset: NonNegativeInt
        :param limit: The maximum number of Analysis objects to fetch
        :type limit: PositiveInt
        :return: A list of Analysis objects within the range, if found.
         Otherwise, return None
        :rtype: Optional[list[Analysis]]
        """
        stmt: Select = select(self.model).offset(offset).limit(limit)
        async with self.session as session:
            try:
                results: ScalarResult = await session.scalars(stmt)
                analyses: list[Analysis] = results.all()
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                raise DatabaseException(
                    f"Error at reading analyses.\n{str(sa_exc)}") from sa_exc
            return analyses

    async def create_analysis(
            self, analysis: AnalysisCreate) -> Optional[Analysis]:
        """
        Insert a new Analysis object into the database
        :param analysis: A request object containing the details of the
         Analysis object to be inserted
        :type analysis: AnalysisCreate
        :return: The inserted Analysis object, if successful.
         Otherwise, return None.
         database
        :rtype: Optional[Analysis]
        """
        analysis_create: Analysis = Analysis(**analysis.dict())
        async with self.session as session:
            try:
                session.add(analysis_create)
                await session.commit()
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                raise DatabaseException(
                    f"Error at creating analysis with {analysis_create.id}"
                ) from sa_exc
            try:
                created_analysis: Analysis = await self.read_by_id(
                    IdSpecification(
                        analysis_create.id))
            except SQLAlchemyError as db_exc:
                logger.error(db_exc)
                raise DatabaseException(str(db_exc)) from db_exc
            return created_analysis


async def get_analysis_repository() -> AnalysisRepository:
    """
    Factory function for creating an AnalysisRepository instance with
     an associated session.
    :return: An instance of the AnalysisRepository class with an
     associated session
    :rtype: AnalysisRepository
    """
    return AnalysisRepository(await get_session(), await get_index_filter())
