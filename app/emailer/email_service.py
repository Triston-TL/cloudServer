import os
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import aiosmtplib
import aioimaplib

from utils.encryption_utils import EncryptionUtils
from user import UserSettings
from logger_config import logger


class EmailService:
    def __init__(self, user_settings: UserSettings) -> None:
        self.encryption_utils = EncryptionUtils()
        self.user = user_settings.user
        self.pwd = self._get_user_pass(user_settings.user_key, user_settings.pwd)
        self.email = user_settings.email
        self.imap_config = user_settings.imap
        self.smtp_config = user_settings.smtp

    def _get_user_pass(self, user_key: Optional[str], user_pwd: str) -> str:
        if user_key is None:
            raise ValueError("User key is None")
        return self.encryption_utils.get_user_pass(user_key, user_pwd)

    async def validate_smtp_server(self) -> None:
        if self.smtp_config is None:
            raise ValueError("SMTP config is None")
        try:
            logger.info(f"Validating SMTP server: {self.smtp_config.server}")
            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_config.server,
                port=self.smtp_config.port,
                use_tls=self.smtp_config.ssl_only,
            )
            await smtp.connect()
            await smtp.login(self.email, self.pwd)
            await smtp.quit()
            logger.info(f"SMTP server {self.smtp_config.server} is valid")
        except Exception as e:
            logger.error(f"Error validating SMTP server: {e}")
            raise ValueError("Failed to validate SMTP server") from e

    async def validate_imap_server(self) -> None:
        if self.imap_config is None:
            raise ValueError("IMAP config is None")
        try:
            logger.info(f"Validating IMAP server: {self.imap_config.server}")
            imap = (
                aioimaplib.IMAP4_SSL(
                    host=self.imap_config.server, port=self.imap_config.port
                )
                if self.imap_config.ssl_only
                else aioimaplib.IMAP4(
                    host=self.imap_config.server, port=self.imap_config.port
                )
            )
            await imap.wait_hello_from_server()
            await imap.login(self.email, self.pwd)
            await imap.logout()
            logger.info(f"IMAP server {self.imap_config.server} is valid")
        except Exception as e:
            logger.error(f"Error validating IMAP server: {e}")
            raise ValueError("Failed to validate IMAP server") from e

    async def send_test_email_with_pdf(self, recipient: str, pdf_path: str) -> None:
        try:
            logger.info(f"Sending test email with PDF attachment to {recipient}")
            message = MIMEMultipart()
            message["From"] = self.email
            message["To"] = recipient
            message["Subject"] = "Test Email with PDF Attachment"

            text = MIMEText(
                "This is a test email with a PDF attachment.", "plain", "utf-8"
            )
            message.attach(text)

            with open(pdf_path, "rb") as pdf_file:
                pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
                pdf_attachment.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{pdf_path.split("/")[-1]}"',
                )
                message.attach(pdf_attachment)

            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_config.server,
                port=self.smtp_config.port,
                use_tls=self.smtp_config.ssl_only,
            )
            await smtp.connect()
            await smtp.login(self.email, self.pwd)
            await smtp.send_message(message)
            await smtp.quit()

            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            logger.info(f"Test email with PDF attachment sent to {recipient}")
        except Exception as e:
            logger.error(f"Error sending test email with PDF attachment: {e}")
            raise ValueError("Failed to send test email with PDF attachment") from e
