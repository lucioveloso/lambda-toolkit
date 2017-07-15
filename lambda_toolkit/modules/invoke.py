#!/usr/bin/env python

import os
import sys
import json
import base64
from lambda_toolkit.modules.lambdacontext import LambdaContext

class Invoke:
    def __init__(self, conf, kwargs):
        self.lbs = conf.get_boto3("lambda", "client")
        self.log = conf.log
        self.conf = conf
        self.kwargs = kwargs

    def local_invoke(self):
        if 'python' not in self.conf.projects[self.kwargs['projectname']]['runtime']:
            self.log.error("Cannot invoke locally a JS runtime project in Python lambda-toolkit environment.")
            self.log.critical("Please find: lambda-toolkit-js project.")
        else:
            self.log.info("Importing project " + self.kwargs['projectname'])
            pp = os.path.join(os.path.expanduser(self.conf.sett['C_BASE_DIR']),
                              self.conf.sett['C_LAMBDAS_DIR'],
                              self.conf.region,
                              self.kwargs['projectname'])

            self.log.debug("Using project dir: " + pp)
            sys.path.append(pp)
            func = getattr(__import__("index"), "lambda_handler")

            ctx = LambdaContext(json.loads(open(os.path.join(os.path.expanduser(self.conf.sett['C_BASE_DIR']),
                                                             self.conf.sett['C_INVOKE_DIR_CTX'],
                                                             self.conf.sett['C_INVOKE_CTX_FILE'])).read()))

            func(self._get_event(), ctx)

        return self.conf

    def remote_invoke(self):
        if "projectname" in self.kwargs and self.kwargs['projectname'] is not None:
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
            Payload=open(os.path.join(os.path.expanduser(self.conf.sett['C_BASE_DIR']),
                                      self.conf.sett['C_INVOKE_DIR_EVT'],
                                      self.kwargs['event_file'])).read()
        )

        print(base64.b64decode(ret['LogResult']).decode())

        return self.conf

    def _get_event(self):
        with open(os.path.join(os.path.expanduser(self.conf.sett['C_BASE_DIR']),
                               self.conf.sett['C_INVOKE_DIR_EVT'],
                               self.kwargs['event_file']),
                  'r') as f:
            return json.loads(f.read())
