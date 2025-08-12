from time import sleep

from dassco_utils.messaging import RabbitMqClient

def handler_one(msg, props):
    print('Handler One Running')
    sleep(5)
    print('Handler One Completed')

def handler_two(msg, props):
    print('Handler Two Running')
    sleep(2)
    print('Handler Two Completed')

client = RabbitMqClient(run_async=True)

client.publish('test_queue', 'Hello World')
client.publish('test_queue2', 'Hello World')

client.add_handler('test_queue', handler_one)
client.add_handler('test_queue2', handler_two)
client.start_consuming()
