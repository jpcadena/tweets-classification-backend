"""
Main script
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

from app.api.api_v1.api import api_router
from app.core import logging_config
from app.core.config import settings
from app.core.decorators import with_logging, benchmark
from app.crud.user import get_user_repository
from app.db.authentication import init_auth_db
from app.db.init_db import init_db
from app.schemas.msg import Msg
from app.utils.utils import update_json

logging_config.setup_logging(settings=settings)
logger: logging.Logger = logging.getLogger(__name__)


def custom_generate_unique_id(route: APIRoute) -> str:
    """
    Generate a custom unique ID for each route in API
    :param route: endpoint route
    :type route: APIRoute
    :return: new ID based on tag and route name
    :rtype: str
    """
    if route.name == "welcome_message":
        return ""
    return f"{route.tags[0]}-{route.name}"


app: FastAPI = FastAPI(
    title=settings.PROJECT_NAME, description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}{settings.OPENAPI_FILE_PATH}",
    openapi_tags=settings.TAGS_METADATA, contact=settings.CONTACT,
    license_info=settings.LICENSE_INFO,
    generate_unique_id_function=custom_generate_unique_id)
app.include_router(api_router, prefix=settings.API_V1_STR)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in
                       settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount(
    settings.IMAGES_PATH, StaticFiles(directory=settings.IMAGES_DIRECTORY),
    name="images")


@with_logging
@benchmark
@app.on_event("startup")
async def startup_event() -> None:
    """
    Startup API.
    :return: None
    :rtype: NoneType
    """
    logger.info("Starting API...")
    await update_json(settings)
    await init_db(await get_user_repository(), settings)
    await init_auth_db(settings)


@app.get("/", response_model=Msg)
async def welcome_message() -> Msg:
    """
    Function to retrieve homepage.
    ## Response:
    - `return:` **Welcome message**
    - `rtype:` **Msg**
    """
    logger.info("Salute!")
    return Msg(msg="Hello, world!")
