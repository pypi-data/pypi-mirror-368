import logging
import os
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from math import inf

import click
import tqdm
from click import pass_context

from rebotics_sdk.cli.common import configure, roles, set_token, shell
from rebotics_sdk.cli.utils import (
    app_dir, pass_rebotics_context, process_role, read_saved_role, ReboticsCLIContext, ReboticsScriptsConfiguration,
)
from rebotics_sdk.providers.fvm import FVMProvider
from .. import utils
from ..advanced import remote_loaders
from ..advanced.packers import VirtualClassificationDatabasePacker, extract_numeric
from ..providers import AdminProvider, ProviderHTTPClientException
from ..rcdb import Packer, Unpacker
from ..rcdb.entries import ImportEntry


@click.group()
@click.option('--api-verbosity', default=0, type=click.IntRange(0, 3), help='Display request detail')
@click.option('-f', '--format', default='table', type=click.Choice(['table', 'id', 'json']), help='Result rendering')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-c', '--config', type=click.Path(), default='fvm.json', help="Specify what config.json to use")
@click.option('-r', '--role', default=lambda: read_saved_role('fvm'), help="Key to specify what fvm to use")
@click.version_option()
@click.pass_context
def api(ctx, format, verbose, config, role, api_verbosity):
    """
    Admin CLI tool to communicate with FVM API
    """
    process_role(ctx, role, 'fvm')
    ctx.obj = ReboticsCLIContext(
        'fvm',
        role,
        format,
        verbose,
        api_verbosity,
        os.path.join(app_dir, config),
        provider_class=FVMProvider,
        click_context=ctx,

    )


api.add_command(shell, 'shell')
api.add_command(roles, 'roles')
api.add_command(configure, 'configure')
api.add_command(set_token, 'set_token')


@api.command(name='file')
@click.option('-f', '--name', required=True, help='Filename of the file', type=click.UNPROCESSED)
@pass_rebotics_context
def virtual_upload(ctx, name):
    """Create virtual upload"""
    if ctx.verbose:
        click.echo('Calling create virtual upload')
    result = ctx.provider.create_virtual_upload(
        name
    )
    if 'id' in result.keys():
        pk = result['id']
        with open(name, 'rb', ) as fio:
            click.echo('Uploading file...')
            remote_loaders.upload(destination=result['destination'], file=fio, filename=name)
            ctx.provider.finish(
                pk
            )
            click.echo("Successfully finished uploading")
    else:
        click.echo("Failed to call virtual upload")


@api.group()
def rcdb():
    pass


def _download_rcdb_locally(ctx, rcdb_file, target):
    rcdb_file = str(rcdb_file)

    if rcdb_file.isdigit():
        # download rcdb file by ID
        try:
            response = ctx.provider.get_rcdb_by_id(int(rcdb_file))
        except ProviderHTTPClientException as exc:
            raise click.ClickException(f"Failed to trigger by API with error: {exc}")
        # should we also save a response? probably no
        return _download_rcdb_locally(ctx, response['file']['file'], target)  # get the url
    elif utils.is_url(rcdb_file):
        # download rcdb file by URL
        filename = utils.get_filename_from_url(rcdb_file)
        local_filepath = pathlib.Path(target / filename)
        if local_filepath.exists():
            return local_filepath
        try:
            remote_loaders.download(rcdb_file, local_filepath, progress_bar=ctx.do_progress_bar())
        except Exception as exc:
            raise click.ClickException(f"Failed to download file by URL: {exc}")
        return _download_rcdb_locally(ctx, local_filepath, target)
    else:
        # assuming that it is a local file path
        local_filepath = pathlib.Path(rcdb_file)
        if not local_filepath.exists():
            raise click.ClickException("Local file is not loaded!")
        return local_filepath


preview_downloader_dataclass_kwargs = {
    'frozen': True,
    'eq': False,
}
if sys.version_info >= (3, 10):
    preview_downloader_dataclass_kwargs['slots'] = True


