#!/usr/bin/env python

from lambda_toolkit.modules.utils import Utils

class Role:
    def __init__(self, conf, kwargs):
        self.log = conf.log
        self.conf = conf
        self.rolename = kwargs['rolename']

    def set_default_role(self):
        Utils.click_verify_role_exists(None, None, self.rolename)

        if Utils.click_verify_role_exists(None, None, self.rolename):
            self.log.info("Role '" + self.rolename + "' is set as default now.")
            self.conf.sett['C_DEFAULT_ROLE'] = self.rolename
        return self.conf

    def unset_default_role(self):
        if self.conf.sett['C_DEFAULT_ROLE'] is not None:
            self.log.info("Unset the default role '" + self.conf.sett['C_DEFAULT_ROLE'] + "'.")
            self.conf.sett['C_DEFAULT_ROLE'] = ""
        else:
            self.log.warn("There isn't a default role configured.")

        return self.conf
