import json
import aio_pika
from app.config import RABBITMQ_URL

class RabbitMQPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(RABBITMQ_URL)
        self.channel = await self.connection.channel()

    async def publish(self, routing_key: str, message: dict):
        if not self.channel:
            await self.connect()
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=routing_key
        )

    async def close(self):
        if self.connection:
            await self.connection.close()

rabbitmq_publisher = RabbitMQPublisher()