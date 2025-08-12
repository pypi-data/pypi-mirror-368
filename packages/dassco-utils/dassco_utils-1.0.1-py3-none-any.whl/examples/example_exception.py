from time import sleep

from dassco_utils.messaging import RabbitMqClient
from dassco_utils.messaging.exceptions import FatalError, TransientError

def fatal_handler(msg, props):
    raise FatalError("This message will be dropped")

def transient_handler(msg, props):
    raise TransientError(max_retries=5)

client = RabbitMqClient()
client.publish('test_queue', { 'name': 'John'})
client.add_handler('test_queue', transient_handler)
client.start_consuming()

