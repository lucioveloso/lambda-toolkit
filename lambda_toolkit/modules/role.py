#!/usr/bin/env python

import boto3
import logger


class Role:
    def __init__(self, conf, rolename):
        self.log = logger.get_my_logger("role")
        if rolename == "":
            self.log.critical("Parameter --rolename is required.")

        self.conf = conf
        self.rolename = rolename

    def verify_role_exists(self):
        client = boto3.client('iam')
        try:
            response = client.get_role(
                RoleName=self.rolename.split('/')[-1]
            )
            return True
        except Exception as e:
            self.log.debug(e)
            self.log.critical("The role '" + self.rolename + "' does not exist.")

        return False

    def set_default_role(self):
        if self.verify_role_exists():
            self.log.info("Role '" + self.rolename + "' is set as default now.")
            self.conf.config.set(self.conf.vars['C_CONFIG_SETTINGS'], 'C_DEFAULT_ROLE', self.rolename)
        return self.conf

    def unset_default_role(self):
        if 'C_DEFAULT_ROLE' in self.conf.vars:
            self.conf.config.remove_option(self.conf.vars['C_CONFIG_SETTINGS'], 'C_DEFAULT_ROLE')
            self.log.info("Unset the default role '" + self.conf.vars['C_DEFAULT_ROLE'] + "'.")
        return self.conf
