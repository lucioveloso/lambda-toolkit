#!/usr/bin/env python

import logger
import boto3
import pkgutil
import os


class Utils:

    def __init__(self):
        pass


    @staticmethod
    def docstring_parameter(*sub):
        def dec(obj):
            obj.__doc__ = pkgutil.get_data("lambda_toolkit", os.path.join(sub[0].sett['C_HELPS_FILES'], obj.func_name + ".txt"))
            #obj.__doc__ = "HELPAAAAAAA"
            return obj
        return dec

    @staticmethod
    def click_list_runtime():
        return ['python2.7', 'python3.6', 'nodejs6.10', 'nodejs4.3', 'nodejs4.3-edge']

    @staticmethod
    def click_get_command_choice(command, conf):
        opts = ['']
        if command in conf.cli:
            for opt in conf.cli[command]['commands']:
                opts.append(opt)

        return opts

    @staticmethod
    def click_validate_required_options(ctx,conf):
        if ctx.info_name in conf.cli:
            if ctx.params['action'] in conf.cli[ctx.info_name]['commands']:
                for check in conf.cli[ctx.info_name]['commands'][ctx.params['action']]:
                    if ctx.params[check] is None or ctx.params[check] is False:
                        print("The option '--" + check + "' is required");
                        exit(1)

    @staticmethod
    def click_list_queues_without_fifo(conf):
        opts = ['']
        for c in conf.queues.keys():
            if c.endswith(".fifo"):
                opts.append(c.replace(".fifo", ""))
            else:
                opts.append(c)
        return opts


    @staticmethod
    def click_append_fifo_in_queue(ctx, param, value):
        if value is None:
            return None
        elif value.endswith(".fifo"):
            return value
        else:
            return value + ".fifo"

    @staticmethod
    def click_verify_role_exists(ctx, param, value):
        if value is None:
            return None
        client = boto3.client('iam')
        try:
            response = client.get_role(
                RoleName=value.split('/')[-1]
            )
            return value
        except Exception as e:
            logger.get_my_logger("utils").debug(e)
            logger.get_my_logger("utils").critical("The role '" + value + "' does not exist.")

        return None

    @staticmethod
    def get_default_role(conf):
        if 'C_DEFAULT_ROLE' not in conf.sett:
            return None
        else:
            return conf.sett['C_DEFAULT_ROLE']
