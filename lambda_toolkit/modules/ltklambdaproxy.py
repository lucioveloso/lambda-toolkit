#!/usr/bin/env python

import boto3
from utils import Utils
from shutil import rmtree
from shutil import make_archive
from os import mkdir
from os import remove
import logger


class Ltklambdaproxy:

    def __init__(self, conf, lambdaname):
        self.log = logger.get_my_logger("ltklambdaproxy")
        self.conf = conf
        if lambdaname != "":
            self.lambdaname = lambdaname
        else:
            self.log.critical("Parameter --lambdaname are required.")

    def deploy_lambda_proxy(self, rolename, sqsname):
        rolename = Utils.define_lambda_role(self.conf, rolename)
        if sqsname == "":
            self.log.critical("Parameter --sqsname are required.")

        if sqsname not in Utils.get_list_config(self.conf, self.conf.vars['C_CONFIG_SQS'],
                                                     self.conf.vars['C_CONFIG_SQS_QUEUES']):
            self.log.critical("The queue " + sqsname + " does not exist.")

        if not self.conf.config.has_section(self.conf.vars['C_CONFIG_LAMBDAPROXY']):
            self.conf.config.add_section(self.conf.vars['C_CONFIG_LAMBDAPROXY'])
        else:
            if self.conf.config.has_option(self.conf.vars['C_CONFIG_LAMBDAPROXY'], self.lambdaname):
                self.log.critical("Lambda proxy " + self.lambdaname + " already exists")

        lambdafolder = self.conf.vars['C_LAMBDAS_DIR'] + self.lambdaname + "/"

        mkdir(lambdafolder)

        f1 = open(self.conf.vars['C_LAMBDAPROXY_FUNC'], "r")
        f2 = open(lambdafolder + "index.py", "w")
        for line in f1:
            f2.write(line.replace(self.conf.vars['C_LAMBDASTANDERD_FUNC_VAR_REPLACE'], sqsname))
        f1.close()
        f2.close()
        make_archive(self.conf.vars['C_LAMBDAS_DIR'] + self.conf.vars['C_LAMBDAS_ZIP_DIR']
                     + self.lambdaname, "zip", lambdafolder)

        lbs = boto3.client('lambda')

        try:
            lbs.create_function(
                FunctionName=self.lambdaname,
                Runtime='python2.7',
                Role=rolename,
                Handler='index.lambda_handler',
                Description="Proxy lambda function " + self.lambdaname + "proxying requests to " + sqsname,
                Code={
                    'ZipFile': open(self.conf.vars['C_LAMBDAS_DIR'] + self.conf.vars['C_LAMBDAS_ZIP_DIR']
                                    + self.lambdaname + ".zip", "rb").read()
                }
            )
            self.log.info("Lambda proxy " + self.lambdaname + " created proxying requests to " + sqsname)
            self.conf.config.set(self.conf.vars['C_CONFIG_LAMBDAPROXY'], self.lambdaname, sqsname)

        except Exception as e:
            self.log.error(str(e))
            self.log.critical("Failed to create the lambda function")

        rmtree(lambdafolder)

        return self.conf


    def undeploy_lambda_proxy(self):
        if self.conf.config.has_section(self.conf.vars['C_CONFIG_LAMBDAPROXY']):
            if self.conf.config.has_option(self.conf.vars['C_CONFIG_LAMBDAPROXY'], self.lambdaname):
                lbs = boto3.client('lambda')
                try:
                    lbs.delete_function(FunctionName=self.lambdaname)
                    self.log.info("Lambda proxy " + self.lambdaname + " has been removed.")
                    remove(self.conf.vars['C_LAMBDAS_DIR'] + self.conf.vars['C_LAMBDAS_ZIP_DIR'] + self.lambdaname + ".zip")
                except Exception as e:
                    self.log.error(str(e))
                    self.log.error("Failed to delete the lambda proxy.")

                self.conf.config.remove_option(self.conf.vars['C_CONFIG_LAMBDAPROXY'], self.lambdaname)
            else:
                self.log.critical("Lambda proxy " + self.lambdaname + " does not exist")

        return self.conf
