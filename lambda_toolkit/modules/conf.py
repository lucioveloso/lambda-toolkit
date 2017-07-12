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
        if self.region not in self.full_data:
            self.full_data[self.region] = {}

        confs = self.cli.keys()
        # plural issue
        confs.remove("proxy")
        confs.append("proxie")
        for c in confs:
            c = c + "s"
            if c not in self.full_data[self.region]:
                self.full_data[self.region][c] = {}
            setattr(self, c, self.full_data[self.region][c])

    def get_boto3(self, api_type):
        if self.auth_mode == "env":
            return boto3.client(
                api_type,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
        else:
            return boto3.client(api_type)

    def get_boto3_r(self, api_type):
        if self.auth_mode == "env":
            return boto3.resource(
                api_type,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
        else:
            return boto3.resource(api_type)

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
            copytree(os.path.join(self.data_dir, self.sett['C_STANDARD_FOLDER_DIR']), self.base_dir)

        # Regional Config
        self.auth_mode = "env"
        for env_var in ['AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']:
            if env_var not in os.environ:
                self.auth_mode = "file"

        if self.auth_mode == "env":
            self.region = os.environ['AWS_REGION']
            self.access_key = os.environ['AWS_ACCESS_KEY_ID']
            self.secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
        else:
            self.region = boto3.session.Session().region_name

        if self.region is None:
            self.log.critical("Cannot read 'region' from env or credential file")

        self._init_confs()
