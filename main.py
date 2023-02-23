"""
Main script
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.api_v1.router import authentication, user
from app.core.config import settings
from app.db.authorization import init_auth_db
from app.db.init_db import init_db
from app.db.session import get_session

DESCRIPTION: str = """**FastAPI**, **SQLAlchemy** and **Redis** helps you do
 awesome stuff. 🚀\n\n ![Instagram](https://camo.githubusercontent.com/4ba91c3b883e4636545386ffd115e1f8538becce7d4bc39d9b391505ac10fa0c/68747470733a2f2f7777772e70726f666573696f6e616c7265766965772e636f6d2f77702d636f6e74656e742f75706c6f6164732f323031382f30342f496e7374616772616d2d74616d62692543332541396e2d6162616e646f6e612d6c612d706c617461666f726d612d57696e646f77732d31302d4d6f62696c652e6a7067)"""
tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users, such as register, get, update "
                       "and delete.",
    },
    {
        "name": "posts",
        "description": "Manage post with create, get a specific post, all "
                       "posts and delete.",
    },
    {
        "name": "authentication",
        "description": "The **login** logic is here as well as password "
                       "recovery and reset",
    },
]
app: FastAPI = FastAPI(
    title=settings.PROJECT_NAME,
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
