import json
from abc import ABC, abstractmethod
from typing import Type, TYPE_CHECKING

import click

from ..renderers import format_full_table
from .configurations import ReboticsScriptsConfiguration

if TYPE_CHECKING:
    from rebotics_sdk.providers import ReboticsBaseProvider


class BaseReboticsCLIContext(ABC):
    def __init__(self,
                 format: str,
                 verbose: bool,
                 api_verbosity: int,
                 provider_class: Type['ReboticsBaseProvider'],
                 click_context: click.Context):
        self.format = format
        self.verbose = verbose
        self.api_verbosity = api_verbosity
        self.provider_class = provider_class
        self.click_context = click_context

    @property
    @abstractmethod
    def provider(self) -> 'ReboticsBaseProvider':
        ...

    def format_result(self, items, max_column_length=30, keys_to_skip=None, force_format=None):
        force_format = force_format if force_format else self.format
        if force_format == 'json':
            click.echo(json.dumps(items, indent=2))
        elif force_format == 'id':
            click.echo(" ".join([str(item.get('id')) for item in items]))
        else:
            format_full_table(items, max_column_length=max_column_length, keys_to_skip=keys_to_skip)

    def verbose_log(self, message: str) -> None:
        if self.verbose:
            click.echo(message)

    def do_progress_bar(self) -> bool:
        return self.format not in ('id', 'json')


class ReboticsCLINoConfigContext(BaseReboticsCLIContext):
    def __init__(self,
                 host: str,
                 format: str,
                 verbose: bool,
                 api_verbosity: int,
                 provider_class: Type['ReboticsBaseProvider'],
                 click_context: click.Context):
        super().__init__(format, verbose, api_verbosity, provider_class, click_context)
        self.host = host

    @property
    def provider(self) -> 'ReboticsBaseProvider':
        return self.provider_class(host=self.host, api_verbosity=self.api_verbosity)


class ReboticsCLIContext(BaseReboticsCLIContext):
    configuration_class = ReboticsScriptsConfiguration

    def __init__(self,
                 command: str,
                 role: str,
                 format: str,
                 verbose: bool,
                 api_verbosity: int,
                 config_path: str,
                 provider_class: Type['ReboticsBaseProvider'],
                 click_context: click.Context):
        super().__init__(format, verbose, api_verbosity, provider_class, click_context)
        self.command = command
        self.role = role
        self.config_path = config_path
        self.verbose_log(f"Config path: {self.config_path}")
        self.config_provider = self.configuration_class(self.config_path, self.provider_class)
        self.config = self.config_provider.config

    @property
    def provider(self) -> 'ReboticsBaseProvider':
        provider = self.config_provider.get_provider(self.role, self.api_verbosity)

        if provider is None:
            raise click.ClickException(
                f'Role {self.role} is not configured.\n'
                f'Run: \n{self.command} -r {self.role} configure'
            )
        return provider

    def update_configuration(self, **configuration):
        self.config_provider.update_configuration(self.role, **configuration)


pass_rebotics_context = click.make_pass_decorator(ReboticsCLIContext, True)
pass_rebotics_no_config_context = click.make_pass_decorator(ReboticsCLINoConfigContext, True)
