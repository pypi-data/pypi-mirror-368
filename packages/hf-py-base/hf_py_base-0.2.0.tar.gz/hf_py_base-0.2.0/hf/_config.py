from pydantic import HttpUrl
from pydantic_settings import BaseSettings

from ._types import Environment


class CommonSettings(BaseSettings):
    environment: Environment = Environment.LOCAL
    sentry_dsn: HttpUrl | None = None
