#!/usr/bin/env python

import os
import pkgutil
import pickle
from shutil import make_archive
from shutil import rmtree
from lambda_toolkit.modules.utils import Utils


class Proxy:
    def __init__(self, conf, kwargs):
        self.lbs = conf.get_boto3("lambda", "client")
        self.log = conf.log

        if Utils.check_kwargs(kwargs, "region"):
            self.log.info("Updating region to '" + kwargs['region'] + "'.")
            self.conf = conf.set_region(kwargs['region'])
        else:
            self.conf = conf

        if Utils.check_kwargs(kwargs, "proxyname"):
            self.proxyname = kwargs['proxyname']
            self._set_proxyname(kwargs['proxyname'])

        self.proxies = self.conf.proxies.keys()
        self.queues = self.conf.queues.keys()
        self.kwargs = kwargs

    def list_proxy(self):
        if len(self.proxies) > 0:
            self.log.info("Proxies (Lambda proxies):")
            for q in self.proxies:
                self.log.info('{0: <{1}}'.format("- Proxy name:", 15) +
                              '{0: <{1}}'.format(q, 25) +
                              '{0: <{1}}'.format("Queue:", 10) +
                              '{0: <{1}}'.format(self.conf.proxies[q]['sqsname'], 25) +
                              '{0: <{1}}'.format("Runtime:", 10) +
                              self.conf.proxies[q]['runtime'])

        return self.conf

    def undeploy_all_proxy(self):
        for q in list(self.proxies):
            self._set_proxyname(q)
            self.undeploy_proxy()

        self.log.info("Undeployed all proxies.")
        return self.conf

    def deploy_proxy(self):
        if self.proxyname in self.proxies:
            self.log.critical("The proxy '" + self.proxyname + "' already exists.")

        if self.kwargs['sqsname'] not in self.queues:
            self.log.critical("The queue '" + self.proxyname + "' does not exist.")

        try:
            os.makedirs(self.lambdaproxy_dir)
        except Exception as a:
            self.log.debug("Proxy temp folder already exists")

        f1 = pkgutil.get_data("lambda_toolkit", self.conf.sett['C_LAMBDAPROXY_FUNC'])
        if 'python' in self.kwargs['runtime']:
            index_file = "index.py"
        elif 'nodejs' in self.kwargs['runtime']:
            index_file = "index.js"

        f2 = open(os.path.join(self.lambdaproxy_dir, index_file), "w")
        for line in f1.splitlines():
            a = str(line.decode()).replace(self.conf.sett['C_LAMBDASTANDERD_FUNC_VAR_REPLACE'], self.kwargs['sqsname'])
            f2.write(a)
            f2.write("\n")
        f2.close()

        make_archive(os.path.splitext(self.lambdaproxy_zip_file)[0], "zip", self.lambdaproxy_dir)

        try:
            self.lbs.create_function(
                FunctionName=self.proxyname,
                Runtime=self.kwargs['runtime'],
                Role=self.kwargs['rolename'],
                Handler='index.lambda_handler',
                Description="Proxy lambda function " + self.proxyname + "proxying requests to " + self.kwargs[
                    'sqsname'],
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
        self.log.debug("Updating proxy environment to: '" + proxyname + "'")
        if  proxyname in self.conf.projects.keys():
            self.log.critical("You cannot create a proxy with the same name of an existing project.")

        self.proxyname = proxyname
        self.lambdaproxy_dir = os.path.join(Utils.fixpath(self.conf.sett['C_BASE_DIR']),
                                            Utils.fixpath(self.conf.sett['C_LAMBDAS_DIR']),
                                            self.conf.region,
                                            proxyname)
        self.lambdaproxy_zip_dir = os.path.join(Utils.fixpath(self.conf.sett['C_BASE_DIR']),
                                                Utils.fixpath(self.conf.sett['C_LAMBDAS_DIR']),
                                                self.conf.region,
                                                Utils.fixpath(self.conf.sett['C_LAMBDAS_ZIP_DIR']))
        self.lambdaproxy_zip_file = os.path.join(self.lambdaproxy_zip_dir, proxyname + ".zip")
