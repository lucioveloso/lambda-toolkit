#!/usr/bin/env python

import logger


class Utils:

    def __init__(self):
        pass

    @staticmethod
    def get_list_config(conf, section, attr):
        if conf.config.has_section(section):
            if conf.config.has_option(section, attr):
                l = conf.config.get(section, attr)
                if l != "":
                    return l.split(",")
        else:
            conf.config.add_section(section)

        return []

    @staticmethod
    def append_fifo_in_queue(queuename):
        if queuename.endswith(".fifo"):
            return queuename
        else:
            return queuename + ".fifo"

    @staticmethod
    def validate_reserved_sections(conf, p):
        if (p == conf.vars['C_CONFIG_SQS'] or p == conf.vars['C_CONFIG_SQS_QUEUES']
           or p == conf.vars['C_CONFIG_LAMBDAPROXY'] or p == conf.vars['C_CONFIG_SETTINGS']):
            return True

        return False

    @staticmethod
    def define_lambda_role(conf, rolename):
        if rolename == "":
            if 'C_DEFAULT_ROLE' in conf.vars:
                rolename = conf.vars['C_DEFAULT_ROLE']
                logger.get_my_logger("utils").info("Using the default lambda role: " + rolename)
            else:
                logger.get_my_logger("utils").critical("Parameter --rolename or set a default-role is required.")

        return rolename
