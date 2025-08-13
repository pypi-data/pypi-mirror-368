import click
import toml

from pathlib import Path

from . import cli, msg


@cli.group('config', help='Manage ts-scan configuration')
def config():
    pass


@config.command('set', help='Unset a configuration option')
@cli.api_default_options(is_project_name_required=False)
@click.pass_context
def set_config(ctx, **kwargs):
    pass


@config.command('unset', help='Set a configuration option')
@cli.api_default_options(is_project_name_required=False)
@click.pass_context
def unset_config(ctx, **kwargs):
    pass

