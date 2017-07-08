#!/usr/bin/env python

import boto3
from utils import Utils
from shutil import rmtree
from shutil import make_archive
import os
import logger
import pkgutil


class Proxy:

    def __init__(self, conf, kwargs):
        self.lbs = boto3.client('lambda')
        self.log = logger.get_my_logger("ltklambdaproxy")
        self.conf = conf
        self.proxies = self.conf.proxies.keys()
        self.queues = self.conf.queues.keys()
        self.base_dir = os.path.expanduser(self.conf.sett['C_BASE_DIR'])
        self.lambdas_dir = os.path.join(self.base_dir, self.conf.sett['C_LAMBDAS_DIR'])
        self.kwargs = kwargs
        if kwargs['proxyname'] is not None:
            self._set_proxyname(kwargs['proxyname'])

    def list_proxy(self):
        if len(self.proxies) > 0:
            self.log.info("Proxies (Lambda proxies):")
            for q in self.proxies:
                self.log.info("- Proxy name '" + q + "' pointing to the queue '"
                              + self.conf.proxies[q]['sqsname'] +"'\t [Runtime: " +
                              self.conf.proxies[q]['runtime'] + "]")

        return self.conf

    def undeployall_proxy(self):
        for q in self.proxies:
            self._set_proxyname(q)
            self.undeploy_proxy()

        return self.conf

    def deploy_proxy(self):

        if self.proxyname in self.proxies:
            self.log.critical("The proxy '" + self.proxyname + "' already exists.")

        if self.kwargs['sqsname'] not in self.queues:
            self.log.critical("The queue '" + self.proxyname + "' does not exist.")

        try:
            os.mkdir(self.lambdaproxy_dir)
        except Exception as a:
            self.log.debug("Proxy temp folder already exists")

        f1 = pkgutil.get_data("lambda_toolkit", self.conf.sett['C_LAMBDAPROXY_FUNC'])
        f2 = open(os.path.join(self.lambdaproxy_dir, "index.py"), "w")
        for line in f1.splitlines():
            f2.write(line.replace(self.conf.sett['C_LAMBDASTANDERD_FUNC_VAR_REPLACE'], self.kwargs['sqsname']))
            f2.write("\n")
        f2.close()
        make_archive(os.path.splitext(self.lambdaproxy_zip_file)[0], "zip", self.lambdaproxy_dir)


        try:
            self.lbs.create_function(
                FunctionName=self.proxyname,
                Runtime=self.kwargs['runtime'],
                Role=self.kwargs['rolename'],
                Handler='index.lambda_handler',
                Description="Proxy lambda function " + self.proxyname + "proxying requests to " + self.kwargs['sqsname'],
                Code={
                    'ZipFile': open(self.lambdaproxy_zip_file, "rb").read()
                }
            )
            self.log.info("Lambda proxy " + self.proxyname + " created proxying requests to " + self.kwargs['sqsname'])
            self.conf.proxies[self.proxyname] = {}
            self.conf.proxies[self.proxyname]['sqsname'] = self.kwargs['sqsname']
            self.conf.proxies[self.proxyname]['runtime'] = self.kwargs['runtime']

        except Exception as e:
            self.log.error(str(e))
            self.log.critical("Failed to create the lambda function")

        rmtree(self.lambdaproxy_dir)

        return self.conf


    def undeploy_proxy(self):
        if self.proxyname not in self.proxies:
            self.log.critical("The proxy '" + self.proxyname + "' does not exist.")

        try:
            self.lbs.delete_function(FunctionName=self.proxyname)
            self.log.info("Lambda proxy '" + self.proxyname + "' has been removed.")
            os.remove(self.lambdaproxy_zip_file)
        except Exception as e:
            self.log.error(str(e))
            self.log.error("Failed to delete the lambda proxy.")

        self.conf.proxies.pop(self.proxyname)

        return self.conf

    def _set_proxyname(self, proxyname):
        self.proxyname = proxyname
        proxyname_region = proxyname + "_" + self.conf.region
        self.lambdaproxy_dir = os.path.join(self.lambdas_dir, self.proxyname)
        self.lambdaproxy_zip_dir = os.path.join(self.lambdas_dir, self.conf.sett['C_LAMBDAS_ZIP_DIR'])
        self.lambdaproxy_zip_file = os.path.join(self.lambdaproxy_zip_dir, self.proxyname + ".zip")