@dataclass(**preview_downloader_dataclass_kwargs)
class PreviewDownloader:
    provider: FVMProvider
    progress_bar: tqdm.tqdm
    error_logger: logging.Logger

    def __call__(self, url: str, target: pathlib.Path) -> None:
        try:
            self.provider.download(url, target)
        except Exception as exc:
            self.error_logger.exception(f"Failed to download preview from {url} to {target}", exc_info=exc)
        self.progress_bar.update()


@rcdb.command(name='download')
@click.option('-t', '--target', type=click.Path(), default=pathlib.Path('.'))
@click.argument('rcdb_file')
@pass_rebotics_context
def rcdb_download(ctx, rcdb_file, target):
    target = pathlib.Path(target)
    click.echo("Downloading rcdb file locally...")
    rcdb_file = _download_rcdb_locally(ctx, rcdb_file, target)
    click.echo(rcdb_file)


@rcdb.command(name="unpack")
@click.argument('rcdb_file')
@click.option('-t', '--target', type=click.Path(), default=pathlib.Path('.'))
@click.option('-w', '--with-images', is_flag=True)
@click.option('-c', '--concurrency', default=None, type=click.INT)
@pass_rebotics_context
def rcdb_unpack(ctx, rcdb_file, target, with_images, concurrency):
    """Unpack rcdb files. if the images """
    target = pathlib.Path(target)
    click.echo("Downloading rcdb file locally...")
    rcdb_file = _download_rcdb_locally(ctx, rcdb_file, target)
    if not with_images:
        click.echo(f"File loaded into {rcdb_file}")
        return

    # create new packer and unpacker
    packer = VirtualClassificationDatabasePacker(
        source=str(rcdb_file),
        with_images=with_images
    )
    images_links_expiration = packer.get_images_links_expiration()
    if images_links_expiration is not None and images_links_expiration < datetime.now(timezone.utc):
        raise click.ClickException("Cannot download images: links are expired")

    features_count = packer.get_features_count()
    click.echo(f"Total features count: {features_count if features_count is not None else 'unknown'}")

    max_workers = concurrency
    if max_workers is not None:
        max_workers = max(max_workers, 1)

    error_logger = logging.getLogger('fvm.rcdb_unpack.errors')
    error_logger.setLevel(logging.ERROR)
    error_log_path = target / 'errors.log'
    error_logger_handler = logging.FileHandler(error_log_path, delay=True)
    error_logger_handler.setLevel(logging.ERROR)
    error_logger.addHandler(error_logger_handler)

    labels_path = target / VirtualClassificationDatabasePacker.FieldNames.LABELS
    features_path = target / VirtualClassificationDatabasePacker.FieldNames.FEATURES
    uuids_path = target / VirtualClassificationDatabasePacker.FieldNames.UUIDS
    images_path = target / VirtualClassificationDatabasePacker.FieldNames.IMAGES

    # Initialize downloading previews progress bar with certain params (leave, delay) to not display anything yet
    with tqdm.tqdm(desc="Downloading previews", leave=False, delay=inf) as download_previews_progress_bar, \
        ThreadPoolExecutor(max_workers=max_workers) as executor:  # noqa

        # TODO: REB3-13527 reuse HTTP connections to speed up things up to 5 times
        preview_downloader = PreviewDownloader(ctx.provider, download_previews_progress_bar, error_logger)
        total_images_to_download = 0

        with open(labels_path, 'w') as labels_io, \
            open(features_path, 'w') as features_io, \
            open(uuids_path, 'w') as uuids_io, \
            open(images_path, 'w') as images_io:  # noqa

            for index, entry in tqdm.tqdm(
                enumerate(packer.unpack()),
                desc="Iterating over RCDB entries",
                total=features_count,
                leave=False,
                position=0
            ):
                labels_io.write(f"{entry.label}\n")
                features_io.write(f"{','.join(map(str, entry.feature))}\n")

                # handle the case when no uuid
                if entry.uuid is not None:
                    uuid = str(entry.uuid)
                else:
                    uuid = ''
                uuids_io.write(f"{uuid}\n")

                # handle the case when no image url
                if entry.image_url is None:
                    images_io.write("\n")
                    continue

                # save images from entry. btw need to think about image extension, can be not only JPEG
                if uuid:
                    image_file_name = uuid
                else:
                    image_file_name = f'image_{index}'
                image_path = target / entry.label / f'{image_file_name}.jpeg'
                images_io.write(f"{image_path}\n")
                if image_path.exists():
                    # check if image can be loaded via pil and whatnot
                    continue
                image_path.parent.mkdir(exist_ok=True, parents=True)

                # Enqueue a task for the executor to download image
                executor.submit(preview_downloader, entry.image_url, image_path)
                total_images_to_download += 1

        if total_images_to_download > 0:
            click.echo(f"Downloading {total_images_to_download} images not present in FS, please wait...")
            # Now we set params to display the progress bar, because there are previews to download
            download_previews_progress_bar.total = total_images_to_download
            download_previews_progress_bar.leave = True
            download_previews_progress_bar.delay = 0
            download_previews_progress_bar.refresh()

    if error_log_path.exists():
        click.echo(f"Some errors occurred, check {error_log_path} for details")

    click.echo("Unpacking is completed")


