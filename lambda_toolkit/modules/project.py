#!/usr/bin/env python

import os
import pkgutil
from lambda_toolkit.modules.utils import Utils
from shutil import make_archive
from shutil import rmtree
from zipfile import ZipFile
import sys
import time

class Project:
    def __init__(self, conf, kwargs):
        self.log = conf.log

        if Utils.check_kwargs(kwargs, "region"):
            self.log.info("Updating region to '" + kwargs['region'] + "'.")
            self.conf = conf.set_region(kwargs['region'])
        else:
            self.conf = conf

        if Utils.check_kwargs(kwargs, "projectname"):
            self.projectname = kwargs['projectname']
            self._set_project(self.projectname)

        self.kwargs = kwargs
        self.projects = self.conf.projects.keys()


    def _update_new_region(self, reg):
        self.conf.set_region(reg)
        self.projects = self.conf.projects.keys()

    def import_all_project(self):
        lambdas = self.conf.get_boto3("lambda", "client").list_functions()
        for mylb in lambdas['Functions']:
            if mylb['FunctionName'] not in self.conf.proxies:
                self._set_project(mylb['FunctionName'])
                self.import_project()

        self.log.info("Imported all projects in " + self.conf.region + ".")
        return self.conf

    def deploy_all_project(self):
        for s in list(self.projects):
            self._set_project(s)
            self.deploy_project()

        self.log.info("Deployed all projects in " + self.conf.region + ".")
        return self.conf

    def undeploy_all_project(self):
        for s in list(self.projects):
            self._set_project(s)
            self.undeploy_project()

        self.log.info("Undeployed all projects in " + self.conf.region + ".")
        return self.conf

    def create_project(self):
        if self.projectname in self.conf.projects:
            self.log.warn("Project '" + self.projectname + "' already exists in lambda-toolkit.")
        else:
            self._create_project_folders()

            if 'python' in self.kwargs['runtime']:
                open(self.project_dir + "/__init__.py", 'a').close()
                with open(os.path.join(self.project_dir, "index.py"), "wb") as text_file:
                    text_file.write(pkgutil.get_data("lambda_toolkit", self.conf.sett['C_LAMBDASTANDARD_FUNC_PY']))
            elif 'nodejs' in self.kwargs['runtime']:
                with open(os.path.join(self.project_dir, "index.js"), "wb") as text_file:
                    text_file.write(pkgutil.get_data("lambda_toolkit", self.conf.sett['C_LAMBDASTANDARD_FUNC_JS']))

            self.log.info("Project '" + self.projectname + "' "
                          "[" + self.kwargs['runtime'] + "] has been created.")
            self.conf.projects[self.projectname] = {}
            self.conf.projects[self.projectname]['deployed'] = False
            self.conf.projects[self.projectname]['runtime'] = self.kwargs['runtime']

        return self.conf

    def delete_all_project(self):
        for s in list(self.projects):
            self._set_project(s)
            self.delete_project()

        self.log.info("Deleted all projects in " + self.conf.region + ".")
        return self.conf

    def delete_project(self):
        if self.projectname in self.conf.projects:
            self.conf.projects.pop(self.projectname)
            if not os.path.exists(self.project_dir):
                self.log.warn("The folder '" + self.project_dir + "' does not exist. Ignoring folder removing.")
            else:
                rmtree(self.project_dir)
            self.log.info("Project '" + self.projectname + "' has been deleted.")
        else:
            self.log.warn("Project '" + self.projectname + "' does not exist.")

        return self.conf

    def import_project(self):
        if self.projectname in self.conf.proxies.keys():
            self.log.warn("Project '" + self.projectname + "' is a proxy. Ignoring import.")
            return self.conf

        try:
            lambda_function = self.conf.get_boto3("lambda", "client").get_function(FunctionName=self.projectname)

            if self.projectname in self.conf.projects:
                self.log.info("Project '" + self.projectname + "' already exists in your configuration. Updating.")
                self.conf.projects[self.projectname]['deployed'] = True
            else:
                self._create_project_folders()
                open(self.project_dir + "/__init__.py", 'a').close()
                self.conf.projects[self.projectname] = {}
                self.conf.projects[self.projectname]['deployed'] = True
                self.conf.projects[self.projectname]['runtime'] = lambda_function['Configuration']['Runtime']
                self.log.info("Project " + self.projectname + " imported.")

            import requests, zipfile
            if sys.version_info[0] == 3:
                import io
                r = requests.get(lambda_function['Code']['Location'], stream=True)
                z = zipfile.ZipFile(io.BytesIO(r.content))
            else:
                import StringIO
                r = requests.get(lambda_function['Code']['Location'], stream=True)
                z = zipfile.ZipFile(StringIO.StringIO(r.content))

            z.extractall(self.project_dir)
            z.close()
        except Exception as e:
            self.log.error(str(e))
            self.log.warn("The project '" + self.projectname + "' does not exist in AWS environment.")

        return self.conf

    def deploy_project(self):
        if self.projectname not in self.projects:
            self.log.critical("Project '" + self.projectname + "' does not exist.")

        make_archive(self.project_zip_file_without_ext, "zip", self.project_dir)

        try:
            self.conf.get_boto3("lambda", "client").get_function(FunctionName=self.projectname)
            replace = True
        except Exception:
            replace = False

        try:
            if replace:
                self.conf.get_boto3("lambda", "client").update_function_code(
                    FunctionName=self.projectname,
                    ZipFile=open(self.project_zip_file, "rb").read()
                )
                self.log.info("Lambda project " + self.projectname + " was redeployed.")
            else:
                if 'rolename' not in self.kwargs:
                    self.log.warn("Project '" + self.project +
                                  "' is new. The parameter --rolename is required. Skipping.")
                    return self.conf

                self.conf.get_boto3("lambda", "client").create_function(
                    FunctionName=self.projectname,
                    Runtime=self.conf.projects[self.projectname]['runtime'],
                    Role=self.kwargs['rolename'],
                    Handler='index.lambda_handler',
                    Description="Lambda project " + self.projectname + " deployed by lambda-proxy",
                    Code={
                        'ZipFile': open(self.project_zip_file, "rb").read()
                    }
                )
                self.log.info("Lambda project " + self.projectname + " was created and deployed.")

            self.conf.projects[self.projectname]['deployed'] = True

        except Exception as e:
            self.log.error(str(e))
            self.log.critical("Failed to deploy the lambda project.")

        return self.conf

    def undeploy_project(self):
        if self.projectname not in self.projects:
            self.log.critical("Project '" + self.projectname + "' does not exist.")

        try:
            self.conf.get_boto3("lambda", "client").delete_function(FunctionName=self.projectname)
            self.log.info("Project '" + self.projectname + "' is now undeployed.")
        except Exception as e:
            self.log.warn("Project '" + self.projectname + "' is not deployed.")

        self.conf.projects[self.projectname]['deployed'] = False

        return self.conf


    def delete_all_regions_project(self):
        for reg in self.conf.aws_regions:
            self._update_new_region(reg)
            self.delete_all_project()

        return self.conf

    def deploy_all_regions_project(self):
        for reg in self.conf.aws_regions:
            self._update_new_region(reg)
            self.deploy_all_project()

        return self.conf

    def undeploy_all_regions_project(self):
        for reg in self.conf.aws_regions:
            self._update_new_region(reg)
            self.undeploy_all_project()

        return self.conf

    def import_all_regions_project(self):
        for reg in self.conf.aws_regions:
            self._update_new_region(reg)
            self.import_all_project()

        return self.conf

    def list_aws_all_project(self):
        for reg in self.conf.aws_regions:
            self._update_new_region(reg)
            self.list_aws_project()

        return self.conf

    def list_all_project(self):
        for reg in self.conf.aws_regions:
            self._update_new_region(reg)
            self.list_project()

        return self.conf

    def check_regions_delay_project(self):
        for reg in self.conf.aws_regions:
            self._update_new_region(reg)
            start_time = time.time()
            self.conf.get_boto3("lambda", "client").list_functions()
            self.log.info('{0: <{1}}'.format(self.conf.region + ": ", 20) +
                          str((time.time() - start_time)))

        return self.conf

    def list_aws_project(self):
        self.log.info("AWS Projects (Lambda Functions in " + self.conf.region + "):")
        lambdas = self.conf.get_boto3("lambda", "client").list_functions()
        for mylb in lambdas['Functions']:
            imported = False
            if mylb['FunctionName'] in self.projects:
                imported = True
            self.log.info('{0: <{1}}'.format("- Project:", 15) +
                          '{0: <{1}}'.format(mylb['FunctionName'], 25) +
                          '{0: <{1}}'.format("Imported:", 10) +
                          '{0: <{1}}'.format(str(imported), 25) +
                          '{0: <{1}}'.format("Runtime:", 10) +
                          mylb['Runtime'])

        return self.conf

    def list_project(self):
        if len(self.projects) > 0:
            self.log.info("User Projects (Lambda Functions in " + self.conf.region + "):")
            for p in self.projects:
                self.log.info('{0: <{1}}'.format("- Project:", 15) +
                              '{0: <{1}}'.format(p, 25) +
                              '{0: <{1}}'.format("Deployed:", 10) +
                              '{0: <{1}}'.format(str(self.conf.projects[p]["deployed"]), 25) +
                              '{0: <{1}}'.format("Runtime:", 10) +
                              self.conf.projects[p]["runtime"])

        return self.conf

    def _create_project_folders(self):
        if not os.path.exists(self.project_dir):
            self.log.info("Creating the project lambda-toolkit folder '" + self.project_dir + "'")
            os.makedirs(self.project_dir)

        if not os.path.exists(self.project_zip_dir):
            self.log.info("Creating the zip lambda-toolkit folder '" + self.project_zip_dir + "'")
            os.makedirs(self.project_zip_dir)


    def _set_project(self, projectname):
        self.log.debug("Updating project environment to: '" + projectname + "'")
        if projectname in self.conf.proxies.keys():
            self.log.critical("You cannot act in a project with the same name of an existing proxy.")
        self.projectname = projectname
        self.project_dir = os.path.join(Utils.fixpath(self.conf.sett['C_BASE_DIR']),
                                        Utils.fixpath(self.conf.sett['C_LAMBDAS_DIR']),
                                        self.conf.region, projectname)
        self.project_zip_dir = os.path.join(Utils.fixpath(self.conf.sett['C_BASE_DIR']),
                                            Utils.fixpath(self.conf.sett['C_LAMBDAS_DIR']),
                                            self.conf.region,
                                            Utils.fixpath(self.conf.sett['C_LAMBDAS_ZIP_DIR']))
        self.project_zip_file = os.path.join(self.project_zip_dir, projectname + ".zip")
        self.project_zip_file_without_ext = os.path.join(self.project_zip_dir, projectname)

# TODO -> ZIP (ALL / SPECIFIC) (local / remote)
# TODO -> SYNC ONLY STATUS (ALL / SPECIFIC)
# TODO -> SYNC FILES -> OVERWRITE LOCAL OR REMOTE (same that import and deploy?)
# TODO -> COMPARE MD5 (ALL / SPECIFIC)
# TODO -> IMPORT/DEPLOY WITH OVERWRITE OPTION
# TODO -> import from a .zip (only local, only deploy, both)
# TODO -> Change runtime
# TODO -> Copy project among regions
