#!/usr/bin/env python

import boto3
import logger


class Queue:

    def __init__(self, conf, kwargs):
        self.sqs = boto3.client('sqs')
        self.log = logger.get_my_logger("queue")
        self.conf = conf
        self.queues = self.conf.queues.keys()
        self.sqsname = kwargs['sqsname']

    def create_queue(self):
        if self.sqsname in self.conf.queues:
            self.log.critical("The queue '" + self.sqsname + "' already exists.")
        else:
            try:
                self.sqs.create_queue(QueueName=self.sqsname,
                                      Attributes={'VisibilityTimeout': '3',
                                                  'FifoQueue': 'true'})

                self.conf.queues[self.sqsname] = {}

                self.log.info("The queue '" + self.sqsname + "' has been created.")
            except Exception as e:
                self.log.error(str(e))
                self.log.critical("Failed to create the queue '" + self.sqsname + "'.")

        return self.conf

    def purge_queue(self):
        if self.sqsname in self.queues:
            try:
                response = self.sqs.get_queue_url(QueueName=self.sqsname)
                self.sqs.purge_queue(QueueUrl=response['QueueUrl'])
                self.log.info("The queue '" + self.sqsname + "' has been purged.")
            except Exception as e:
                self.log.error(str(e))
                self.log.critical("Failed to purge the queue '" + self.sqsname + "'.")
        else:
            self.log.critical("The queue '" + self.sqsname + "' does not exist.")

        return self.conf

    def deleteall_queue(self):
        for q in self.queues:
            self.sqsname = q
            self.delete_queue()

        return self.conf

    def delete_queue(self):
        # TODO: Verifiy if queue is in use
        #if not self._verify_queue_in_use():
        #    return self.conf

        if self.sqsname in self.queues:
            try:
                response = self.sqs.get_queue_url(QueueName=self.sqsname)
                self.sqs.delete_queue(QueueUrl=response['QueueUrl'])
                self.log.info("The queue '" + self.sqsname + "' has been removed.")
            except Exception as e:
                self.log.error(str(e))
                self.log.error("Failed to remove the queue '" + self.sqsname + "' in AWS.")

            self.conf.queues.pop(self.sqsname)
        else:
            self.log.warn("The queue '" + self.sqsname + "' does not exist in lambda-toolkit.")

        return self.conf

    def list_queue(self):
        if len(self.queues) > 0:
            self.log.info("SQS (Queues):")
            for q in self.queues:
                self.log.info("- Queue name: " + q)

        return self.conf

    def _verify_queue_in_use(self):
        # TODO: Verifiy if queue is in use
        if self.conf.config.has_section(self.conf.sett['C_CONFIG_LAMBDAPROXY']):
            for proxy in self.conf.config.items(self.conf.sett['C_CONFIG_LAMBDAPROXY']):
                if str(proxy[1]) == self.sqsname:
                    self.log.warn("Impossible to remove '" + self.sqsname + "'."
                                  + " The lambda-proxy '"
                                  + proxy[0] + "' is using it.")
                    return False

        return True
