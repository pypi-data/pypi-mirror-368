import json
import pika
import pytest
from unittest.mock import patch, MagicMock
from dassco_utils.messaging import RabbitMqClient

QUEUE_NAME = 'test_queue'

@pytest.fixture
def rabbit_client(monkeypatch):
    connection = MagicMock()
    channel = MagicMock()
    connection.channel.return_value = channel
    connection_factory = MagicMock(return_value=connection)
    monkeypatch.setattr(pika, "BlockingConnection", connection_factory)
    return connection_factory, channel

def test_publish(rabbit_client):
    _, channel = rabbit_client
    client = RabbitMqClient()
    payload = {'id': '1'}
    client.publish(QUEUE_NAME, payload)

    channel.basic_publish.assert_called_once_with(
        exchange='',
        routing_key=QUEUE_NAME,
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
    )

def test_add_handler(rabbit_client):
    _, channel = rabbit_client
    client = RabbitMqClient()
    done = [False, '']

    def dummy_handler(msg, props):
        done[0] = True
        done[1] = msg

    # Test handler registration
    client.add_handler(QUEUE_NAME, dummy_handler)
    channel.queue_declare.assert_called_once_with(queue=QUEUE_NAME, durable=True)
    channel.basic_consume.assert_called_once()

    # Test start consuming
    client.start_consuming()
    channel.start_consuming.assert_called_once()

    # Test handler callback
    callback = channel.basic_consume.call_args[1]['on_message_callback']
    body = json.dumps({'id': '5'}).encode('utf-8')
    callback(channel, MagicMock(), None, body)
    assert done[0] == True
    assert done[1] == {"id": "5"}

@patch('threading.Thread')
def test_async_consumer(mock_thread, rabbit_client):
    _, channel = rabbit_client
    client = RabbitMqClient(run_async=True)
    handler = MagicMock()

    client.add_handler(QUEUE_NAME, handler)
    mock_thread.assert_called_once()
    mock_thread_instance = mock_thread.return_value
    mock_thread_instance.start.assert_called_once()

@patch('threading.Thread')
def test_two_async_consumers(mock_thread, rabbit_client):
    connection_factory, _ = rabbit_client
    client = RabbitMqClient(run_async=True)
    handler = MagicMock()

    client.add_handler(QUEUE_NAME, handler)
    client.add_handler(QUEUE_NAME, handler)
    assert mock_thread.call_count == 2
    assert connection_factory.call_count == 3












