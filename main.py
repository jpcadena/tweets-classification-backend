"""
Main script
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.api_v1.router import authentication, user, model
from app.core.config import settings
from app.db.authorization import init_auth_db
from app.db.init_db import init_db
from app.db.session import get_session

DESCRIPTION: str = """**FastAPI**, **SQLAlchemy** and **Redis** helps you do
 awesome stuff. 🚀\n\n ![Twitter](https://rb.gy/iu4yij)"""
tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users, such as register, get, update "
                       "and delete.",
    },
    {
        "name": "analysis",
        "description": "Manage analyses with creation and get a specific"
                       " analysis on a single or multiple tweets from an"
                       " specific username.",
    },
    {
        "name": "model",
        "description": "Manage Machine Learning model with creation and get"
                       " a specific model performance information.",
    },
    {
        "name": "authentication",
        "description": "The **login** logic is here as well as password "
                       "recovery and reset",
    },
]
app: FastAPI = FastAPI(
    title=settings.PROJECT_NAME,
    description=DESCRIPTION,
    openapi_url=f'{settings.API_V1_STR}/{settings.OPENAPI_FILE_PATH}',
    contact={
        "name": "Juan Pablo Cadena Aguilar",
        "url": "https://www.github.com/jpcadena",
        "email": "jpcadena@espol.edu.ec"},
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"},
)
app.include_router(authentication.router, prefix=settings.API_V1_STR)
app.include_router(user.router, prefix=settings.API_V1_STR)
app.include_router(model.router, prefix=settings.API_V1_STR)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in
                       settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
app.mount('/./app/assets/images', StaticFiles(directory='./app/assets/images'),
          name='images')


@app.on_event('startup')
async def startup_event() -> None:
    """
    Startup API
    :return: None
    :rtype: NoneType
    """
    async_session = await get_session()
    await init_db(async_session)
    await init_auth_db()


@app.get("/")
async def root() -> dict[str, str]:
    """
    Function to retrieve homepage.
    - :return: Welcome message
    - :rtype: dict[str, str]
    """
    # msg: Msg = Msg("Hello, world!")
    return {"msg": "Hello, world!"}
