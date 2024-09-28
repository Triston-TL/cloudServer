import asyncio

from firestore import SubscriptionService
from emailer import setup_email_handlers
from logger_config import logger

async def main():
    logger.info("Starting subscription service...")
    subscription_service = SubscriptionService()
    logger.info("Subscribing to collections...")
    subscription_service.subscribe_to_collection("email")

    logger.info("Setting up email handlers...")
    setup_email_handlers(subscription_service)

    logger.info("App is running. Press Ctrl+C to stop.")
    try:
        stop_event = asyncio.Event()
        while not stop_event.is_set():
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Asyncio task cancelled")
    finally:
        logger.info("Stopping subscription service...")
        subscription_service.unsubscribe()
        logger.info("Subscription service stopped.")


if __name__ == "__main__":
    logger.info("Starting main application...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Stopping application...")
    finally:
        logger.info("Application terminated.")
