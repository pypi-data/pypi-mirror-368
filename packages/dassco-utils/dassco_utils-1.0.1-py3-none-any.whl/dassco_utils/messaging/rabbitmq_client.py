import threading
import pika
import json
import signal
import logging

from dassco_utils.messaging.exceptions import TransientError, FatalError
from typing import Callable, Optional, Dict

class RabbitMqClient:

    def __init__(
        self,
        host_name: str = 'localhost',
        run_async: bool = False,
        credentials: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize a RabbitMQ client
        :param host_name: RabbitMQ host (default: 'localhost')
        :param run_async: If True, messages handlers run in separate threads.
        :param credentials: Optional dict with 'username' and 'password'
        """
        self.host_name = host_name
        self.run_async = run_async
        self.credentials = credentials
        self._connection = self._create_connection()
        self._producer_channel = None
        self._consumer_channel = None
        self._exit_event = threading.Event()

    def _create_connection(self):
        """
        Open a blocking connection to the RabbitMQ server.
        """
        params_kwargs = {"host": self.host_name}
        credentials = self._get_credentials()

        if credentials is not None:
            username, password = credentials
            params_kwargs["credentials"] = pika.PlainCredentials(username, password)

        connection = pika.BlockingConnection(pika.ConnectionParameters(**params_kwargs))
        return connection

    def add_handler(self, queue: str, handler: Callable):
        """
        Register a message handler for the given queue.

        Uses a threaded consumer if `run_async=True, otherwise runs synchronously.

        :param queue: The name of the queue to consume messages from.
        :param handler: The callback function to be executed whenever a message is consumed from the queue.
        :return: None
        """
        if self.run_async:
            self._add_handler_async(queue, handler)
        else:
            self._add_handler_sync(queue, handler)

    def _add_handler_sync(self, queue: str, handler: Callable):
        """
        Create a blocking consumer for the given queue and handler.
        """
        if self._consumer_channel is None:
            self._consumer_channel = self._connection.channel()
        self._prepare_consumer(self._consumer_channel, queue, handler)

    def _add_handler_async(self, queue: str, handler: Callable):
        """
        Create an asynchronous consumer for the given queue and handler.
        """
        connection = self._create_connection()
        channel = connection.channel()
        thread = threading.Thread(
            target = self._consumer_thread,
            args = (channel, queue, handler),
            daemon = True
        )
        thread.start()

    def _consumer_thread(self, channel, queue, handler):
        """
        Used by an asynchronous handler to prepare a threaded consumer.
        """
        self._prepare_consumer(channel, queue, handler)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.close()

    def _prepare_consumer(self, channel, queue, handler):
        """
        Prepare a consumer for the queue on the given channel.

        Behavior:
            - Declares the queue as durable.
            - Invokes the given handler function when a message is consumed.
            - On TransientError: retries until `max_retries` is reached.
            - On FatalError or unexpected exceptions: drop the message.
            - Acknowledges successful messages; negatively acknowledges failed ones.
        """
        channel.queue_declare(queue=queue, durable=True)

        def callback(ch, method, properties, body):
            try:
                message = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                message = body.decode('utf-8')
            headers = getattr(properties, "headers", None) or {}
            retries = headers.get('x-retries', 0)
            try:
                handler(message, properties)
            except TransientError as e:
                max_retries = e.max_retries
                if retries < max_retries:
                    logging.error(f"TransientError, retry message {message} {retries + 1}/{max_retries}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    new_headers = {**headers, 'x-retries': retries + 1}

                    properties = pika.BasicProperties(
                        delivery_mode=pika.DeliveryMode.Persistent,
                        headers=new_headers
                    )
                    self.publish(queue, message, properties)
                else:
                    logging.error(f"Retry limit {max_retries} reached, dropping message {message!r}.")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except FatalError as e:
                logging.error(f"FatalError, dropping message: {str(e)}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except Exception as e:
                logging.error(f"Unexpected error, dropping message: {str(e)}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            else:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue=queue, on_message_callback=callback)

    def publish(self, queue: str, payload: any, properties: Optional[pika.BasicProperties] = None):
        """
        Publish a message to the given queue.
        :param queue: name of the queue.
        :param payload: message payload.
        :param properties: messages properties
        :return: None
        """
        if self._producer_channel is None:
            self._producer_channel = self._connection.channel()

        if properties is None:
            properties = pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)

        self._producer_channel.basic_publish(
            exchange = '',
            routing_key = queue,
            body= json.dumps(payload),
            properties=properties
        )

    def _get_credentials(self):
        """
        Extracts the credentials from the provided credentials dictionary.
        :return: A tuple (username, password) if credentials exist; otherwise None.
        """
        if self.credentials is not None:
            try:
                username = self.credentials['username']
                password = self.credentials['password']
            except KeyError:
                raise ValueError("Credentials must contain 'username' and 'password'")
            return username, password
        return None

    def _signal_handler(self, _signum, _frame):
        """
        Handles termination signals and triggers graceful shutdown.
        """
        self._exit_event.set()

    def start_consuming(self):
        """
        Start the message consumption process.

        In asynchronous mode, signal handlers are registered for graceful shutdown.
        :return: None
        """
        if self.run_async:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            self._exit_event.wait()
        else:
            try:
                self._consumer_channel.start_consuming()
            except KeyboardInterrupt:
                if self._consumer_channel is not None:
                    self._consumer_channel.close()
                if self._producer_channel is not None:
                    self._producer_channel.close()
                self._connection.close()