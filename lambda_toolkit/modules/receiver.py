#!/usr/bin/env python

import boto3
import json
import sys
from collections import namedtuple
from utils import Utils
import logger
import os

class Receiver:

    def __init__(self, conf, sqsname, projectname):
        self.log = logger.get_my_logger("receiver")
        self.conf = conf
        if sqsname != "" and projectname != "":
            self.sqsname = sqsname
            self.projectname = projectname
        else:
            self.log.critical("Parameter --sqsname and --projectname are required.")

    def receiver(self):
        if self.sqsname not in Utils.get_list_config(self.conf, self.conf.vars['C_CONFIG_SQS'], self.conf.vars['C_CONFIG_SQS_QUEUES']):
            self.log.critical("The queue " + self.sqsname + " does not exist.")
        if not self.conf.config.has_section(self.projectname):
            self.log.critical("Project" + self.projectname + " does not exist.")

        sqs = boto3.resource('sqs')
        queue = sqs.get_queue_by_name(QueueName=self.sqsname)
        self.log.info("Importing project " + self.projectname)
        pp = os.path.join(os.path.expanduser(self.conf.vars['C_BASE_DIR']), "lambdas")
        sys.path.append(pp)
        lambdas = __import__(self.projectname + ".index")

        self.log.info("Starting the receiver using the queue " + self.sqsname)
        while True:
            sys.stdout.write(".")
            sys.stdout.flush()
            msg_list = queue.receive_messages(
                VisibilityTimeout=int(self.conf.vars['QUEUE_GETMESSAGE_VISIBILITY_TIMEOUT']),
                MaxNumberOfMessages=int(self.conf.vars['QUEUE_GETMESSAGE_MAXNUMBEROFMESSAGES']),
                WaitTimeSeconds=int(self.conf.vars['QUEUE_GETMESSAGE_WAITTIMESECONDS']))
            for msg in msg_list:
                jsonmsg = json.loads(msg.body)
                self.log.info("=======================================")
                self.log.info("* New message. Sending to " + self.projectname)
                func = getattr(getattr(lambdas, "index"), "lambda_handler")
                #func = getattr(getattr(getattr(lambdas, self.projectname), "index"), "lambda_handler")

                if func(jsonmsg["event"], json.loads(json.dumps(jsonmsg["context"]),
                                                     object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))):
                    msg.delete()
                    self.log.info("* Message deleted.")
                else:
                    self.log.info("* Project " + self.projectname + " returned False. Keeping message in the queue.")

                self.log.info("=======================================")
