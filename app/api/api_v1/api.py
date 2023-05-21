"""
Centralized API routing script.
This module integrates the individual routers from the different
 modules of the API.
"""
from fastapi import APIRouter

from app.api.api_v1.router import authentication, user, model, analysis

api_router: APIRouter = APIRouter()
api_router.include_router(authentication.router)
api_router.include_router(user.router)
api_router.include_router(model.router)
api_router.include_router(analysis.router)
# api_router.include_router(utils.router)
