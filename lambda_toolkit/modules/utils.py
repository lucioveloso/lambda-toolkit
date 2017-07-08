#!/usr/bin/env python

import logger
import boto3

class Utils:

    def __init__(self):
        pass

    @staticmethod
    def click_get_command_choice(command, conf):
        opts = ['']
        if command in conf.cli:
            for opt in conf.cli[command]:
                opts.append(opt)

        return opts

    @staticmethod
    def click_validate_required_options(ctx,conf):
        if ctx.info_name in conf.cli:
            if ctx.params['action'] in conf.cli[ctx.info_name]:
                for check in conf.cli[ctx.info_name][ctx.params['action']]:
                    if ctx.params[check] is None or ctx.params[check] is False:
                        print("The option '--" + check + "' is required");
                        exit(1)

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
