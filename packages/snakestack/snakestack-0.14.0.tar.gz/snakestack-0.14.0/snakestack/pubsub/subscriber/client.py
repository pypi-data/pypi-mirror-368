import asyncio
import logging
from asyncio.events import AbstractEventLoop
from typing import Self, cast

try:
    from google.cloud.pubsub_v1 import SubscriberClient
    from google.cloud.pubsub_v1.subscriber.futures import StreamingPullFuture
    from google.cloud.pubsub_v1.types import FlowControl, SubscriberOptions
except ImportError:
    raise RuntimeError("Pubsub extra is not installed. Run `pip install snakestack[pubsub]`.")

from .batch import BatchesType, BatchingWorker, BatchSettingsModel
from .exceptions import AckableError, RetryableError
from .processors import BatchProcessor, SimpleProcessor
from .types import (
    AsyncQueueMessagePubSub,
    MessagePubSubType,
    QueuesType,
    SchemaType,
)
from .utils import get_message_info, parse_message

logger = logging.getLogger(__name__)

class SnakeStackSubscriber:

    def __init__(
        self: Self,
        client: "SubscriberClient",
        processor: SimpleProcessor | BatchProcessor,
        subscription_path: str,
        flow_control: FlowControl,
        schema: SchemaType | None = None
    ) -> None:
        self.client: "SubscriberClient" = client
        self.subscription_path: str = subscription_path
        self._max_latency_ms: float | None = None
        self._streaming_pull_future: StreamingPullFuture | None = None
        self._schema: SchemaType | None = schema
        self._contexts: list[BatchSettingsModel] = []
        self._queue: AsyncQueueMessagePubSub
        self._batches: BatchesType = {}
        self._queues: QueuesType = {}
        self.processor = processor
        self._flow_control: FlowControl = flow_control
        self._is_batch: bool = hasattr(processor, "process_batch")
        self._stop_event: asyncio.Event = asyncio.Event()
        self._loop: AbstractEventLoop | None = None

    @classmethod
    def from_processor(
        cls: type[Self],
        processor: SimpleProcessor | BatchProcessor,
        project_id: str,
        subscription_name: str,
        *,
        flow_control: FlowControl,
        schema: SchemaType | None = None,
        enable_open_telemetry: bool = False
    ) -> Self:
        subscriber_options = SubscriberOptions(
            enable_open_telemetry_tracing=enable_open_telemetry
        )
        client = SubscriberClient(subscriber_options=subscriber_options)
        subscription_path = client.subscription_path(project_id, subscription_name)
        return cls(
            client=client,
            processor=processor,
            subscription_path=subscription_path,
            schema=schema,
            flow_control=flow_control,
        )

    async def start(
        self: Self,
        max_latency_ms: float | None = None,
        num_workers: int = 2,
        contexts: list[BatchSettingsModel] | None = None
    ) -> None:
        self._max_latency_ms = max_latency_ms
        self._contexts = contexts or []
        self._batches = {}
        self._loop = asyncio.get_running_loop()

        logger.debug(f"Starting consumer with {self.subscription_path}")

        async def _start() -> None:
            logger.debug("Starting streaming pull")
            self._queue = asyncio.Queue(maxsize=self._flow_control.max_messages or 100)

            self._streaming_pull_future = self.client.subscribe(
                subscription=self.subscription_path,
                callback=self._wrapper,
                flow_control=self._flow_control
            )
            logger.debug("Streaming pull started")

            for i in range(num_workers):
                logger.debug(f"Scheduling worker [{i}]")
                asyncio.create_task(self.worker(num=i))

            if hasattr(self.processor, "process_batch") and hasattr(self.processor, "set_queues"):
                for context in self._contexts:
                    batch = BatchingWorker(
                        batch_settings=context,
                        callback=self.processor.process_batch
                    )
                    queue: AsyncQueueMessagePubSub = asyncio.Queue(maxsize=context.size * 2)
                    asyncio.create_task(batch.run(queue=queue))
                    self._batches[context.name] = batch
                    self._queues[context.name] = queue

                self.processor.set_queues(self._queues)

        await _start()
        await self._stop_event.wait()
        await self.stop(streaming_pull_future=self._streaming_pull_future)
        logger.debug("Shutting down...")

    def shutdown(self: Self) -> None:
        logger.debug("Shutdown signal received.")
        self._stop_event.set()

    async def stop(self: Self, streaming_pull_future: StreamingPullFuture) -> None:
        logger.debug(f"Finishing consumer with {self.subscription_path}")
        if streaming_pull_future:
            streaming_pull_future.cancel()

        for batch in self._batches.values():
            await batch._flush()

    def _wrapper(self: Self, message: MessagePubSubType) -> None:
        logger.debug(f"Received raw message {message.message_id}")

        def enqueue() -> None:
            logger.debug(f"Queue size before enqueue: {self._queue.qsize()}")
            try:
                queue = self._queue
                queue.put_nowait(message)
            except asyncio.QueueFull:
                logger.warning(f"Queue is full. Nacking message {message.message_id}")
                message.nack()

        cast(AbstractEventLoop, self._loop).call_soon_threadsafe(enqueue)

    async def worker(self: Self, num: int) -> None:
        logger.debug(f"Starting worker [{num}]")
        while True:
            logger.debug(f"Worker [{num}] waiting messages...")
            queue = self._queue
            message = await queue.get()
            logger.debug(f"Worker [{num}] pulled message {message.message_id}")
            await self.process_message(message)

    async def process_message(self: Self, message: MessagePubSubType) -> None:
        try:
            _, _ = get_message_info(message=message)
            parsed_message = parse_message(message=message, schema=self._schema)
            await self.processor.process(data=parsed_message, message=message)
            if not self._is_batch:
                message.ack()
        except AckableError as error:
            logger.exception("Ackable error - Message will be discarded", exc_info=error)
            message.ack()
        except RetryableError as error:
            logger.exception("Retryable error - Message will be enqueued", exc_info=error)
            message.nack()
        except Exception as error:
            logger.exception("Unexpected error - Message will be discarded", exc_info=error)
            message.ack()