@rcdb.command(name='upload')
@click.argument('rcdb_file', type=click.Path(exists=True, dir_okay=False, file_okay=True))
@click.option('-r', '--retailer-codename', type=click.STRING,  prompt=True) # required in endpoint /api/rcdb/
@click.option('-m', '--model-codename', type=click.STRING, prompt=True) # required in endpoint /api/rcdb/
@click.option('-w', '--with-images', is_flag=True)
@pass_rebotics_context
def rcdb_upload(ctx, rcdb_file, **kwargs):
    """
    Upload RCDB file
    """
    # retrieve model_id by the model_codename
    # read features count in the file

    rcdb_file = pathlib.Path(rcdb_file)
    kwargs['archive_size'] = rcdb_file.stat().st_size
    unpacker = Unpacker(rcdb_file)
    with unpacker:
        metadata = unpacker.get_metadata()
        kwargs['features_count'] = metadata.count

    ctx.verbose_log(f"Archive size: {kwargs['archive_size']}. "
                    f"Features count: {kwargs['features_count']}")

    ctx.verbose_log("Upload rcdb file using presigned post URL")
    with open(rcdb_file, 'rb') as file_io:
        file_upload = ctx.provider.upload_file(file_io, filename=rcdb_file.name, progress_bar=ctx.do_progress_bar())
    file_id = file_upload['id']

    # call API to create an RCDB entry in database
    ctx.provider.save_rcdb(
        file_id,
        **kwargs
    )


@rcdb.command(name='copy')
@click.argument("backup_id", type=int)
@click.option("-r", "--retailer-codename", type=click.STRING, required=True, help="Retailer codename is required")
@click.option('-m', '--model-codename', type=click.STRING, help="If not specified,"
                                                                " the model_codename from the backup will be used")
@click.option("--admin-role", type=click.STRING, help="Uses the role, if not specified, "
                                                      "will be using the same role from fvm. "
                                                      "E.g. we have r3dev and r3us for both fvm and admin")
