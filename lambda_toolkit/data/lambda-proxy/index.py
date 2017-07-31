import boto3
import json
import os


class NormalizeJson(json.JSONEncoder):
    def default(self, obj):
        return obj.__repr__()


def lambda_handler(event, context):

        sqs = boto3.resource('sqs')

        queue = sqs.get_queue_by_name(QueueName=os.environ['sqsname'])
        queue.send_message(MessageDeduplicationId=context.aws_request_id, MessageGroupId="sametoall", MessageBody="{ \"event\": " + json.dumps(event) + ", \"context\": " + json.dumps(vars(context), cls=NormalizeJson) + " }")
