#!/usr/bin/env python


class Help:

    def __init__(self):
        pass

    @staticmethod
    def print_help(msg):
        print("lambda-toolkit usage:")
        print(" * List projects:                 lt list")
        print(" * Add SQS:                       lt create-sqs [-q] --sqsname <queuename>")
        print(" * Delete SQS:                    lt delete-sqs [-q] --sqsname <queuename>")
        print(" * Purge SQS:                     lt purge-sqs [-q] --sqsname <queuename>")
        print(" * Deploy Lambda Proxy:           lt deploy-lambda-proxy [-l] --lambdaname "
              + "<lambdaname> [-q] --sqsname <queuename> [-r] --rolename <rolename>")
        print(" * Undeploy Lambda proxy:         lt undeploy-lambda-proxy [-l] --lambdaname <lambdaname>")
        print(" * Create a new lambda project:   lt create-project [-p] --projectname <projectname>")
        print(" * Delete a lambda project:       lt delete-project [-p] --projectname <projectname>")
        print(" * Deploy a lambda project:       lt deploy-project [-p] --projectname <projectname>"
              "[-r] --rolename <rolename>")
        print(" * Deploy all lambda projects:    lt deploy-all-projects [-r] --rolename <rolename>")
        print(" * Undeploy a lambda project:     lt undeploy-project [-p] --projectname <projectname>")
        print(" * Import a lambda project:       lt import-project [-p] --projectname <projectname>")
        print(" * Import all lambda projects:    lt import-all-projects")
        print(" * Set a default role to lambdas: lt set-default-role [-r] --rolename <rolename> ")
        print(" * Delete the default role:       lt unset-default-role")
        print("")
        print(" * Create star (All)              lt create-star [-p] --projectname <projectname> [-r] --rolename <rolename>")
        print(" * Remove all proxies and queues  lt delete-all-configuration")
        print(" * Tail lambda function logs      lt tail [-l] --lambdaname <lambdaname>")
        print(" * Receive and Process queue:     lt receiver [-p] --projectname <projectname> [-q]"
              + "--sqsname <queuename>")
        print(msg)
        exit(1)
