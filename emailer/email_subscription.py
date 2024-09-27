from typing import Any, Optional
from firestore import SubscriptionService
from pydantic import BaseModel

from logger_config import logger
from firestore import DBService
from schemas import UserSettings
from .email_service import EmailService


class EmailSubscription(BaseModel):
    storeID: str
    orderID: str
    userID: str
    path: str


async def set_order_status(
    store_id: str, order_id: str, status: str, status_detail: str
) -> None:
    db_service = DBService()
    order_doc = await db_service.get_document(
        f"operational/stores_data/{store_id}/data/auto_ordering/auto_orders/orders/{order_id}"
    )
    await order_doc.reference.update({"status": status, "statusDetail": status_detail})


async def get_user_mailer_settings(
    db_service: DBService, store_id: str, user_id: str
) -> Optional[UserSettings]:
    user_settings_doc = await db_service.get_document(
        f"operational/stores_data/{store_id}/data/auto_ordering/user-settings/settings/{user_id}"
    )
    user_dict = user_settings_doc.to_dict()
    if not user_dict:
        return None
    mailer_settings = user_dict.get("mailer")
    if not mailer_settings:
        return None
    return UserSettings(**mailer_settings)


async def get_user_key(db_service: DBService, user_id: str) -> Optional[str]:
    user_doc = await db_service.get_document(f"user_access/{user_id}/docs/user_key")
    user_dict = user_doc.to_dict()
    if not user_dict:
        return None
    return user_dict.get("key")


async def validate_servers(
    user_settings: UserSettings,
    email_service: EmailService,
    store_id: str,
    order_id: str,
) -> None:
    try:
        await email_service.validate_smtp_server()
        if user_settings.imap:
            await email_service.validate_imap_server()
    except Exception as e:
        logger.error(f"Error validating servers: {e}")
        await set_order_status(
            store_id,
            order_id,
            "ERROR",
            f"Error validating servers: {e}",
        )


def setup_email_handlers(subscription_service: SubscriptionService) -> None:

    @subscription_service.on_create("email")
    async def handle_email_creation(doc: Any) -> None:
        try:
            db_service = DBService()
            email_doc = EmailSubscription(**doc.to_dict())
            order_doc = await db_service.get_document(
                f"operational/stores_data/{email_doc.storeID}/{email_doc.path}/{email_doc.orderID}"
            )

            userID = order_doc.get("userID")
            if not userID:
                await set_order_status(
                    email_doc.storeID, email_doc.orderID, "ERROR", "User ID not found"
                )
                return

            user_settings = await get_user_mailer_settings(
                db_service, email_doc.storeID, userID
            )
            if not user_settings:
                await set_order_status(
                    email_doc.storeID,
                    email_doc.orderID,
                    "ERROR",
                    "User settings not found",
                )
                return

            user_key = await get_user_key(db_service, userID)
            if not user_key:
                await set_order_status(
                    email_doc.storeID,
                    email_doc.orderID,
                    "ERROR",
                    "User key not found",
                )
                return
            user_settings.user_key = user_key
            email_service = EmailService(user_settings)
            await validate_servers(
                user_settings, email_service, email_doc.storeID, email_doc.orderID
            )
        except Exception as e:
            logger.error(f"Error processing email creation: {e}")
