#!/usr/bin/env python

import os
import pkgutil
from shutil import make_archive
from shutil import rmtree
from urllib import urlretrieve
from zipfile import ZipFile

import boto3

import logger


class Project:
    def __init__(self, conf, kwargs):
        self.lbs = boto3.client('lambda')
        self.log = logger.get_my_logger(self.__class__.__name__)
        self.conf = conf
        self.projects = self.conf.projects.keys()
        self.kwargs = kwargs
        if 'projectname' in kwargs and kwargs['projectname'] is not None:
            self._set_project(kwargs['projectname'])

    def import_all_project(self):
        lambdas = self.lbs.list_functions()
        for mylb in lambdas['Functions']:
            self._set_project(mylb['FunctionName'])
            self.import_project()

        self.log.info("Imported all projects.")
        return self.conf

    def deploy_all_project(self):
        for s in self.projects:
            self._set_project(s)
            self.deploy_project()

        self.log.info("Deployed all projects.")
        return self.conf

    def undeploy_all_project(self):
        for s in self.projects:
            self._set_project(s)
            self.undeploy_project()

        self.log.info("Undeployed all projects.")
        return self.conf

    def create_project(self):
        if self.projectname in self.conf.projects:
            self.log.warn("Project '" + self.projectname + "' already exists in lambda-toolkit.")
        else:
            self._create_project_folders()

            if 'python' in self.kwargs['runtime']:
                open(self.project_dir + "/__init__.py", 'a').close()
                with open(os.path.join(self.project_dir, "index.py"), "w") as text_file:
                    text_file.write(pkgutil.get_data("lambda_toolkit", self.conf.sett['C_LAMBDASTANDARD_FUNC_PY']))
            elif 'nodejs' in self.kwargs['runtime']:
                with open(os.path.join(self.project_dir, "index.js"), "w") as text_file:
                    text_file.write(pkgutil.get_data("lambda_toolkit", self.conf.sett['C_LAMBDASTANDARD_FUNC_JS']))

            self.log.info("Project '" + self.projectname + "' "
                          "[" + self.kwargs['runtime'] + "] has been created.")
            self.conf.projects[self.projectname] = {}
            self.conf.projects[self.projectname]['deployed'] = False
            self.conf.projects[self.projectname]['runtime'] = self.kwargs['runtime']

        return self.conf

    def delete_all_project(self):
        for s in self.projects:
            self._set_project(s)
            self.delete_project()

        self.log.info("Deleted all projects.")
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
            lambda_function = self.lbs.get_function(FunctionName=self.projectname)

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

            urlretrieve(lambda_function['Code']['Location'], self.project_zip_file)
            zip_ref = ZipFile(self.project_zip_file, 'r')
            zip_ref.extractall(self.project_dir)
            zip_ref.close()

        except Exception as e:
            self.log.error(str(e))
            self.log.warn("The project '" + self.projectname + "' does not exist in AWS environment.")

        return self.conf

    def deploy_project(self):
        if self.projectname not in self.projects:
            self.log.critical("Project '" + self.projectname + "' does not exist.")

        make_archive(self.project_zip_file_without_ext, "zip", self.project_dir)

        try:
            self.lbs.get_function(FunctionName=self.projectname)
            replace = True
        except Exception:
            replace = False

        try:
            if replace:
                self.lbs.update_function_code(
                    FunctionName=self.projectname,
                    ZipFile=open(self.project_zip_file, "rb").read()
                )
                self.log.info("Lambda project " + self.projectname + " was redeployed.")
            else:
                self.lbs.create_function(
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

        #os.remove(self.project_zip_file)
        return self.conf

    def undeploy_project(self):
        if self.projectname not in self.projects:
            self.log.critical("Project '" + self.projectname + "' does not exist.")

        try:
            self.lbs.delete_function(FunctionName=self.projectname)
            self.log.info("Project '" + self.projectname + "' is now undeployed.")
        except Exception as e:
            self.log.warn("Project '" + self.projectname + "' is not deployed.")

        self.conf.projects[self.projectname]['deployed'] = False

        return self.conf

    def list_aws_project(self):
        lambdas = self.lbs.list_functions()
        for mylb in lambdas['Functions']:
            imported = False
            if mylb['FunctionName'] in self.projects:
                print("imported")
                imported = True

            self.log.info("- User Lambda Project: " + mylb['FunctionName'] +
                          "\t[Runtime: " + mylb['Runtime'] + "]"
                          "\t[Imported: " + str(imported) + "]")

        return self.conf

    def list_project(self):
        if len(self.projects) > 0:
            self.log.info("User Projects (Lambda Functions):")
            for p in self.projects:
                self.log.info("- User Lambda Project: " + p +
                              "\t[Deployed: " + str(self.conf.projects[p]["deployed"]) + "]" +
                              "\t[Runtime: " + self.conf.projects[p]["runtime"] + "]")

        return self.conf

    def _create_project_folders(self):
        if not os.path.exists(self.project_dir):
            self.log.info("Creating the project lambda-toolkit folder '" + self.project_dir + "'")
            os.mkdir(self.project_dir)

        if not os.path.exists(self.project_zip_dir):
            self.log.info("Creating the zip lambda-toolkit folder '" + self.project_zip_dir + "'")
            os.mkdir(self.project_zip_dir)


    def _set_project(self, projectname):
        self.log.debug("Updating project environment to: '" + projectname + "'")
        self.projectname = projectname
        projectname_region = projectname + "_" + self.conf.region
        self.project_dir = os.path.join(self.conf.lambdas_dir, projectname_region)
        self.project_zip_dir = os.path.join(self.conf.lambdas_dir,
                                            self.conf.sett['C_LAMBDAS_ZIP_DIR'] + "_" + self.conf.region)
        self.project_zip_file = os.path.join(self.project_zip_dir, projectname_region + ".zip")
        self.project_zip_file_without_ext = os.path.join(self.project_zip_dir, projectname_region)

# TODO -> ZIP (ALL / SPECIFIC) (local / remote)
# TODO -> SYNC ONLY STATUS (ALL / SPECIFIC)
# TODO -> SYNC FILES -> OVERWRITE LOCAL OR REMOTE (same that import and deploy?)
# TODO -> COMPARE MD5 (ALL / SPECIFIC)
# TODO -> IMPORT/DEPLOY WITH OVERWRITE OPTION
# TODO -> import from a .zip (only local, only deploy, both)
# TODO -> Change runtime
# TODO -> Copy project among regions
