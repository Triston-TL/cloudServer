from typing import Any
from firestore import SubscriptionService
from pydantic import BaseModel, Field

from logger_config import logger
from firestore import DBService
from .email_service import EmailService
from .email_utils import (
    set_order_status,
    get_user_mailer_settings,
    get_user_key,
    validate_servers,
)


class EmailDoc(BaseModel):
    storeID: str
    orderID: str
    userID: str
    path: str
    test_email: str | None = Field(default=None, alias="testEmail")

def setup_email_handlers(subscription_service: SubscriptionService) -> None:

    @subscription_service.on_create("email")
    async def handle_email_creation(doc: Any) -> None:
        try:
            db_service = DBService()
            email_doc = EmailDoc(**doc.to_dict())
            order_doc = await db_service.get_document(
                f"operational/stores_data/{email_doc.storeID}/{email_doc.path}/{email_doc.orderID}"
            )

            userID = order_doc.get("userID")
            if not userID:
                await set_order_status(
                    email_doc.storeID,
                    email_doc.orderID,
                    status="ERROR",
                    status_detail="User ID not found",
                )
                return

            user_settings = await get_user_mailer_settings(email_doc.storeID, userID)
            if not user_settings:
                await set_order_status(
                    email_doc.storeID,
                    email_doc.orderID,
                    status="ERROR",
                    status_detail="User settings not found",
                )
                return

            user_key = await get_user_key(userID)
            if not user_key:
                await set_order_status(
                    email_doc.storeID,
                    email_doc.orderID,
                    status="ERROR",
                    status_detail="User key not found",
                )
                return
            user_settings.user_key = user_key

            email_service = EmailService(user_settings)
            await validate_servers(
                user_settings, email_service, email_doc.storeID, email_doc.orderID
            )
            if email_doc.test_email:
                await email_service.send_test_email(email_doc.test_email)
        except Exception as e:
            logger.error(f"Error processing email creation: {e}")
