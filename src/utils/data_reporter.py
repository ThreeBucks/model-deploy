import logging

from kafka import KafkaProducer


KAFKA_BOOTSTRAP_SERVER = [
    '103.134.142.249:9092',
    '45.255.127.196:9092',
    '172.81.122.7:9092',
]

logger = logging.getLogger('kafka')
logger.setLevel(logging.WARNING)


class DataReporter(object):
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVER)

    def report(self, topic, value, sync=False):
        future = self.producer.send(topic, value=value)
        if sync:
            future.get(timeout=10)


data_reporter = DataReporter()


def get_instance():
    return data_reporter
