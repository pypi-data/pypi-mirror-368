import sys

from loguru import logger
from pydantic import HttpUrl
import sentry_sdk

from ._types import Environment


def setup_logger(
    *,
    serialize: bool,
) -> None:
    logger.remove()
    logger.add(sys.stdout, level='INFO', serialize=serialize)


def setup_sentry(
    sentry_dsn: HttpUrl | None,
    environment: Environment,
) -> None:
    if sentry_dsn:
        sentry_sdk.init(
            dsn=str(sentry_dsn),
            environment=environment,
        )
