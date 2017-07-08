#!/usr/bin/env python

import logger
import os
import json
import pkgutil
import boto3

class Conf:

    config = ""
    vars = ""

    def __init__(self):
        self.log = logger.get_my_logger("conf")
        self.config_file = os.path.join(os.path.expanduser('~'), ".lambda-toolkit.json")
        self.read_config()

    def _init_confs(self):
        confs = ['projects', 'queues', 'proxies']
        for c in confs:
            self.full_data[self.region][c] = {}
            setattr(self, c, self.full_data[self.region][c])

    def save_config(self):
        f = open(self.config_file, "w")
        f.write(json.dumps(self.full_data, indent=4))
        f.close()

    def read_config(self):
        self.full_data = None
        if os.path.isfile(self.config_file):
            f = open(self.config_file, "r")
            self.full_data = json.loads(f.read())
            f.close()
        else:
            self.log.info("Creating a new config file: '" + self.config_file + "'")
            f = open(self.config_file, "w")
            self.full_data = json.loads(pkgutil.get_data("lambda_toolkit", "templates/lambda-toolkit.json"))
            f.write(json.dumps(self.full_data, indent=4))
            f.close()

        # Global Config
        self.cli = self.full_data['cli']
        self.sett = self.full_data['settings']

    # Regional Config
        self.region = boto3.session.Session().region_name
        if self.region not in self.full_data:
            self.full_data[self.region] = {}

        self._init_confs()
