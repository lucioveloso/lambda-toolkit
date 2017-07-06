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
        current_time = int(time.time() * 1000) - int(self.conf.vars['C_CONFIG_TAIL_TIME_PREVIOUS_LOG'])

        print ("Collecting logs in real time, starting from "
               + str(int(self.conf.vars['C_CONFIG_TAIL_TIME_PREVIOUS_LOG']) / 1000 / 60)
               + " minutes ago")
        log_group_name = "/aws/lambda/" + self.lambdaname
        while True:
            try:
                paginator = client.get_paginator('describe_log_streams')
                for page in paginator.paginate(logGroupName=log_group_name):
                    for stream in page.get('logStreams', []):
                        response = client.get_log_events(logGroupName=log_group_name,
                                                         logStreamName=stream['logStreamName'],
                                                         startTime=current_time)
                        new_current_time = int(time.time() * 1000)
                        if len(response['events']) > 0:
                            if str(response['events'][len(response['events']) - 1]['message']).startswith('REPORT RequestId:'):
                                for event in response['events']:
                                    print event['message'].rstrip()

                                print("*************")

                                current_time = new_current_time
            except Exception as e:
                self.log.debug(e)
                self.log.critical("Failed to load the logGroupName '" + log_group_name + "'.")

            time.sleep(int(self.conf.vars['C_CONFIG_TAIL_TIME_TO_SLEEP']))
