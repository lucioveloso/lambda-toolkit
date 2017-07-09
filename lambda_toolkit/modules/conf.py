#!/usr/bin/env python

import logger
import os
import json
import pkgutil
import boto3
from shutil import copytree

class Conf:

    config = ""
    vars = ""

    def __init__(self):
        self.log = logger.get_my_logger(self.__class__.__name__)
        self.config_file = os.path.join(os.path.expanduser('~'), ".lambda-toolkit.json")
        self.read_config()

    def _init_confs(self):
        confs = self.cli.keys()
        # plural issue
        confs.remove("proxy")
        confs.append("proxie")
        for c in confs:
            c = c + "s"
            if c not in self.full_data[self.region]:
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
            self.full_data = json.loads(pkgutil.get_data("lambda_toolkit", "data/lambda-toolkit.json"))
            f.write(json.dumps(self.full_data, indent=4))
            f.close()

        # Global Config
        self.cli = self.full_data['cli']
        self.sett = self.full_data['settings']

        # Create basic folders
        self.data_dir = pkgutil.get_loader("lambda_toolkit").filename

        # TODO: reflexion
        self.base_dir = os.path.expanduser(self.sett['C_BASE_DIR'])

        list_dir = ["LAMBDAS_DIR", "INVOKE_DIR", "INVOKE_DIR_EVT", "INVOKE_DIR_CTX"]

        for d in list_dir:
            setattr(self, d.lower(), os.path.join(self.base_dir, self.sett["C_" + d]))

        if not os.path.exists(self.base_dir):
            self.log.info("Creating the base lambda-toolkit folder: '" + self.base_dir + "'.")
            copytree(os.path.join(self.data_dir, self.sett['C_STANDARD_FOLDER_DIR']), self.base_dir)

        # Regional Config
        self.region = boto3.session.Session().region_name
        if self.region not in self.full_data:
            self.full_data[self.region] = {}

        self._init_confs()
