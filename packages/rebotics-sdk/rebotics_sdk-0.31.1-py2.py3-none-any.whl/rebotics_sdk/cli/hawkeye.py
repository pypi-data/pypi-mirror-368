import os
import pathlib
from typing import List

import click

from rebotics_sdk.advanced.flows import PresignedURLFileUploader, FileUploadError
from rebotics_sdk.cli.common import configure, shell, roles, set_token
from rebotics_sdk.cli.utils import (
    read_saved_role, process_role, ReboticsCLIContext, ReboticsCLINoConfigContext, app_dir, pass_rebotics_context,
    pass_rebotics_no_config_context,
)
from rebotics_sdk.constants import CameraGroupActionStatusType
from rebotics_sdk.providers import ProviderHTTPServiceException
from rebotics_sdk.providers.hawkeye import HawkeyeProvider, HawkeyeCameraProvider


@click.group()
@click.option('--api-verbosity', default=0, type=click.IntRange(0, 3), help='Display request detail')
@click.option('-h', '--host', required=True, type=click.STRING, help='Hawkeye App Host')
@click.option('-f', '--format', default='table', type=click.Choice(['table', 'id', 'json']), help='Result rendering')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.version_option()
@click.pass_context
def hawkeye_camera(ctx, host: str, format: str, verbose: bool, api_verbosity: int):
    """
    Admin CLI tool to communicate with Public Hawkeye API for cameras without authorization
    """
    ctx.obj = ReboticsCLINoConfigContext(
        host,
        format,
        verbose,
        api_verbosity,
        provider_class=HawkeyeCameraProvider,
        click_context=ctx,
    )


@hawkeye_camera.command(name='heartbeat')
@click.option('-c', '--camera', required=True, help='Shelf Camera Token to save its heartbeat data',
              type=click.STRING)
@click.option('-b', '--battery', required=True, help='Battery status of the camera', type=click.FLOAT)
@click.option('-w', '--wifi-signal', 'wifi_signal', required=True, help='Wi-Fi Signal Strength of the Camera',
              type=click.FLOAT)
@click.option('-t', '--time', 'time', required=True, help='Current time', type=click.STRING)
@pass_rebotics_no_config_context
def create_camera_heartbeat(ctx, camera: str, battery: float, wifi_signal: float, time: str):
    """
    Saves camera heartbeat data and returns the camera's list of actions
    Usage:
        hawkeye_camera -h https://hawkeye.rebotics.net heartbeat -c "token" -b 0.6 -w 0.9 -t 2023-09-15T09:13:00.583Z
    """
    ctx.verbose_log('Calling create camera heartbeat')
    try:
        result = ctx.provider.save_camera_heartbeat(camera, battery, wifi_signal, time)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))

    ctx.format_result(result)


@hawkeye_camera.command()
@click.argument('filepath', type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path))
@click.option('-c', '--camera', required=True, help='Shelf Camera Token', type=click.STRING)
@pass_rebotics_no_config_context
def create_capture(ctx, filepath: pathlib.Path, camera: str):
    """
    Usage:
        hawkeye_camera -h https://hawkeye.rebotics.net create-capture "image.jpg" -c "token"
    """
    filename = filepath.name
    ctx.verbose_log('Calling create capture presigned url')
    try:
        response = ctx.provider.create_capture_url(camera, filename)
        destination = response['destination']
        file_key = response['file_key']

        file_uploader = PresignedURLFileUploader(destination)
        with open(filepath, 'rb') as file_io:
            file_uploader.upload(file_io, filename=filename)

        ctx.verbose_log('Calling create capture API')
        ctx.provider.create_capture(camera, file_key)
    except (ProviderHTTPServiceException, FileUploadError) as exc:
        raise click.ClickException(str(exc))

    click.echo('Capture created successfully')


@click.group()
@click.option('--api-verbosity', default=0, type=click.IntRange(0, 3), help='Display request detail')
@click.option('-f', '--format', default='table', type=click.Choice(['table', 'id', 'json']), help='Result rendering')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-c', '--config', type=click.Path(), default='hawkeye.json', help="Specify what config.json to use")
@click.option('-r', '--role', default=lambda: read_saved_role('hawkeye'), help="Key to specify what hawkeye to use")
@click.version_option()
@click.pass_context
def api(ctx, format, verbose, config, role, api_verbosity):
    """
    Admin CLI tool to communicate with Hawkeye API
    """
    process_role(ctx, role, 'hawkeye')
    ctx.obj = ReboticsCLIContext(
        'hawkeye',
        role,
        format,
        verbose,
        api_verbosity,
        os.path.join(app_dir, config),
        provider_class=HawkeyeProvider,
        click_context=ctx,
    )


