#!/usr/bin/env python

from conf import Conf
from utils import Utils
import click
from lambda_toolkit import __version__
import sys

def execute_cli(args):
    Utils.click_validate_required_options(click.get_current_context(), conf)
    module = click.get_current_context().info_name
    myclass = __import__("lambda_toolkit.modules." + module)
    clazz = getattr(getattr(myclass.modules, module), module.title())
    getattr(clazz(conf, args), args['action'].replace("-", "_") + "_" + module)().save_config()

@click.group()
def cli(**kwargs):
    pass

if len(sys.argv) > 1 and sys.argv[1] == "tail":
    import tail_toolkit.modules.cli

conf = Conf()

@cli.command()
@click.argument('action', required=True, type=click.Choice(Utils.click_get_command_choice("queue", conf)))
@click.option('--sqsname', '-q', callback=Utils.click_append_fifo_in_queue, help="Define the queue.")
@Utils.docstring_parameter(conf)
def queue(**kwargs):
    execute_cli(kwargs)

@cli.command()
@click.argument('action', required=True, type=click.Choice(Utils.click_get_command_choice("proxy", conf)))
@click.option('--proxyname', '-p', help="Define the proxy name.")
@click.option('--sqsname', '-q', callback=Utils.click_append_fifo_in_queue, help="Define the queue name.",
              type=click.Choice(Utils.click_list_queues_without_fifo(conf)))
@click.option('--rolename', '-r', default=Utils.get_default_role(conf), callback=Utils.click_verify_role_exists,
              help="Define the role or try to get the default.")
@click.option('--runtime','-e', default="python2.7", help="Define runtime. (Default: Python2.7)",
              type=click.Choice(Utils.click_list_runtime()))
@Utils.docstring_parameter(conf)
def proxy(**kwargs):
    execute_cli(kwargs)

@cli.command()
@click.argument('action', required=True, type=click.Choice(Utils.click_get_command_choice("project", conf)))
@click.option( '--projectname', '-p', help="Define the project.")
@click.option('--rolename', '-r', default=Utils.get_default_role(conf), callback=Utils.click_verify_role_exists,
              help="Define the role or try to get the default.")
@click.option('--runtime','-e', default="python2.7", help="Define runtime. (Default: Python2.7)",
              type=click.Choice(Utils.click_list_runtime()))
@Utils.docstring_parameter(conf)
def project(**kwargs):
    execute_cli(kwargs)

@cli.command()
@click.argument('action', required=True, type=click.Choice(Utils.click_get_command_choice("role", conf)))
@click.option('--rolename', '-r', default=Utils.get_default_role(conf),
              help="Define the role or try to get the default.")
@Utils.docstring_parameter(conf)
def role(**kwargs):
    execute_cli(kwargs)

@cli.command()
def tail(**kwargs):
    """Forward to tail-toolkit"""
    pass

print("Initializing lambda-toolkit CLI (v" + __version__ + ") - Region: " + conf.region)
cli()
