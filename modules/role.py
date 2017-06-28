class Role:
    def __init__(self, conf, rolename):
        self.conf = conf
        self.rolename = rolename

    def set_default_role(self):
        print("Role '" + self.rolename + "' is set as default now.")
        self.conf.config.set(self.conf.vars['C_CONFIG_SETTINGS'], 'C_DEFAULT_ROLE', self.rolename)
