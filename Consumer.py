import threading

import time

from ProducerConsumerBase import ProducerConsumerBase


class Consumer(ProducerConsumerBase, threading.Thread):
    def __init__(self, channel, id, queueName, rateLimit, txSize, autoAck, multiAckEvery, stats, msgLimit, timeLimit):
        ProducerConsumerBase.__init__(self, rateLimit, 0, 0)
        threading.Thread.__init__(self)
        self.channel = channel
        self.id = id
        self.queueName = queueName
        self.rateLimit = rateLimit
        self.txSize = txSize
        self.autoAck = autoAck
        self.multiAckEvery = multiAckEvery
        self.stats = stats
        self.msgLimit = msgLimit
        self.timeLimit = timeLimit
        self.totalMsgCount = 0
        self.msgCount = 0

    def consumer_callback(self, channel, method, properties, body):
        # print("consumer_callback, receive a message")
        self.totalMsgCount += 1
        self.msgCount += 1

        if self.msgLimit == 0 or self.msgCount <= self.msgLimit:
            msg = body.split(';')
            # print(msg[0])
            # print(body)
            msgTime = float(msg[1])
            nano = time.time()

        if self.autoAck is False:
            if self.multiAckEvery == 0:
                channel.basic_ack(method.delivery_tag)
            elif self.totalMsgCount % self.multiAckEvery == 0:
                channel.basic_ack(method.delivery_tag, True)

        if self.txSize != 0 and self.totalMsgCount % self.txSize == 0:
            channel.tx_commit()

        now = time.time()

        latency = 0L
        if self.id == method.routing_key:
            latency = nano - msgTime

        # print("latency %d" % latency)

        self.stats.handleRecv(latency)
        self.delay(now)

    def kill(self):
        self.channel.stop_consuming()

    def run(self):
        # print("run")

        self.channel.basic_consume(self.consumer_callback, queue=self.queueName, no_ack=True, exclusive=False,
                                   consumer_tag=None, arguments=None)
        self.channel.start_consuming()


