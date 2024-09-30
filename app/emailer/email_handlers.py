from firestore import DBService

from logger_config import logger
from pdf.pdf_service import PDFService
from .email_schemas import EmailOrder, EmailTest
from .email_service import EmailService
from .email_utils import (
    set_order_status,
    get_user_mailer_settings,
    get_user_key,
    validate_servers,
)

db_service = DBService()


async def handle_test_email(email_doc: EmailTest):
    user_settings = await get_user_mailer_settings(
        email_doc.store_id, email_doc.user_id
    )
    if not user_settings:
        logger.error(f"User settings not found for user {email_doc.user_id} in store {email_doc.store_id}")
        return
        # TODO: Set message in firestore about error

    user_key = await get_user_key(email_doc.user_id)
    if not user_key:
        logger.error(f"User key not found for user {email_doc.user_id}")
        return
        # TODO: Set message in firestore about error

    user_settings.user_key = user_key

    email_service = EmailService(user_settings)
    pdf_service = PDFService()
    data = {"title": "Sample PDF", "description": "This is a sample PDF document."}
    pdf_path = pdf_service.generate_pdf(data)
    if not pdf_path:
        logger.error(f"Failed to generate PDF for user {email_doc.user_id}")
        return
        # TODO: Set message in firestore about error

    await email_service.send_test_email_with_pdf(email_doc.test_email, pdf_path)


async def handle_order_email(email_doc: EmailOrder):
    order_doc = await db_service.get_document(
        f"operational/stores_data/{email_doc.store_id}/{email_doc.path}/{email_doc.order_id}"
    )
    # TODO: Use order_doc data to send email

    user_settings = await get_user_mailer_settings(
        email_doc.store_id, email_doc.user_id
    )
    if not user_settings:
        await set_order_status(
            email_doc.store_id,
            email_doc.order_id,
            status="ERROR",
            status_detail="User settings not found",
        )
        return

    user_key = await get_user_key(email_doc.user_id)
    if not user_key:
        await set_order_status(
            email_doc.store_id,
            email_doc.order_id,
            status="ERROR",
            status_detail="User key not found",
        )
        return

    user_settings.user_key = user_key

    email_service = EmailService(user_settings)
    await validate_servers(
        user_settings, email_service, email_doc.store_id, email_doc.order_id
    )