#!/usr/bin/env python

from lambda_toolkit.modules.conf import Conf
from lambda_toolkit.modules.utils import Utils
import click
from lambda_toolkit import __version__
import sys


if len(sys.argv) > 1:
    if sys.argv[1] == "tail":
        # External modudle
        import tail_toolkit.modules.cli
else:
    sys.argv[0] == "--help"

def execute_cli(args):
    Utils.click_validate_required_options(click.get_current_context(), conf)
    module = click.get_current_context().info_name
    myclass = __import__("lambda_toolkit.modules." + module)
    clazz = getattr(getattr(myclass.modules, module), module.title())
    getattr(clazz(conf, args), args['action'].replace("-", "_") + "_" + module)().save_config()

conf = Conf()

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(**kwargs):
    pass



@cli.command()
@click.argument('action', required=True, type=click.Choice(Utils.click_get_command_choice("queue", conf)))
@click.option('--sqsname', '-q', callback=Utils.click_append_fifo_in_queue, help="Define the queue.")
@click.option('--region', '-R', type=click.Choice(conf.aws_regions), help="Define the optional region.")
@Utils.docstring_parameter(conf)
def queue(**kwargs):
    execute_cli(kwargs)

@cli.command()
@click.argument('action', required=True, type=click.Choice(Utils.click_get_command_choice("proxy", conf)))
@click.option('--proxyname', '-p', help="Define the proxy name.")
@click.option('--sqsname', '-q', callback=Utils.click_append_fifo_in_queue, help="Define the queue name.",
              type=click.Choice(Utils.click_list_queues_without_fifo(conf)))
@click.option('--rolename', '-r', default=conf.sett['C_DEFAULT_ROLE'], callback=Utils.click_verify_role_exists,
              help="Define the role or try to get the default.")
@click.option('--runtime','-e', default="python2.7", help="Define runtime. (Default: Python2.7)",
              type=click.Choice(Utils.click_list_runtime()))
@click.option('--region', '-R', type=click.Choice(conf.aws_regions), help="Define the optional region.")
@Utils.docstring_parameter(conf)
def proxy(**kwargs):
    execute_cli(kwargs)

@cli.command()
@click.argument('action', required=True, type=click.Choice(Utils.click_get_command_choice("project", conf)))
@click.option( '--projectname', '-p', help="Define the project.")
@click.option('--rolename', '-r', default=conf.sett['C_DEFAULT_ROLE'], callback=Utils.click_verify_role_exists,
              help="Define the role or try to get the default.")
@click.option('--runtime','-e', default="python2.7", help="Define runtime. (Default: Python2.7)",
              type=click.Choice(Utils.click_list_runtime()))
@click.option('--region', '-R', type=click.Choice(conf.aws_regions), help="Define the optional region.")
@Utils.docstring_parameter(conf)
def project(**kwargs):
    execute_cli(kwargs)

@cli.command()
@click.argument('action', required=True, type=click.Choice(Utils.click_get_command_choice("role", conf)))
@click.option('--rolename', '-r',
              help="Define the role or try to get the default.")
@Utils.docstring_parameter(conf)
def role(**kwargs):
    execute_cli(kwargs)

@cli.command()
@click.argument('action', required=True, type=click.Choice(Utils.click_get_command_choice("receiver", conf)))
@click.option('--sqsname', '-q', callback=Utils.click_append_fifo_in_queue, help="Define the queue name.",
              type=click.Choice(Utils.click_list_queues_without_fifo(conf)))
@click.option( '--projectname', '-p', help="Define the project.", type=click.Choice(conf.projects.keys()))
@Utils.docstring_parameter(conf)
def receiver(**kwargs):
    execute_cli(kwargs)

@cli.command()
@click.argument('action', required=True, type=click.Choice(Utils.click_get_command_choice("invoke", conf)))
@Utils.docstring_parameter(conf)
@click.option( '--projectname', '-p', help="Define the project.", type=click.Choice(conf.projects.keys()))
@click.option( '--event-file', '-f', help="Define a file.",
               type=click.Choice(Utils.click_list_event_files(conf)))
@click.option( '--proxyname', '-pp', help="Define the proxy.", type=click.Choice(conf.proxies.keys()))
def invoke(**kwargs):
    execute_cli(kwargs)

@cli.command()
def tail(**kwargs):
    """Forward to tail-toolkit"""
    pass

@cli.command()
@Utils.docstring_parameter(conf)
def list(**kwargs):
    modules = ['project', 'queue', 'proxy']

    for m in modules:
        conf.log.info("")
        myclass = __import__("lambda_toolkit.modules." + m)
        args = {}
        args['action'] = "list"
        clazz = getattr(getattr(myclass.modules, m), m.title())
        getattr(clazz(conf, args), args['action'].replace("-", "_") + "_" + m)().save_config()


print("Initializing lambda-toolkit CLI (v" + __version__ + ") - Region: " + conf.region + " - Auth: " + conf.auth_mode)
cli()
