"""
Utils API Router
"""
from fastapi import APIRouter
from fastapi import status
from pydantic.networks import EmailStr

from app.api.deps import CurrentUser
# from app.core.celery_app import celery_app
from app.schemas.msg import Msg
from app.utils.utils import send_test_email

router: APIRouter = APIRouter(prefix="/utils", tags=["utils"])


# @router.post(
#     "/test-celery/", response_model=Msg, status_code=status.HTTP_201_CREATED)
# def test_celery(
#         msg: Msg,
#         current_user: CurrentUser,
# ) -> Msg:
#     """
#     Test Celery worker
#     - :param msg: Message to send
#     - :type msg: Msg
#     - :return: Msg object
#     - :rtype: Msg
#     \f
#     :param current_user: Dependency method for authorization by current user
#     :type current_user: CurrentUser
#     """
#     celery_app.send_task("app.worker.test_celery", args=[msg.msg])
#     return Msg(msg="Word received")


@router.post(
    "/test-email/", response_model=Msg, status_code=status.HTTP_201_CREATED)
async def test_email(
        email_to: EmailStr,
        current_user: CurrentUser,
) -> Msg:
    """
    Test emails.
    - :param email_to: The email to send
    - :type email_to: EmailStr
    - :return: Msg object
    - :rtype: Msg
    \f
    :param current_user: Dependency method for authorization by current user
    :type current_user: CurrentUser
    """
    await send_test_email(email_to)
    return Msg(msg="Test email sent")
