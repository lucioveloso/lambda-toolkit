#!/usr/bin/env python

import boto3
import os
from shutil import copy2
from shutil import rmtree
from shutil import make_archive
from utils import Utils
from zipfile import ZipFile
from urllib import urlretrieve
import logger


class Project:

    def __init__(self, conf, projectname):
        self.log = logger.get_my_logger("project")
        self.conf = conf
        if projectname != "":
            self.projectname = projectname
        else:
            self.log.critical("Parameter --projectname is required.")

        self.base_dir = os.path.join(os.path.expanduser('~'), self.conf.vars['C_BASE_DIR'])
        self.lambdas_dir = os.path.join(self.base_dir, self.conf.vars['C_LAMBDAS_DIR'])
        self.project_dir = os.path.join(self.lambdas_dir, self.projectname)
        self.project_zip_dir = os.path.join(self.lambdas_dir, self.conf.vars['C_LAMBDAS_ZIP_DIR'])
        self.project_zip_file = os.path.join(self.project_zip_dir, self.projectname + ".zip")
        self.project_zip_file_without_ext = os.path.join(self.project_zip_dir, self.projectname)

    def create_project(self):
        if Utils.validate_reserved_sections(self.conf, self.projectname):
            self.log.critical("Reserved name: " + self.projectname)

        if self.conf.config.has_section(self.projectname):
            self.log.critical("Project '" + self.projectname + "' already exists in lambda-toolkit.")
        else:
            self.create_project_folders()
            open(self.project_dir + "/__init__.py", 'a').close()
            # TODO: This C_LAMBDASTANDARD_FUNC should be placed in a dynamic place. (Templates in general)
            copy2(self.conf.vars['C_LAMBDASTANDARD_FUNC'], self.project_dir)
            self.log.info("Project " + self.projectname + " has been created.")
            self.conf.config.add_section(self.projectname)
            self.conf.config.set(self.projectname, "deployed", "False")

        return self.conf

    def delete_project(self):
        if Utils.validate_reserved_sections(self.conf, self.projectname):
            self.log.critical("Reserved name: " + self.projectname)

        if self.conf.config.has_section(self.projectname):
            self.conf = self.undeploy_project()
            self.conf.config.remove_section(self.projectname)
            if not os.path.exists(self.project_dir):
                self.log.warn("The folder '" + self.project_dir + "' does not exist. Ignoring folder removing.")
            else:
                rmtree(self.project_dir)
            self.log.info("Project '" + self.projectname + "' has been deleted.")
        else:
            self.log.critical("Project '" + self.projectname + "' does not exist.")

        return self.conf

    def import_project(self):
        if self.conf.config.has_section(self.projectname):
            self.log.critical("Project " + self.projectname + " already exists in your configuration.")

        lbs = boto3.client('lambda')

        try:
            lambda_function = lbs.get_function(FunctionName=self.projectname)
            self.create_project_folders();
            urlretrieve(lambda_function['Code']['Location'], self.project_zip_file)
            open(self.project_dir + "/__init__.py", 'a').close()
            zip_ref = ZipFile(self.project_zip_file, 'r')
            zip_ref.extractall(self.project_dir)
            zip_ref.close()
            self.conf.config.add_section(self.projectname)
            self.conf.config.set(self.projectname, "deployed", "True")
            self.log.info("Project " + self.projectname + " imported.")
        except Exception as e:
            self.log.error(str(e))
            self.log.critical("The project " + self.projectname + " does not exist in AWS environment.")

        return self.conf

    def deploy_project(self, rolename):
        rolename = Utils.define_lambda_role(self.conf, rolename)

        if not self.conf.config.has_section(self.projectname):
            self.log.critical("Project " + self.projectname + " does not exist.")

        lbs = boto3.client('lambda')

        make_archive(self.project_zip_file_without_ext, "zip", self.project_dir)

        try:
            lbs.get_function(FunctionName=self.projectname)
            replace = True
        except Exception:
            replace = False

        try:
            if replace:
                lbs.update_function_code(
                    FunctionName=self.projectname,
                    ZipFile=open(self.project_zip_file, "rb").read()
                )
                self.log.info("Lambda project " + self.projectname + " was redeployed.")
            else:
                lbs.create_function(
                    FunctionName=self.projectname,
                    Runtime='python2.7',
                    Role=rolename,
                    Handler='index.lambda_handler',
                    Description="Lambda project " + self.projectname + " deployed by lambda-proxy",
                    Code={
                        'ZipFile': open(self.project_zip_file, "rb").read()
                    }
                )
                self.log.info("Lambda project " + self.projectname + " was created and deployed.")

            self.conf.config.set(self.projectname, "deployed", "True")

        except Exception as e:
            self.log.error(str(e))
            self.log.critical("Failed to deploy the lambda project.")

        os.remove(self.project_zip_file)
        return self.conf


    def undeploy_project(self):
        if not self.conf.config.has_section(self.projectname):
            self.log.critical("Project '" + self.projectname + "' does not exist.")

        lbs = boto3.client('lambda')
        try:
            lbs.delete_function(FunctionName=self.projectname)
            self.log.info("Project '" + self.projectname + "' is now undeployed.")
        except Exception as e:
            self.log.warn("Project '" + self.projectname + "' is not deployed.")

        self.conf.config.set(self.projectname, "deployed", "False")

        return self.conf

    def create_project_folders(self):
        if not os.path.exists(self.base_dir):
            self.log.info("Creating the base lambda-toolkit folder: '" + self.base_dir + "'.")
            os.mkdir(self.base_dir)

        if not os.path.exists(self.lambdas_dir):
            self.log.info("Creating the lambda lambda-toolkit folder: '" + self.lambdas_dir + "'.")
            os.mkdir(self.lambdas_dir)

        if not os.path.exists(self.project_dir):
            self.log.info("Creating the project lambda-toolkit folder '" + self.project_dir + "'")
            os.mkdir(self.project_dir)

        if not os.path.exists(self.project_zip_dir):
            self.log.info("Creating the zip lambda-toolkit folder '" + self.project_zip_dir + "'")
            os.mkdir(self.project_zip_dir)