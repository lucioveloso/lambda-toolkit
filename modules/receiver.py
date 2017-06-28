import boto3
import json
import sys
from collections import namedtuple
from utils import Utils


class Receiver:

    def __init__(self, conf, sqsname, projectname):
        self.conf = conf
        if sqsname != "" and projectname != "":
            self.sqsname = sqsname
            self.projectname = projectname
        else:
            print("Parameter --sqsname and --projectname are required.")
            exit(1)

    def receiver(self):
        if self.sqsname not in Utils.get_list_config(self.conf, self.conf.vars['C_CONFIG_SQS'], self.conf.vars['C_CONFIG_SQS_QUEUES']):
            print("The queue " + self.sqsname + " does not exist.")
            exit(1)
        if not self.conf.config.has_section(self.projectname):
            print("Project" + self.projectname + " does not exist.")
            exit(1)

        sqs = boto3.resource('sqs')
        queue = sqs.get_queue_by_name(QueueName=self.sqsname)
        print("Importing project " + self.projectname)
        lambdas = __import__("lambdas." + self.projectname + ".index")
        print("Starting the receiver using the queue " + self.sqsname)
        while True:
            sys.stdout.write(".")
            sys.stdout.flush()
            msg_list = queue.receive_messages(
                VisibilityTimeout=int(self.conf.vars['QUEUE_GETMESSAGE_VISIBILITY_TIMEOUT']),
                MaxNumberOfMessages=int(self.conf.vars['QUEUE_GETMESSAGE_MAXNUMBEROFMESSAGES']),
                WaitTimeSeconds=int(self.conf.vars['QUEUE_GETMESSAGE_WAITTIMESECONDS']))
            for msg in msg_list:
                jsonmsg = json.loads(msg.body)
                print("=======================================")
                print("* New message. Sending to " + self.projectname)

                func = getattr(getattr(getattr(lambdas, self.projectname), "index"), "lambda_handler")

                if func(jsonmsg["event"], json.loads(json.dumps(jsonmsg["context"]),
                                                     object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))):
                    msg.delete()
                    print("* Message deleted.")
                else:
                    print("* Project " + self.projectname + " returned False. Keeping message in the queue.")

                print("=======================================")