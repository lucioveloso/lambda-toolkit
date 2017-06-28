from ConfigParser import ConfigParser
from queue import Queue
from ltklambdaproxy import Ltklambdaproxy
from utils import Utils

class Conf:

    config = ""
    vars = ""

    def __init__(self, config_file):
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
            print("Failed to load the settings in the config file.")
            exit(1)

    def list_config(self):
        print("Showing lambda-toolkit configurations:")
        if "C_DEFAULT_ROLE" in self.vars:
            print("- Default Role: " + self.vars['C_DEFAULT_ROLE'])
            print("-----------------")

        for s in self.config.sections():
            if s == self.vars['C_CONFIG_SQS']:
                if 'C_CONFIG_SQS_QUEUES' in self.vars:
                    queues = Utils.get_list_config(self, self.vars['C_CONFIG_SQS'], self.vars['C_CONFIG_SQS_QUEUES'])
                    if len(queues) != 0:
                        print("SQS (Queues):")
                        for q in queues:
                            print("- Queue name: " + q)
                        print("-----------------")
            elif s == self.vars['C_CONFIG_LAMBDAPROXY']:
                lbs = self.config.items(self.vars['C_CONFIG_LAMBDAPROXY'])
                if len(lbs) != 0:
                    print("Lambda Proxies:")
                    for lb in lbs:
                        print("- Lambda Proxy: " + lb[0] + "\t\t[SQS: " + lb[1] + "]")
                    print("-----------------")
            elif s == self.vars['C_CONFIG_SETTINGS']:
                pass
            else:
                deployed = self.config.get(s, "deployed")
                print("- User Lambda Project: " + s + "\t[Deployed: " + deployed + "]")

    def delete_all_config(self):
        if 'C_CONFIG_LAMBDAPROXY' in self.vars:
            for lp in self.config.items(self.vars['C_CONFIG_LAMBDAPROXY']):
                self.conf = Ltklambdaproxy(self, lp[0]).undeploy_lambda_proxy()

        if 'C_CONFIG_SQS_QUEUES' in self.vars:
            queues = Utils.get_list_config(self, self.vars['C_CONFIG_SQS'],
                                           self.vars['C_CONFIG_SQS_QUEUES'])
            for q in queues:
                self.conf = Queue(self, q).delete_queue()

        print("Removed all proxies and queues.")