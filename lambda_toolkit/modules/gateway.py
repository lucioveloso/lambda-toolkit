#!/usr/bin/env python

import getopt
from help import Help
from queue import Queue
from project import Project
from ltklambdaproxy import Ltklambdaproxy
from receiver import Receiver
from role import Role
from utils import Utils
from tail import Tail
import logger


class Gateway:

    projectname = ""
    sqsname = ""
    lambdaname = ""
    rolename = ""

    def __init__(self, action, args):
        self.log = logger.get_my_logger("gateway")
        self.action = action
        self.get_args(args)

    def get_args(self, args):
        try:
            opts, args = getopt.getopt(args, "p:q:l:r:",
                                       ["projectname=", "sqsname=", "lambdaname=", "rolename="])
        except getopt.GetoptError:
            Help.print_help("Getopterror")
            exit(1)
        for opt, arg in opts:
            if opt in ("-p", "--projectname"):
                self.projectname = arg
            elif opt in ("-q", "--sqsname"):
                self.sqsname = Utils.append_fifo_in_queue(arg)
            elif opt in ("-r", "--rolename"):
                self.rolename = arg
            elif opt in ("-l", "--lambdaname"):
                self.lambdaname = arg

    def do_action(self, conf):
        if self.action == "create-project":
            return Project(conf, self.projectname).create_project()
        elif self.action == "delete-project":
            return Project(conf, self.projectname).delete_project()
        elif self.action == "list":
            conf.list_config()
        elif self.action == "create-sqs":
            return Queue(conf, self.sqsname).create_queue()
        elif self.action == "delete-sqs":
            return Queue(conf, self.sqsname).delete_queue()
        elif self.action == "purge-sqs":
            Queue(conf, self.sqsname).purge_queue()
        elif self.action == "deploy-project":
            return Project(conf, self.projectname).deploy_project(self.rolename)
        elif self.action == "import-project":
            return Project(conf, self.projectname).import_project()
        elif self.action == "import-all-projects":
            return Project(conf, "bypassvalidator").import_all_projects()
        elif self.action == "deploy-all-projects":
            return Project(conf, "bypassvalidator").deploy_all_projects(self.rolename)
        elif self.action == "undeploy-project":
            return Project(conf, self.projectname).undeploy_project()
        elif self.action == "deploy-lambda-proxy":
            return Ltklambdaproxy(conf, self.lambdaname).deploy_lambda_proxy(self.rolename, self.sqsname)
        elif self.action == "undeploy-lambda-proxy":
            return Ltklambdaproxy(conf, self.lambdaname).undeploy_lambda_proxy()
        elif self.action == "receiver":
            try:
                Receiver(conf, self.sqsname, self.projectname).receiver()
            except KeyboardInterrupt:
                self.log.info("Stopping the receiver.")
        elif self.action == "tail":
            try:
                Tail(conf, self.lambdaname).tail_log()
            except KeyboardInterrupt:
                self.log.info("Stopping the tail.")
        elif self.action == "set-default-role":
            return Role(conf, self.rolename).set_default_role()
        elif self.action == "unset-default-role":
            return Role(conf, "bypassvalidator").unset_default_role()
        elif self.action == "create-star":
            Utils.define_lambda_role(conf, self.rolename)
            queue_name = Utils.append_fifo_in_queue(self.projectname + "_queue")
            conf = Project(conf, self.projectname).create_project()
            conf = Queue(conf, queue_name).create_queue()
            conf = Ltklambdaproxy(conf, self.projectname + "_proxy").deploy_lambda_proxy(self.rolename, queue_name)
            return Project(conf, self.projectname).deploy_project(self.rolename)
        elif self.action == "delete-all-configuration":
            conf.delete_all_config()
        else:
            Help.print_help("Invalid command")

        return conf
