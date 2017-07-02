#!/usr/bin/env python


import sys
import os
from modules.conf import Conf
from modules.help import Help
from modules.gateway import Gateway

sys.dont_write_bytecode = True


if __name__ == "__main__":
    if len(sys.argv) == 1:
        Help.print_help("")

    conf = Conf(".lambda-toolkit.cfg")
    gw = Gateway(sys.argv[1], sys.argv[2:])
    gw.do_action(conf).save_config()
