#!/usr/bin/env python

from ConfigParser import ConfigParser
from queue import Queue
from ltklambdaproxy import Ltklambdaproxy
from utils import Utils
from role import Role
import logger
import os


class Conf:

    config = ""
    vars = ""

    def __init__(self, config_file):
        self.log = logger.get_my_logger("conf")
        self.config_file = os.path.join(os.path.expanduser('~'), config_file)
        self.read_config()
        self.load_variables()

    def save_config(self):
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
        if "C_DEFAULT_ROLE" in self.vars:
            self.log.info("- Default Role: " + self.vars['C_DEFAULT_ROLE'])
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
        self.config = ConfigParser()
        self.config.optionxform = str
        if not os.path.isfile(self.config_file):
            self.log.info("Creating a new config file: '" + self.config_file + "'")
            open(self.config_file, 'a').close()
            self.config.add_section("settings")
            self.config.set("settings", "C_BASE_DIR", "\"~/lambda-toolkit/\"")
            self.config.set("settings", "C_LAMBDAS_DIR", "\"lambdas/\"")
            self.config.set("settings", "C_LAMBDAS_ZIP_DIR", "\".zips/\"")
            self.config.set("settings", "C_LAMBDAPROXY_FUNC", "\"templates/lambda-proxy/index.py\"")
            self.config.set("settings", "C_LAMBDASTANDARD_FUNC", "\"templates/standard-lambda/index.py\"")
            self.config.set("settings", "C_LAMBDASTANDERD_FUNC_VAR_REPLACE", "\"TEMPLATEQUEUENAME\"")
            self.config.set("settings", "C_CONFIG_SQS", "\"sqs\"")
            self.config.set("settings", "C_CONFIG_SQS_QUEUES", "\"queues\"")
            self.config.set("settings", "C_CONFIG_SETTINGS", "\"settings\"")
            self.config.set("settings", "C_CONFIG_LAMBDAPROXY", "\"lambda-proxy\"")
            self.config.set("settings", "C_CONFIG_DEFAULT_ROLE", "\"DEFAULT_ROLE\"")
            self.config.set("settings", "QUEUE_GETMESSAGE_VISIBILITY_TIMEOUT", 10)
            self.config.set("settings", "QUEUE_GETMESSAGE_WAITTIMESECONDS", 20)
            self.config.set("settings", "QUEUE_GETMESSAGE_MAXNUMBEROFMESSAGES", 10)
            self.config.set("settings", "QUEUE_CREATEQUEUE_VISIBILITY_TIMEOUT", 3)
            self.config.set("settings", "C_CONFIG_TAIL_TIME_TO_SLEEP", 5)
            self.config.set("settings", "C_CONFIG_TAIL_TIME_PREVIOUS_LOG", 300000)
            self.save_config()

        self.config.read(self.config_file)
