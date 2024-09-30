from typing import Optional

from user import UserSettings
from firestore import DBService
from logger_config import logger
from emailer.email_service import EmailService

db_service = DBService()


async def set_order_status(
    store_id: str, order_id: str, status: str, status_detail: str
) -> None:
    order_doc = await db_service.get_document(
        f"operational/stores_data/{store_id}/data/auto_ordering/auto_orders/orders/{order_id}"
    )
    await order_doc.reference.update({"status": status, "statusDetail": status_detail})


async def get_user_mailer_settings(
    store_id: str, user_id: str
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


async def get_user_key(user_id: str) -> Optional[str]:
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
