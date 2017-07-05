#!/usr/bin/env python

import sys
import logger
from conf import Conf
from help import Help
from gateway import Gateway
from lambda_toolkit import __version__


class CLI:

    def __init__(self):
        self.log = logger.get_my_logger("CLI")
        self.log.info("Initializing lambda-toolkit CLI (v" + __version__ + ")")

    def main(self):
        if len(sys.argv) == 1:
            Help.print_help("")

        conf = Conf(".lambda-toolkit.cfg")
        gw = Gateway(sys.argv[1], sys.argv[2:])
        gw.do_action(conf).save_config()
