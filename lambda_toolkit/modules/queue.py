#!/usr/bin/env python

from lambda_toolkit.modules.utils import Utils


class Queue:
    def __init__(self, conf, kwargs):
        self.sqs = conf.get_boto3("sqs", "client")
        self.log = conf.log

        if Utils.check_kwargs(kwargs, "region"):
            self.log.info("Updating region to '" + kwargs['region'] + "'.")
            self.conf = conf.set_region(kwargs['region'])
        else:
            self.conf = conf

        if Utils.check_kwargs(kwargs, "sqsname"):
            self.sqsname = kwargs['sqsname']

        self.queues = self.conf.queues.keys()

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

    def delete_all_queue(self):
        for q in list(self.queues):
            self.sqsname = q
            self.delete_queue()

        return self.conf

    def delete_queue(self):
        uses = self._verify_queue_in_use()
        if uses is not None and len(uses) > 0:
            self.log.warn("Impossible to remove '" + self.sqsname + "'."
                          + " The lambda-proxy '"
                          + ', '.join(map(str, uses)) + "' is using it.")
            return self.conf

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
                self.sqsname = q
                uses = self._verify_queue_in_use()
                display_uses = ""
                if uses is not None and len(uses) > 0:
                    display_uses = ', '.join(map(str, uses))

                self.log.info('{0: <{1}}'.format("- Queue name:", 15) +
                              '{0: <{1}}'.format(q, 25) +
                              '{0: <{1}}'.format("Used by:", 10) +
                              display_uses)

        return self.conf

    def _verify_queue_in_use(self):
        used = []
        for q in self.conf.proxies.keys():
            if self.conf.proxies[q]['sqsname'] == self.sqsname:
                used.append(q)

        return used