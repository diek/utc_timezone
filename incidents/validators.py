import logging

from django.utils import timezone

logger = logging.getLogger(__name__)


def validate_past_datetime(value):
    if timezone.is_naive(value):
        logger.warning(
            "validate_past_datetime received a naive datetime: %r. "
            "This should be fixed at the source.",
            value,
        )
