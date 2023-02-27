"""
Main script
"""
from sqlalchemy.ext.asyncio import AsyncSession


class ModelService:
    """
    Model service class.
    """

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    # async def get_model_by_id(self, model_id: int) -> ModelResponse:
    #     """
    #     Get model information with the correct schema for response
    #     :param model_id: Unique identifier of the model
    #     :type model_id: int
    #     :return: Model information
    #     :rtype: ModelResponse
    #     """
    #     model: Model = await read_model_by_id(model_id, self.session)
    #     return await model_to_response(model, ModelResponse)
