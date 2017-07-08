#!/usr/bin/env python

from ConfigParser import ConfigParser
from queue import Queue
from ltklambdaproxy import Ltklambdaproxy
from utils import Utils
from role import Role
import logger
import os
import json
import pkgutil
import boto3

class Conf:

    config = ""
    vars = ""

    def __init__(self, config_file):
        self.log = logger.get_my_logger("conf")
        self.config_file = os.path.join(os.path.expanduser('~'), config_file)
        self.read_config()
        self.load_variables()

    def save_config(self):
        file_t = os.path.join(os.path.expanduser('~'), ".lambda-toolkit.json")
        f = open(file_t, "w")
        f.write(json.dumps(self.full_data, indent=4))
        f.close()

        f = open(self.config_file, "w+")
        self.config.write(f)

    def load_variables(self):
        if self.config.has_section("settings"):
            par = dict(self.config.items("settings"))
            for p in par:
                par[p] = par[p].split("#", 1)[0].strip().replace("\"", "")
            self.vars = par
        else:
            self.log.critical("Failed to load the settings in the config file.")

    def list_config(self):
        self.log.info("Showing lambda-toolkit configurations:")
        if self.sett.has_key("C_DEFAULT_ROLE"):
            self.log.info("- Default Role: " + self.sett['C_DEFAULT_ROLE'])
            self.log.info("---------------------------------------------------")

        if self.config.has_section(self.vars['C_CONFIG_SQS']):
            if 'C_CONFIG_SQS_QUEUES' in self.vars:
                queues = Utils.get_list_config(self, self.vars['C_CONFIG_SQS'], self.vars['C_CONFIG_SQS_QUEUES'])
                if len(queues) != 0:
                    self.log.info("SQS (Queues):")
                    for q in queues:
                        self.log.info("- Queue name: " + q)
                    self.log.info("---------------------------------------------------")

        if self.config.has_section(self.vars['C_CONFIG_LAMBDAPROXY']):
            lbs = self.config.items(self.vars['C_CONFIG_LAMBDAPROXY'])
            if len(lbs) != 0:
                self.log.info("Lambda Proxies:")
                for lb in lbs:
                    self.log.info("- Lambda Proxy: " + lb[0] + "\t\t[SQS: " + lb[1] + "]")
                self.log.info("---------------------------------------------------")

        for s in self.config.sections():
            if not Utils.validate_reserved_sections(self, s):
                deployed = self.config.get(s, "deployed")
                self.log.info("- User Lambda Project: " + s + "\t[Deployed: " + deployed + "]")

    def delete_all_config(self):
        if 'C_CONFIG_LAMBDAPROXY' in self.vars:
            if self.config.has_section(self.vars['C_CONFIG_LAMBDAPROXY']):
                for lp in self.config.items(self.vars['C_CONFIG_LAMBDAPROXY']):
                    self = Ltklambdaproxy(self, lp[0]).undeploy_lambda_proxy()

        if 'C_CONFIG_SQS_QUEUES' in self.vars and 'C_CONFIG_SQS' in self.vars:
            queues = Utils.get_list_config(self, self.vars['C_CONFIG_SQS'],
                                           self.vars['C_CONFIG_SQS_QUEUES'])
            for q in queues:
                self = Queue(self, q).delete_queue()

        self = Role(self, "bypassvalidator").unset_default_role()

    def read_config(self):

        file_t = os.path.join(os.path.expanduser('~'), ".lambda-toolkit.json")
        self.full_data = None
        if os.path.isfile(file_t):
            f = open(file_t, "r")
            self.full_data = json.loads(f.read())
            f.close()
        else:
            self.log.info("Creating a new config file: '" + self.config_file + "'")
            f = open(file_t, "w")
            self.full_data = json.loads(pkgutil.get_data("lambda_toolkit", "templates/.lambda-toolkit.json"))
            f.write(json.dumps(self.full_data, indent=4))
            f.close()

        # Global Config
        self.cli = self.full_data['cli']
        self.sett = self.full_data['settings']

        # Regional Config
        self.region = boto3.session.Session().region_name
        if self.region not in self.full_data:
            self.full_data[self.region] = {}
            self.full_data[self.region]['projects'] = {}
            self.full_data[self.region]['queues'] = {}

        self.queues = self.full_data[self.region]['queues']
        self.projects = self.full_data[self.region]['projects']





        self.config = ConfigParser()
        self.config.optionxform = str
        self.config.read(self.config_file)
