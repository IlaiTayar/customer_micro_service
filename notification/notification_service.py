import logging

logger = logging.getLogger("customer_service.notification")


def notify_customer(customer_id: int, message: str) -> None:
    logger.info("notification to customer %s: %s", customer_id, message)
