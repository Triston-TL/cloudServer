from typing import Any
from firestore import SubscriptionService

from logger_config import logger
from .email_handlers import handle_order_email, handle_test_email
from .email_schemas import EmailOrder, EmailTest


def setup_email_handlers(subscription_service: SubscriptionService) -> None:

    @subscription_service.on_create("email")
    async def handle_email_creation(doc: Any) -> None:
        try:
            doc_data = doc.to_dict()

            if doc_data.get("type") == "order":
                user_id = doc_data.get("userID")
                path = doc_data.get("path")
                order_id = doc_data.get("orderID")
                store_id = doc_data.get("storeID")
                email_doc = EmailOrder(
                    user_id=user_id,
                    path=path,
                    order_id=order_id,
                    store_id=store_id,
                )
                await handle_order_email(email_doc)
            elif doc_data.get("type") == "test":
                user_id = doc_data.get("userID")
                store_id = doc_data.get("storeID")
                test_email = doc_data.get("testEmail")
                email_doc = EmailTest(
                    user_id=user_id, store_id=store_id, test_email=test_email
                )
                await handle_test_email(email_doc)
            elif doc_data.get("type") is None:
                logger.warning(f"Email document without type: {doc.id}")
            else:
                logger.error(f"Invalid email type: {doc_data.get('type')}")
        except Exception as e:
            logger.error(f"Error processing email creation: {e}")
