# """
# Utils API Router
# """
# from typing import Any
# from app.core.celery_app import celery_app
# from fastapi import APIRouter, Depends
# from pydantic.networks import EmailStr
# from app import models, schemas
# from app.api.deps import get_current_user
# from app.utils import send_test_email
#
# router: APIRouter = APIRouter(prefix="/utils", tags=["utils"])
#
#
# @router.post("/test-celery/", response_model=schemas.Msg, status_code=201)
# def test_celery(
#         msg: schemas.Msg,
#         current_user: models.User = Depends(get_current_user),
# ) -> Any:
#     """
#     Test Celery worker
#     - :param msg:
#     - :type msg: schemas.Msg
#     - :return:
#     - :rtype: Any
#     \f
#     :param current_user:
#     :type current_user: models.User
#     """
#     celery_app.send_task("app.worker.test_celery", args=[msg.msg])
#     return {"msg": "Word received"}
#
#
# @router.post("/test-email/", response_model=schemas.Msg, status_code=201)
# def test_email(
#         email_to: EmailStr,
#         current_user: models.User = Depends(get_current_user),
# ) -> Any:
#     """
#     Test emails.
#     :param email_to:
#     :type email_to: EmailStr
#     :return:
#     :rtype: Any
#     \f
#     :param current_user:
#     :type current_user: models.User
#     """
#     send_test_email(email_to=email_to)
#     return {"msg": "Test email sent"}
