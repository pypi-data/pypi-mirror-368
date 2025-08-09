import asyncio
import logging
import time
from typing import Awaitable, Callable, Self, TypeAlias

try:
    from google.cloud.pubsub_v1 import SubscriberClient
    from google.cloud.pubsub_v1.subscriber.message import Message
except ImportError:
    raise RuntimeError("Pubsub extra is not installed. Run `pip install snakestack[pubsub]`.")

from snakestack.model import LenientModel
from snakestack.pubsub.subscriber.types import AsyncQueueMessagePubSub, DataPubSubType

logger = logging.getLogger(__name__)


class BatchSettingsModel(LenientModel):
    size: int
    timeout: float
    name: str
    subscriber_client: SubscriberClient | None = None
    subscription_path: str | None = None


class BatchingWorker:
    def __init__(
        self: Self,
        *,
        callback: Callable[[list[tuple[Message, DataPubSubType]], BatchSettingsModel], Awaitable[None]],
        batch_settings: BatchSettingsModel
    ) -> None:
        self.buffer: list[tuple[Message, DataPubSubType]] = []
        self.last_flush = time.monotonic()
        self.callback = callback
        self.batch_settings = batch_settings

    async def run(self: Self, queue: AsyncQueueMessagePubSub) -> None:
        logger.debug(f"Starting batch [{self.batch_settings.name}]")
        while True:
            try:
                timeout = max(self.batch_settings.timeout - (time.monotonic() - self.last_flush), 0.1)
                message, parsed = await asyncio.wait_for(queue.get(), timeout=timeout)
                self.buffer.append((message, parsed))
            except asyncio.TimeoutError:
                pass

            if len(self.buffer) >= self.batch_settings.size or (time.monotonic() - self.last_flush) >= self.batch_settings.timeout:
                await self._flush()

    async def _flush(self: Self) -> None:
        if not self.buffer:
            return

        logger.info(f"[{self.batch_settings.name}] Executing batch with {len(self.buffer)} messages")
        try:
            await self.callback(self.buffer, self.batch_settings)
        except Exception as e:
            logger.exception("Failed to process batch", exc_info=e)
        finally:
            self.buffer.clear()
            self.last_flush = time.monotonic()

BatchesType: TypeAlias = dict[str, BatchingWorker]
