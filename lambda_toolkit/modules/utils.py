#!/usr/bin/env python

import lambda_toolkit.modules.logger as logger
import boto3
import pkgutil
import os
import sys


class Utils:

    def __init__(self):
        pass

    @staticmethod
    def fixpath(path):
        path = os.path.normpath(os.path.expanduser(path))
        if path.startswith("\\"):
            return "C:" + path
        return path

    @staticmethod
    def docstring_parameter(*sub):
        def dec(obj):
            obj.__doc__ = pkgutil.get_data("lambda_toolkit", os.path.join(sub[0].sett['C_HELPS_FILES'], obj.__name__ + ".txt"))
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
    def click_list_event_files(conf):
        opts = ['']
        for f in os.listdir(os.path.join(os.path.expanduser(conf.sett['C_BASE_DIR']), conf.sett['C_INVOKE_DIR_EVT'])):
            opts.append(f)
        return opts


    @staticmethod
    def click_validate_required_options(ctx,conf):
        if ctx.info_name in conf.cli:
            if ctx.params['action'] in conf.cli[ctx.info_name]['commands']:
                for check in conf.cli[ctx.info_name]['commands'][ctx.params['action']]:
                    if sys.version_info[0] == 3:
                        instance_type = str
                    else:
                        instance_type = unicode
                    if isinstance(check, instance_type):
                        # For single parameters
                        c = check.replace("-", "_")
                        if ctx.params[c] is None:
                            logger.get_my_logger("Utils").critical("The option '--" + check + "' is required");
                    elif isinstance(check, list):
                        # At least one parameter in the list should be informed (combined)
                        find = False
                        for c in check:
                            c = c.replace("-", "_")
                            if c in ctx.params and ctx.params[c] is not None:
                                find = True
                                break
                        if find:
                            continue
                        logger.get_my_logger("Utils").critical("One of those parameters should be included: " + ', '.join(map(str, check)))
                    else:
                        logger.get_my_logger("Utils").critical("Invalid cli conf file in: " + check)


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
    def check_kwargs(kwargs, value):
        if value in kwargs and kwargs[value] is not None:
            return True

        return False

    @staticmethod
    def click_verify_role_exists(ctx, param, value):
        if value == "":
            return None
        client = boto3.client('iam')
        try:
            response = client.get_role(
                RoleName=value.split('/')[-1]
            )
            return value
        except Exception as e:
            logger.get_my_logger("Utils").debug(e)
            logger.get_my_logger("Utils").critical("The role '" + value + "' does not exist.")

        return None
