#!/usr/bin/env python

import os
import pkgutil
import sys
import json
import boto3
import logger
import base64
from lambdacontext import LambdaContext


class Invoke:
    def __init__(self, conf, kwargs):
        self.lbs = boto3.client('lambda')
        self.log = logger.get_my_logger(self.__class__.__name__)
        self.conf = conf
        self.kwargs = kwargs

    def local_invoke(self):
        if 'python' not in self.conf.projects[self.kwargs['projectname']]['runtime']:
            self.log.error("Cannot invoke locally a JS runtime project in Python lambda-toolkit environment.")
            self.log.critical("Please find: lambda-toolkit-js project.")
        else:
            self.log.info("Importing project " + self.kwargs['projectname'])
            pp = os.path.join(os.path.expanduser(self.conf.sett['C_BASE_DIR']), self.conf.sett['C_LAMBDAS_DIR'],
                              self.kwargs['projectname'] + "_" + self.conf.region)
            self.log.debug("Using project dir: " + pp)
            sys.path.append(pp)
            a = __import__("index")
            func = getattr(a, "lambda_handler")

            ctx = open(os.path.join(self.conf.invoke_dir_ctx, self.conf.sett['C_INVOKE_CTX_FILE']))
            func(self._get_event(), ctx)

        return self.conf

    def remote_invoke(self):
        if "projectname" in self.kwargs:
            invoke_lambda = self.kwargs['projectname']
            if self.conf.projects[invoke_lambda]['deployed'] == False:
                self.log.critical("Project '" + invoke_lambda + "' is not deployed.")
        else:
            invoke_lambda = self.kwargs['proxyname']

        self.log.info("Invoking the project " + invoke_lambda)
        ret = self.lbs.invoke(
            FunctionName=invoke_lambda,
            LogType='Tail',
            InvocationType='RequestResponse',
            Payload=open(os.path.join(self.conf.invoke_dir_evt, self.kwargs['event_file']))
        )

        print base64.b64decode(ret['LogResult'])

        return self.conf

    def _get_event(self):
        with open(os.path.join(self.conf.invoke_dir_evt, self.kwargs['event_file']), 'r') as f:
            return json.loads(f.read())
