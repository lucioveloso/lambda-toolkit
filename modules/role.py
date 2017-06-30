import logger


class Role:
    def __init__(self, conf, rolename):
        self.log = logger.get_my_logger("role")
        self.conf = conf
        self.rolename = rolename

    def set_default_role(self):
        self.log.info("Role '" + self.rolename + "' is set as default now.")
        self.conf.config.set(self.conf.vars['C_CONFIG_SETTINGS'], 'C_DEFAULT_ROLE', self.rolename)
