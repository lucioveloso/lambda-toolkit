#!/usr/bin/env python
import boto3
import time
import logger


class Tail:

    def __init__(self, conf, lambdaname):
        self.log = logger.get_my_logger("tail")
        self.conf = conf
        if lambdaname != "":
            self.lambdaname = lambdaname
        else:
            self.log.critical("Parameter --lambdaname are required.")

    def tail_log(self):
        client = boto3.client('logs')
        current_time = int(time.time() * 1000) - 300000

        print ("Collecting logs in real time, starting from " + str(300000 / 1000 / 60) + " minutes ago")
        while True:
            paginator = client.get_paginator('describe_log_streams')
            for page in paginator.paginate(logGroupName='/aws/lambda/' + self.lambdaname):
                for stream in page.get('logStreams', []):
                    response = client.get_log_events(logGroupName='/aws/lambda/' + self.lambdaname,
                                                     logStreamName=stream['logStreamName'],
                                                     startTime=current_time)
                    new_current_time = int(time.time() * 1000)
                    if len(response['events']) > 0:
                        if str(response['events'][len(response['events']) - 1]['message']).startswith('REPORT RequestId:'):
                            for event in response['events']:
                                print event['message'].rstrip()

                            print("*************")



                            current_time = new_current_time
            time.sleep(5)
