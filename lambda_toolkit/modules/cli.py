#!/usr/bin/env python

from conf import Conf
from queue import Queue
from project import Project
from utils import Utils
import click
import json
from lambda_toolkit import __version__


conf = Conf(".lambda-toolkit.cfg")

default_role = None
if 'C_DEFAULT_ROLE' in conf.sett:
    default_role = conf.sett['C_DEFAULT_ROLE']

def execute_cli(m_arg):
    Utils.click_validate_required_options(click.get_current_context(), conf)
    module = click.get_current_context().info_name
    myclass = __import__("lambda_toolkit.modules." + module)
    clazz = getattr(getattr(myclass.modules, module), module.title())
    getattr(clazz(conf, m_arg), m_arg['action'].replace("-", "") + "_" + module)().save_config()

@click.group()
@click.option('-v', '--version')
def cli(**kwargs):
    pass

@cli.command()
@click.argument('action', required=True, type=click.Choice(Utils.click_get_command_choice("queue", conf)))
@click.option('--sqsname', '-q', callback=Utils.click_append_fifo_in_queue, help="Define the queue.")
def queue(**kwargs):
    """Manage yours SQS Queues"""
    execute_cli(kwargs)


@cli.command()
@click.argument('action', required=True, type=click.Choice(Utils.click_get_command_choice("project", conf)))
@click.option( '--projectname', '-p', help="Define the project.")
@click.option('--rolename', '-r', default=default_role, callback=Utils.click_verify_role_exists,
              help="Define the role or try to get the default.")
@click.option('--runtime','-e', default="python2.7", help="Define runtime. (Default: Python2.7)",
                type=click.Choice(['python2.7', 'python3.6', 'nodejs6.10', 'nodejs4.3', 'nodejs4.3-edge']))
def project(**kwargs):
    """Manage yours lambda projects:"""
    execute_cli(kwargs)


print("Initializing lambda-toolkit CLI (v" + __version__ + ") - Region: " + conf.region)
cli()
