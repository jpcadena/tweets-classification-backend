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
from app.db.authorization import init_auth_db
from app.db.init_db import init_db
from app.schemas.msg import Msg
from app.utils import update_json

logging_config.setup_logging()
logger: logging.Logger = logging.getLogger(__name__)
DESCRIPTION: str = """**FastAPI**, **SQLAlchemy** and **Redis** helps you do
 awesome stuff. 🚀\n\n ![Twitter](https://rb.gy/iu4yij)"""
contact: dict[str, str] = {
    "name": "Juan Pablo Cadena Aguilar",
    "url": "https://www.github.com/jpcadena",
    "email": "jpcadena@espol.edu.ec"}
license_info: dict[str, str] = {
    "name": "Apache 2.0",
    "url": "https://www.apache.org/licenses/LICENSE-2.0.html"}
tags_metadata: list[dict[str, str]] = [
    {
        "name": "users",
        "description": "Operations with users, such as register, get, update "
                       "and delete."
    },
    {
        "name": "analyses",
        "description": "Manage analyses with creation and get a specific"
                       " analysis on a single or multiple tweets from an"
                       " specific username."
    },
    {
        "name": "models",
        "description": "Manage Machine Learning model with creation and get"
                       " a specific model performance information."
    },
    {
        "name": "auth",
        "description": "The authentication logic is here as well as password "
                       "recovery and reset."}]


def custom_generate_unique_id(route: APIRoute) -> str:
    """
    Generate a custom unique ID for each route in API
    :param route: endpoint route
    :type route: APIRoute
    :return: new ID based on tag and route name
    :rtype: string
    """
    if route.name == 'root':
        return ''
    return f"{route.tags[0]}-{route.name}"


app: FastAPI = FastAPI(
    title=settings.PROJECT_NAME, description=DESCRIPTION, version="1.0",
    openapi_url=f'{settings.API_V1_STR}{settings.OPENAPI_FILE_PATH}',
    openapi_tags=tags_metadata, contact=contact, license_info=license_info,
    generate_unique_id_function=custom_generate_unique_id)
app.include_router(api_router, prefix=settings.API_V1_STR)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in
                       settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount('/./app/assets/images', StaticFiles(directory='./app/assets/images'),
          name='images')


@with_logging
@benchmark
@app.on_event('startup')
async def startup_event() -> None:
    """
    Startup API
    :return: None
    :rtype: NoneType
    """
    logger.info('Starting API...')
    await update_json()
    await init_db(await get_user_repository())
    await init_auth_db()


@app.get("/", response_model=Msg)
async def root() -> Msg:
    """
    Function to retrieve homepage.
    - :return: Welcome message
    - :rtype: Msg
    """
    logger.info("Salute!")
    return Msg(msg="Hello, world!")