@pass_rebotics_context
@pass_context
def rcdb_copy_from_admin(click_ctx, ctx, backup_id, retailer_codename, model_codename, admin_role):
    """Copy CORE rcdb from the admin and upload and assign the rcdb file to appropriate retailer and model.

    To create rcdb backup from CORE go to admin application on /admin/nn_models/retailermodel/
    Click on "Download reference data"
    Wait a couple of minutes, and navigate to /admin/classification_data/featurevectorbackup/
    Retrieve the ID of the backup and use it with this command.
    """
    try:
        if admin_role is None:
            admin_role = ctx.role
            ctx.verbose_log(f"Admin role is not specified, using same role for fvm: {admin_role}")
        admin_config = ReboticsScriptsConfiguration(
            os.path.join(app_dir, 'admin.json'),
            provider_class=AdminProvider
        )
        admin_provider: AdminProvider = admin_config.get_provider(admin_role, api_verbosity=ctx.api_verbosity)

        if admin_provider is None:
            raise Exception(f"There is no admin provider with role name {admin_role}")
    except Exception as exc:
        click.echo(f"Failed to initialize admin provider with {exc}")
        sys.exit(1)

    ctx.verbose_log(f"Fetching rcdb backup {backup_id} from {admin_provider.host}")
    backup = admin_provider.rcdb.get(backup_id)
    ctx.verbose_log("Backup data: ")
    if ctx.verbose:
        ctx.format_result(backup, force_format='json')

    if backup['status'] != 'EXPORT_DONE':
        click.echo(f"The backup #{backup_id} export may not be finished and has status {backup['status']}")

    backup_url = backup['backup']
    rcdb_file_path = pathlib.Path(f"{retailer_codename}_{datetime.now().strftime('%Y_%m_%d_%H-%M')}.rcdb")

    ctx.verbose_log(f"Downloading rcdb backup from {backup_url} to {rcdb_file_path}")

    remote_loaders.download(backup_url, rcdb_file_path, progress_bar=True)

    ctx.verbose_log(f"Invoking rcdb_upload from {rcdb_file_path}")

    selected_model_codename = model_codename
    if model_codename is None:
        ctx.verbose_log('Setting model codename from backup')
        selected_model_codename = backup.get('model_codename')

    if selected_model_codename is None:
        click.echo("There is no specified model_codename.")
        sys.exit(1)

    click_ctx.invoke(rcdb_upload,
                     rcdb_file=rcdb_file_path,
                     retailer_codename=retailer_codename,
                     model_codename=selected_model_codename,
                     with_images=False)


@rcdb.command(name='pack')
@click.option('-r', '--retailer', help="Retailer codename", prompt=True)
@click.option('-m', '--model', help="Model codename", prompt=True)
@click.option('-i', '--images', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('-l', '--labels', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('-f', '--features', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--model-type', type=str, default='arcface')
@click.option('-t', '--target', type=click.Path(dir_okay=True, file_okay=True), default=pathlib.Path('.'))
@pass_rebotics_context
def rcdb_pack(ctx: ReboticsCLIContext, retailer, model, images, labels, features, model_type, target):
    """
    Pack classification database to single .rcdb file
    """
    ctx.verbose_log("Creating import request: \n"
                    "retailer: {}\n"
                    "model: {}\n"
                    "extension: {}".format(retailer, model, Packer.extension))

    target = pathlib.Path(target)

    if target.suffix == '.rcdb':
        destination = target
    elif target.is_dir():
        destination = target / f'{retailer}_{model}.{Packer.extension}'
    else:
        destination = target.with_suffix(f'.{Packer.extension}')
    destination.parent.mkdir(exist_ok=True, parents=True)

    ctx.verbose_log(f"Destination: {destination}")

    # iterate over a folder with images and create a list of paths that are ordered by numeric value in the filename
    image_path_list = sorted(pathlib.Path(images).iterdir(), key=lambda filepath: extract_numeric(filepath.name))
    total_images = len(image_path_list)
    ctx.verbose_log(f"Total images: {total_images}")

    packer = Packer(destination=destination,
                    entry_type=ImportEntry,
                    model_type=model_type,
                    model_codename=model)

    with packer, tqdm.tqdm(total=total_images, leave=True, disable=not ctx.do_progress_bar()) as pbar:
        with open(labels, 'r') as labels_file, open(features, 'r') as features_file:
            counter = 0
            while True:
                try:
                    entry = ImportEntry(
                        label=labels_file.readline(),
                        feature_vector=features_file.readline(),
                        image=image_path_list[counter]
                    )
                except IndexError as exc:
                    # no image found for given counter index, meaning we are done here
                    ctx.verbose_log(str(exc))
                    break

                if entry.is_empty():
                    break

                packer.add_entry(entry)
                counter += 1
                pbar.update(1)

    # add routine for duplicate checking
    click.echo(f"RCDB is saved at: {destination}")


@rcdb.command(name='latest')
@click.option('-r', '--retailer', help="Retailer codename", prompt=True)
@click.option('-m', '--model', help="Model codename", prompt=True)
@pass_rebotics_context
def rcdb_latest(ctx, retailer, model):
    """Retrieve latest RCDB file for retailer and model"""
    result = ctx.provider.get_latest_rcdb(
        model_codename=model,
        retailer_codename=retailer,
    )
    ctx.format_result(result)
