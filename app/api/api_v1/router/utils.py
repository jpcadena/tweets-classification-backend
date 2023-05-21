"""
Utils API Router
This module handles the routing for utility-related API endpoints,
such as testing email functionality and tasks queueing.
"""
from fastapi import APIRouter, Path, status
from pydantic.networks import EmailStr

from app.api.deps import CurrentUser
# from app.core.celery_app import celery_app
from app.schemas.msg import Msg
from app.utils.email_utils.email_utils import send_test_email

# pylint: disable=unused-argument
router: APIRouter = APIRouter(prefix="/utils", tags=["utils"])


# @router.post("/test-celery/", response_model=Msg,
#              status_code=status.HTTP_201_CREATED)
# def test_celery(msg: Msg, current_user: CurrentUser) -> Msg:
#     """
#     Test Celery worker
#     - :param msg: Message to send
#     - :type msg: Msg
#     - :return: Msg object
#     - :rtype: Msg
#     \f
#     :param current_user: Dependency method for authentication by current user
#     :type current_user: CurrentUser
#     """
#     celery_app.send_task("app.worker.test_celery", args=[msg.msg])
#     return Msg(msg="Word received")


@router.post(
    "/test-email/{email_to}", response_model=Msg,
    status_code=status.HTTP_201_CREATED)
async def test_email(
        current_user: CurrentUser, email_to: EmailStr = Path(
            ..., title="Email to", description="The recipient's email address",
            example=EmailStr("someone@example.com"))
) -> Msg:
    """
    Sends a test email.
    - :param email_to: The recipient's email address
    - :type email_to: EmailStr
    - :return: A message confirming that the email has been sent
    - :rtype: Msg
    \f
    :param current_user: Dependency method for authentication by current user
    :type current_user: CurrentUser
    """
    await send_test_email(email_to)
    return Msg(msg="Test email sent")
