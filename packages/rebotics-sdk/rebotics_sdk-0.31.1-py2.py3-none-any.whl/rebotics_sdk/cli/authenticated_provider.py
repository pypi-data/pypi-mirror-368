import pathlib

try:
    import click
except ImportError:
    raise Exception("To use authenticated role provider you have to install rebotics_sdk[shell]")

from rebotics_sdk.cli.utils import app_dir, ReboticsScriptsConfiguration

from rebotics_sdk.providers import (
    RetailerProvider, CvatProvider, AdminProvider, DatasetProvider, FVMProvider, HawkeyeProvider, ReboticsBaseProvider
)

PROVIDER_NAME_TO_CLASS = {
    'retailer': RetailerProvider,
    'cvat': CvatProvider,
    'admin': AdminProvider,
    'dataset': DatasetProvider,
    'fvm': FVMProvider,
    'hawkeye': HawkeyeProvider,
}


class AuthenticatedRoleProvider:
    def __init__(self, application_directory=None):
        if application_directory is None:
            # we can force to use /var/lib/rebotics_sdk/ as application directory for example
            application_directory = app_dir
        self.app_path = pathlib.Path(application_directory)
        assert self.app_path.exists(), "App path from cli should exist and be available"

    def get_provider(self, provider_name, role, provider_class=None, is_async=False):
        config_provider = ReboticsScriptsConfiguration(
            self.app_path / f"{provider_name}.json",
            self.get_provider_class(provider_name, provider_class)
        )
        return config_provider.get_provider(role, is_async=is_async)

    @staticmethod
    def get_provider_class(provider_name, provider_class=None):
        if provider_class is None:
            return PROVIDER_NAME_TO_CLASS[provider_name]

        assert issubclass(
            provider_class,
            ReboticsBaseProvider
        ), "Provider class should be subclass of ReboticsBaseProvider"

        return provider_class

    def list_roles(self, provider_name):
        config_provider = ReboticsScriptsConfiguration(
            self.app_path / f"{provider_name}.json",
            PROVIDER_NAME_TO_CLASS[provider_name]
        )
        return config_provider.list_roles()

    def add_role(self, provider_name, role, host, token):
        assert provider_name in PROVIDER_NAME_TO_CLASS, f"Unknown provider name {provider_name}"

        config_provider = ReboticsScriptsConfiguration(
            self.app_path / f"{provider_name}.json",
            self.get_provider_class(provider_name)
        )
        config_provider.update_configuration(
            role, host=host, token=token
        )


def get_provider(provider_name, role, provider_class=None, is_async=False):
    """
    get authenticated provider for given role.
    Intendent to be used in scripts provided by the rebotics team.

    :param provider_name: name of the provider. One of: retailer, cvat, admin, dataset, fvm, hawkeye
    :param role: role to use for authentication
    :param provider_class: optional. Can be used to specify provider directly
    :param is_async: optional. If True, the provider will use async HTTP requests with httpx (requires rebotics_sdk[async])

    General usage:
    >>> from rebotics_sdk import get_provider
    >>> admin = get_provider('admin', 'r3dev')
    >>> admin.version()

    Async usage:
    >>> import asyncio
    >>> from rebotics_sdk import get_provider
    >>> async def main():
    ...     admin = get_provider('admin', 'r3dev', is_async=True)
    ...     version = await admin.version()
    ...     print(version)
    >>> asyncio.run(main())
    """
    return AuthenticatedRoleProvider().get_provider(provider_name, role, provider_class, is_async)
