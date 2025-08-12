import json
import logging
import os
from typing import Type, Optional, TYPE_CHECKING

import click

from rebotics_sdk import RetailerProvider
from rebotics_sdk.utils import mkdir_p

if TYPE_CHECKING:
    from rebotics_sdk.providers import ReboticsBaseProvider

app_dir = click.get_app_dir('rebotics-scripts')
try:
    mkdir_p(app_dir)
except PermissionError:
    logging.warning(
        "Failed to create click app directory. Please make sure that you have write access to the home directory"
    )


class DumpableConfiguration(object):
    def __init__(self, path):
        self.path = path

    @property
    def filepath(self):
        return os.path.expanduser(self.path)

    @property
    def config(self):
        try:
            with open(self.filepath, 'r') as config_buffer:
                return json.load(config_buffer)
        except FileNotFoundError:
            self.config = {}
            return {}
        except (json.JSONDecodeError,):
            return {}

    @config.setter
    def config(self, value):
        with open(self.filepath, 'w') as config_buffer:
            json.dump(value, config_buffer, indent=2)

    def update_configuration(self, key, **configuration):
        current_configuration = self.config
        if key not in current_configuration:
            current_configuration[key] = configuration
        else:
            current_configuration[key].update(configuration)
        self.config = current_configuration


class ReboticsScriptsConfiguration(DumpableConfiguration):
    def __init__(self, path, provider_class: Type['ReboticsBaseProvider'] = RetailerProvider):
        super(ReboticsScriptsConfiguration, self).__init__(path)
        self.provider_class = provider_class

    def get_provider(self, key: str, api_verbosity: int = 0, is_async: bool = False) -> Optional['ReboticsBaseProvider']:
        config = self.config.get(key, None)
        if config is None:
            return None

        provider_kwargs = {
            'host': config['host'],
            'role': key,
            'api_verbosity': api_verbosity,
            'is_async': is_async,
        }
        if 'token' in config:
            provider_kwargs['token'] = config['token']

        return self.provider_class(**provider_kwargs)

    def list_roles(self):
        return self.config.keys()


states = DumpableConfiguration(os.path.join(app_dir, 'command_state.json'))


def read_saved_role(command_name: str) -> Optional[str]:
    roles = states.config.get('roles')
    if roles is None:
        return None
    role = roles.get(command_name)
    return role


def process_role(ctx: click.Context, role: Optional[str], command_name: str) -> None:
    if not role:
        if ctx.invoked_subcommand != 'roles':
            raise click.ClickException(
                'You have not specified role to use. Use `roles` sub command to see which roles are available'
            )
    else:
        states.update_configuration('roles', **{command_name: role})
