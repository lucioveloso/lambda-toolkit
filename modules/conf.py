from ConfigParser import ConfigParser
from queue import Queue
from ltklambdaproxy import Ltklambdaproxy
from utils import Utils
import logger


class Conf:

    config = ""
    vars = ""

    def __init__(self, config_file):
        self.log = logger.get_my_logger("conf")
        self.config_file = config_file
        self.read_config()
        self.load_variables()

    def read_config(self):
        self.config = ConfigParser()
        self.config.optionxform = str
        self.config.read(self.config_file)

    def save_config(self):
        with open(self.config_file, 'wb') as configfile:
            self.config.write(configfile)

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

        self.log.info("User lambda projects:")
        for s in self.config.sections():
            if (s == self.vars['C_CONFIG_SETTINGS'] or
                s == self.vars['C_CONFIG_LAMBDAPROXY'] or
                s == self.vars['C_CONFIG_SQS']):
                pass
            else:
                deployed = self.config.get(s, "deployed")
                self.log.info("- User Lambda Project: " + s + "\t[Deployed: " + deployed + "]")

    def delete_all_config(self):
        if 'C_CONFIG_LAMBDAPROXY' in self.vars:
            if self.config.has_section(self.vars['C_CONFIG_LAMBDAPROXY']):
                for lp in self.config.items(self.vars['C_CONFIG_LAMBDAPROXY']):
                    self.conf = Ltklambdaproxy(self, lp[0]).undeploy_lambda_proxy()

        if 'C_CONFIG_SQS_QUEUES' in self.vars and 'C_CONFIG_SQS' in self.vars:
            queues = Utils.get_list_config(self, self.vars['C_CONFIG_SQS'],
                                           self.vars['C_CONFIG_SQS_QUEUES'])
            for q in queues:
                self.conf = Queue(self, q).delete_queue()

        self.log.info("Removed all proxies and queues.")
