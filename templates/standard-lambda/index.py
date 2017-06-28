import boto3
import json


def lambda_handler(event, context):
    print("Hi, I'm here. Lambda-proxy is working. =)")
    print("AWS Event ID: " + context.aws_request_id)
    print("Event Body: " + json.dumps(event))
    # print("Event Body: " + event["key1"])

    return True  # Remove message from SQS
