#!/usr/bin/env python

import boto3
from utils import Utils
import logger


class Queue:

    def __init__(self, conf, sqsname):
        self.log = logger.get_my_logger("queue")
        self.conf = conf
        if sqsname != "":
            self.sqsname = Utils.append_fifo_in_queue(sqsname)
        else:
            self.log.critical("Parameter --sqsname is required.")

    def create_queue(self):
        sqs = boto3.client('sqs')
        queues = self.list_queues()
        if self.sqsname in queues:
            self.log.critical("The queue '" + self.sqsname + "' already exists.")
        else:
            try:
                sqs.create_queue(QueueName=self.sqsname,
                                 Attributes={'VisibilityTimeout': '3',
                                             'FifoQueue': 'true'})
                queues.append(self.sqsname)
                self.conf.config.set(self.conf.vars['C_CONFIG_SQS'],
                                     self.conf.vars['C_CONFIG_SQS_QUEUES'],
                                     ','.join(filter(None, queues)))

                self.log.info("The queue '" + self.sqsname + "' has been created.")
            except Exception as e:
                self.log.error(str(e))
                self.log.critical("Failed to create the queue '" + self.sqsname + "'.")

        return self.conf

    def purge_queue(self):
        sqs = boto3.client('sqs')
        queues = self.list_queues()
        if self.sqsname in queues:
            try:
                response = sqs.get_queue_url(QueueName=self.sqsname)
                sqs.purge_queue(QueueUrl=response['QueueUrl'])
                self.log.info("The queue '" + self.sqsname + "' has been purged.")
            except Exception as e:
                self.log.error(str(e))
                self.log.critical("Failed to purge the queue '" + self.sqsname + "'.")
        else:
            self.log.critical("The queue '" + self.sqsname + "' does not exist.")

    def delete_queue(self):
        sqs = boto3.client('sqs')
        self.verify_queue_in_use()
        queues = self.list_queues()
        if self.sqsname in queues:
            try:
                response = sqs.get_queue_url(QueueName=self.sqsname)
                sqs.delete_queue(QueueUrl=response['QueueUrl'])
                self.log.info("The queue '" + self.sqsname + "' has been removed.")
            except Exception as e:
                self.log.error(str(e))
                self.log.critical("Failed to remove the queue '" + self.sqsname + "'.")

            queues.remove(self.sqsname)

            self.conf.config.set(self.conf.vars['C_CONFIG_SQS'],
                                 self.conf.vars['C_CONFIG_SQS_QUEUES'],
                                 ','.join(filter(None, queues)))
        else:
            self.log.critical("The queue '" + self.sqsname + "' does not exist.")

        return self.conf

    def list_queues(self):
        return Utils.get_list_config(self.conf,
                                     self.conf.vars['C_CONFIG_SQS'],
                                     self.conf.vars['C_CONFIG_SQS_QUEUES'])

    def verify_queue_in_use(self):
        if self.conf.config.has_section(self.conf.vars['C_CONFIG_LAMBDAPROXY']):
            for proxy in self.conf.config.items(self.conf.vars['C_CONFIG_LAMBDAPROXY']):
                if str(proxy[1]) == self.sqsname:
                    self.log.critical("Impossible to remove '" + self.sqsname + "'."
                                      + " The lambda-proxy '"
                                      + proxy[0] + "' is using it")
