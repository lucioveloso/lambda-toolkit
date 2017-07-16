#!/usr/bin/env python

import lambda_toolkit.modules.logger as logger
from lambda_toolkit.modules.utils import Utils
import os
import json
import pkgutil
import boto3
from shutil import copytree


class Conf:

    def __init__(self):
        self.config_file = os.path.join(os.path.expanduser('~'), ".lambda-toolkit.json")
        self.log = logger.get_my_logger("lambda-toolkit")
        # Get default configuration
        default_conf = json.loads(pkgutil.get_data("lambda_toolkit", "data/lambda-toolkit.json"))
        self.cli = default_conf['cli']
        self.aws_regions = default_conf['aws-regions']
        self.sett = self._sync_settings(default_conf)
        self._copy_default_folder()
        self._set_authmode_and_default_region()

    def set_region(self, region):
        self.region = region
        if 'configurations' not in self.json_conf:
            self.json_conf['configurations'] = {}

        if self.region not in self.json_conf['configurations']:
            self.json_conf['configurations'][self.region] = {}

        confs = list(self.cli)
        # plural issue
        confs.remove("proxy")
        confs.append("proxie")
        for c in confs:
            c = c + "s"
            if c not in self.json_conf['configurations'][self.region]:
                self.json_conf['configurations'][self.region][c] = {}
            setattr(self, c, self.json_conf['configurations'][self.region][c])

        return self

    def save_config(self):
        with open(self.config_file, "w") as f:
            f.write(json.dumps(self.json_conf, indent=4))

    def get_boto3(self, api_name, api_method):
        func = getattr(__import__("boto3"), api_method)
        if self.auth_mode == "env":
            return func(
                api_name,
                aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                region_name=self.region
            )
        else:
            return func(api_name, region_name=self.region)

    def _set_authmode_and_default_region(self):
        self.auth_mode = "env"
        for env_var in ['AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']:
            if env_var not in os.environ:
                self.auth_mode = "file"
                s = boto3.session.Session().region_name
                if s is None:
                    self.log.critical("Cannot read 'region' from env or credential file")
                self.set_region(boto3.session.Session().region_name)
                break

        if self.auth_mode == "env":
            self.set_region(os.environ['AWS_REGION'])


    def _copy_default_folder(self):
        if not os.path.exists(Utils.fixpath(self.sett['C_BASE_DIR'])):
            path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if not os.path.exists(Utils.fixpath(self.sett['C_BASE_DIR'])):
                copytree(os.path.join(path, Utils.fixpath(self.sett['C_STANDARD_FOLDER_DIR'])),
                         Utils.fixpath(self.sett['C_BASE_DIR']))

    def _sync_settings(self, default_conf):
        if os.path.isfile(self.config_file):
            with open(self.config_file, "r") as f:
                self.json_conf = json.loads(f.read())
                # Check for new settings (Make compatible with older versions)
                for setting in default_conf['settings']:
                    if setting not in self.json_conf['settings']:
                        self.log.debug("Adding new setting: " + setting)
                        self.json_conf['settings'][setting] = default_conf['settings'][setting]
                # Remove deprecated settings
                remove_list = []
                for setting in self.json_conf['settings']:
                    if setting not in default_conf['settings']:
                        self.log.debug("Removing old setting: " + setting)
                        remove_list.append(setting)
                for r in remove_list:
                    self.json_conf['settings'].pop(r)
        else:
            self.json_conf = {}
            self.json_conf['settings'] = default_conf['settings']

        return self.json_conf['settings']
