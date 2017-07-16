#!/usr/bin/env python

import json
import os
import sys
import signal
from lambda_toolkit.modules.utils import  Utils
from lambda_toolkit.modules.lambdacontext import LambdaContext

def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

class Receiver:
    def __init__(self, conf, kwargs):
        self.log = conf.log
        self.conf = conf
        self.sqsname = kwargs['sqsname']
        self.projectname = kwargs['projectname']
        self.sqs = conf.get_boto3("sqs", "resource")

    def collect_receiver(self):

        queue = self.sqs.get_queue_by_name(QueueName=self.sqsname)
        self.log.info("Importing project " + self.projectname)
        pp = os.path.join(Utils.fixpath(self.conf.sett['C_BASE_DIR']),
                          Utils.fixpath(self.conf.sett['C_LAMBDAS_DIR']),
                          self.conf.region, self.projectname)
        self.log.debug("Using project dir: " + pp)
        sys.path.append(pp)
        a = __import__("index")
        func = getattr(a, "lambda_handler")

        self.log.info("Starting the receiver using the queue " + self.sqsname)
        while True:
            try:
                sys.stdout.write(".")
                sys.stdout.flush()
                msg_list = queue.receive_messages(
                    VisibilityTimeout=int(self.conf.sett['QUEUE_GETMESSAGE_VISIBILITY_TIMEOUT']),
                    MaxNumberOfMessages=int(self.conf.sett['QUEUE_GETMESSAGE_MAXNUMBEROFMESSAGES']),
                    WaitTimeSeconds=int(self.conf.sett['QUEUE_GETMESSAGE_WAITTIMESECONDS']))
                for msg in msg_list:
                    jsonmsg = json.loads(msg.body)
                    self.log.info("=======================================")
                    self.log.info("* New message. Sending to " + self.projectname)

                    if func(jsonmsg["event"], LambdaContext(jsonmsg["context"])):
                        try:
                            msg.delete()
                            self.log.info("* Message deleted.")
                        except Exception as e:
                            self.log.warn("* Failed to delete the message. Expired.")
                            self.log.warn("Configured timeout [QUEUE_GETMESSAGE_VISIBILITY_TIMEOUT]: " + str(self.conf.sett[
                                'QUEUE_GETMESSAGE_VISIBILITY_TIMEOUT']))

                    else:
                        self.log.info("* Project " + self.projectname + " returned False. Keeping message in the queue.")

                    self.log.info("=======================================")

            except Exception as a:
                print("OI")
                print(a)