@api.command(name='fixture')
@click.option('-i', '--store', required=True, help='Store ID of a fixture', type=click.STRING)
@click.option('-a', '--aisle', required=False, help='Aisle of a fixture', type=click.STRING)
@click.option('-s', '--section', required=False, help='Section of a fixture', type=click.STRING)
@click.option('-p', '--planogram', required=False, help='Planogram of a fixture', type=click.STRING)
@click.option('-c', '--category', required=False, help='Category of a fixture', type=click.STRING)
@click.option('--camera', required=False, help='Camera ID of the Shelf Camera', type=click.INT)
@pass_rebotics_context
def create_fixture(ctx, store, aisle, section, planogram, category, camera):
    """Saves Fixture object and returns"""
    try:
        if ctx.verbose:
            click.echo('Calling create fixture')
        result = ctx.provider.save_fixture(
            store_id=store,
            aisle=aisle,
            section=section,
            planogram=planogram,
            category=category,
            shelf_camera_id=camera
        )
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@api.command(name='fixtures')
@pass_rebotics_context
def get_list_fixtures(ctx):
    """Shows list of fixtures"""
    try:
        if ctx.verbose:
            click.echo('Calling get fixtures')
        result = ctx.provider.get_fixtures()
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@api.command(name='fixture-delete')
@click.option('-i', '--pk', required=True, help='ID of a fixture to be deleted', type=click.STRING)
@pass_rebotics_context
def delete_fixture(ctx, pk):
    """Shows list of fixtures"""
    try:
        if ctx.verbose:
            click.echo('Calling delete fixture')
        result = ctx.provider.delete_fixture(
            pk=pk
        )
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@api.command(name='camera')
@click.option('-c', '--camera', required=True, help='Camera ID of the Shelf Camera', type=click.STRING)
@click.option('-a', '--added', required=True, help='Who added the camera (ID)', type=click.INT)
@click.option('-f', '--fixture', required=True, help='Fixture ID of the camera', type=click.INT)
@pass_rebotics_context
def create_shelf_camera(ctx, camera, added, fixture):
    """Saves ShelfCamera object"""
    try:
        if ctx.verbose:
            click.echo('Calling create shelf camera')
        result = ctx.provider.create_shelf_camera(
            camera,
            added,
            fixture
        )
        ctx.format_result(result)
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@api.command(name='cameras')
@pass_rebotics_context
def get_list_shelf_cameras(ctx):
    """Shows list of shelf cameras"""
    try:
        if ctx.verbose:
            click.echo('Calling list of shelf cameras')
        result = ctx.provider.get_shelf_cameras()
        ctx.format_result(result)
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@api.group(name='group')
def camera_grouping():
    """Camera grouping flow"""
    pass


@camera_grouping.command(name='create')
@click.option('-sc', '--shelf-camera', multiple=True, help='ID of a shelf camera', type=click.INT)
@pass_rebotics_context
def create_camera_group(ctx, shelf_camera: List[int]):
    """Create a new camera group.

    \b
    SHELF-CAMERA is the ID of a shlef camera and can be provided multiple times.
    Ex.: `hawkeye group create -sc 578 -sc 579 -sc 580 ...`
    """
    try:
        if ctx.verbose:
            click.echo('Calling create camera group')
        result = ctx.provider.create_camera_group(shelf_cameras=shelf_camera)
        ctx.format_result(result)
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@camera_grouping.command(name='list')
@click.option('-p', '--page', help='The number of the page to retrieve.', type=click.INT)
@pass_rebotics_context
def list_camera_groups(ctx, page: int = 1):
    """Show list of camera groups"""
    try:
        if ctx.verbose:
            click.echo('Calling list camera groups')
        result = ctx.provider.list_camera_groups(page=page)
        ctx.format_result(result)
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@camera_grouping.command(name='get')
@click.argument('camera_group_id', type=click.INT)
@pass_rebotics_context
def get_camera_group_by_id(ctx, camera_group_id: int):
    """Get a single camera groups by ID"""
    try:
        if ctx.verbose:
            click.echo('Calling get camera group by id')
        result = ctx.provider.get_camera_group_by_id(camera_group_id)
        ctx.format_result(result)
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@camera_grouping.command(name='enqueue')
@click.argument('camera_group_id', type=click.INT)
@click.option('-a', '--action', required=True, help='The ID of the action', type=click.INT)
@click.option(
    '-s',
    '--status',
    default=CameraGroupActionStatusType.CREATED,
    type=click.Choice(CameraGroupActionStatusType.CHOICES, case_sensitive=False),
)
@pass_rebotics_context
def create_camera_group_action(ctx, camera_group_id: int, action: int, status: str):
    """Create a camera group action"""
    try:
        if ctx.verbose:
            click.echo('Calling create camera group action')
        result = ctx.provider.create_camera_group_action(camera_group_id, action, status)
        ctx.format_result(result)
        click.echo(result)
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


api.add_command(shell, 'shell')
api.add_command(roles, 'roles')
api.add_command(configure, 'configure')
api.add_command(set_token, 'set_token')
