#!/usr/bin/env python

import boto3
import logger
from utils import Utils

class Role:
    def __init__(self, conf, rolename):
        self.log = logger.get_my_logger("role")
        if rolename == "":
            self.log.critical("Parameter --rolename is required.")

        self.conf = conf
        self.rolename = rolename

    def set_default_role(self):
        if Utils.verify_role_exists(self.rolename):
            self.log.info("Role '" + self.rolename + "' is set as default now.")
            self.conf.config.set(self.conf.vars['C_CONFIG_SETTINGS'], 'C_DEFAULT_ROLE', self.rolename)
        return self.conf

    def unset_default_role(self):
        if 'C_DEFAULT_ROLE' in self.conf.vars:
            self.conf.config.remove_option(self.conf.vars['C_CONFIG_SETTINGS'], 'C_DEFAULT_ROLE')
            self.log.info("Unset the default role '" + self.conf.vars['C_DEFAULT_ROLE'] + "'.")
        return self.conf
