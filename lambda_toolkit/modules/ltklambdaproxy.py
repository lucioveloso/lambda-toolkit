#!/usr/bin/env python

import boto3
from utils import Utils
from shutil import rmtree
from shutil import make_archive
import os
import logger
import pkgutil


class Ltklambdaproxy:

    def __init__(self, conf, lambdaname):
        self.log = logger.get_my_logger("ltklambdaproxy")
        self.conf = conf
        if lambdaname != "":
            self.lambdaname = lambdaname
        else:
            self.log.critical("Parameter --lambdaname are required.")

        self.base_dir = os.path.expanduser(self.conf.vars['C_BASE_DIR'])
        self.lambdas_dir = os.path.join(self.base_dir, self.conf.vars['C_LAMBDAS_DIR'])
        self.lambdaproxy_dir = os.path.join(self.lambdas_dir, self.lambdaname)
        self.lambdaproxy_zip_dir = os.path.join(self.lambdas_dir, self.conf.vars['C_LAMBDAS_ZIP_DIR'])
        self.lambdaproxy_zip_file = os.path.join(self.lambdaproxy_zip_dir, self.lambdaname + ".zip")

    def deploy_lambda_proxy(self, rolename, sqsname):
        rolename = Utils.define_lambda_role(self.conf, rolename)
        if sqsname == "":
            self.log.critical("Parameter --sqsname are required.")

        if sqsname not in Utils.get_list_config(self.conf,
                                                self.conf.vars['C_CONFIG_SQS'],
                                                self.conf.vars['C_CONFIG_SQS_QUEUES']):
            self.log.critical("The queue " + sqsname + " does not exist.")

        if not self.conf.config.has_section(self.conf.vars['C_CONFIG_LAMBDAPROXY']):
            self.conf.config.add_section(self.conf.vars['C_CONFIG_LAMBDAPROXY'])
        else:
            if self.conf.config.has_option(self.conf.vars['C_CONFIG_LAMBDAPROXY'], self.lambdaname):
                self.log.critical("Lambda proxy " + self.lambdaname + " already exists")

        try:
            os.mkdir(self.lambdaproxy_dir)
        except Exception as a:
            self.log.debug("Proxy temp folder already exists")

        f1 = pkgutil.get_data("lambda_toolkit", self.conf.vars['C_LAMBDAPROXY_FUNC'])
        f2 = open(os.path.join(self.lambdaproxy_dir, "index.py"), "w")
        for line in f1.splitlines():
            print(line.replace(self.conf.vars['C_LAMBDASTANDERD_FUNC_VAR_REPLACE'], sqsname))
            f2.write(line.replace(self.conf.vars['C_LAMBDASTANDERD_FUNC_VAR_REPLACE'], sqsname))
            f2.write("\n")
        f2.close()
        make_archive(os.path.splitext(self.lambdaproxy_zip_file)[0], "zip", self.lambdaproxy_dir)

        lbs = boto3.client('lambda')
        try:
            lbs.create_function(
                FunctionName=self.lambdaname,
                Runtime='python2.7',
                Role=rolename,
                Handler='index.lambda_handler',
                Description="Proxy lambda function " + self.lambdaname + "proxying requests to " + sqsname,
                Code={
                    'ZipFile': open(self.lambdaproxy_zip_file, "rb").read()
                }
            )
            self.log.info("Lambda proxy " + self.lambdaname + " created proxying requests to " + sqsname)
            self.conf.config.set(self.conf.vars['C_CONFIG_LAMBDAPROXY'], self.lambdaname, sqsname)

        except Exception as e:
            self.log.error(str(e))
            self.log.critical("Failed to create the lambda function")

        rmtree(self.lambdaproxy_dir)

        return self.conf


    def undeploy_lambda_proxy(self):
        if self.conf.config.has_section(self.conf.vars['C_CONFIG_LAMBDAPROXY']):
            if self.conf.config.has_option(self.conf.vars['C_CONFIG_LAMBDAPROXY'], self.lambdaname):
                lbs = boto3.client('lambda')
                try:
                    lbs.delete_function(FunctionName=self.lambdaname)
                    self.log.info("Lambda proxy " + self.lambdaname + " has been removed.")
                    os.remove(self.lambdaproxy_zip_file)
                except Exception as e:
                    self.log.error(str(e))
                    self.log.error("Failed to delete the lambda proxy.")

                self.conf.config.remove_option(self.conf.vars['C_CONFIG_LAMBDAPROXY'], self.lambdaname)
            else:
                self.log.critical("Lambda proxy " + self.lambdaname + " does not exist")

        return self.conf
