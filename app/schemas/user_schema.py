from pydantic import BaseModel, Field


class ImapSettings(BaseModel):
    server: str
    sent_box: str = Field(..., alias="sentBox")
    port: int
    ssl_only: bool = Field(..., alias="sslOnly")


class SmtpSettings(BaseModel):
    server: str
    port: int
    ssl_only: bool = Field(..., alias="sslOnly")


class UserSettings(BaseModel):
    email: str
    pwd: str
    pwd_length: int = Field(..., alias="pwdLength")
    user_key: str | None = Field(default=None, alias="userKey")
    user: str
    imap: ImapSettings | None = None
    smtp: SmtpSettings
