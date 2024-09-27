import smtplib
import imaplib
from typing import Optional
import aiosmtplib
import aioimaplib

from utils.encryption_utils import EncryptionUtils
from schemas.user_schema import UserSettings
from logger_config import logger


class EmailService:
    def __init__(self, user_settings: UserSettings) -> None:
        self.encryption_utils = EncryptionUtils()
        self.user = user_settings.user
        self.pwd = self._get_user_pass(user_settings.user_key, user_settings.pwd)
        self.email = user_settings.email
        self.imap_config = user_settings.imap
        self.smtp_config = user_settings.smtp
        self.smtp_server = (
            smtplib.SMTP_SSL if self.smtp_config.ssl_only else smtplib.SMTP
        )
        self.imap_server = self._set_imap_server()

    def _get_user_pass(self, user_key: Optional[str], user_pwd: str) -> str:
        if user_key is None:
            raise ValueError("User key is None")
        return self.encryption_utils.get_user_pass(user_key, user_pwd)

    def _set_imap_server(self):
        if self.imap_config is None:
            return None
        return imaplib.IMAP4_SSL if self.imap_config.ssl_only else imaplib.IMAP4

    async def validate_smtp_server(self) -> None:
        if self.smtp_config is None:
            raise ValueError("SMTP config is None")
        try:
            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_config.server,
                port=self.smtp_config.port,
                use_tls=self.smtp_config.ssl_only,
            )
            await smtp.connect()
            await smtp.login(self.email, self.pwd)
            await smtp.quit()
        except Exception as e:
            logger.error(f"Error validating SMTP server: {e}")
            raise ValueError("Failed to validate SMTP server") from e

    async def validate_imap_server(self) -> None:
        if self.imap_config is None:
            raise ValueError("IMAP config is None")
        if self.imap_server is None:
            raise ValueError("IMAP server is None")
        try:
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
        except Exception as e:
            logger.error(f"Error validating IMAP server: {e}")
            raise ValueError("Failed to validate IMAP server") from e
