import csv
import json
import logging
import os
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import copy
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import List

import click
import pandas as pd
from click import get_current_context
from tqdm import tqdm

from rebotics_sdk import utils, get_provider
from rebotics_sdk.advanced.reverse_planogram import make_planogram_df
from .common import shell, roles, configure, set_token
from .renderers import format_processing_action_output, format_full_table
from .tasks import (
    task_cancel_processing,
    task_create_processing_action_for_image,
    task_download_line_coordinates,
    task_download_processing_action,
    task_recalculate_processing,
    task_requeue_processing,
    upload_preview_task,
)
from .utils import (
    app_dir,
    download_file_from_dict,
    fetch_scans,
    guess_input_type,
    pass_rebotics_context,
    process_role,
    read_saved_role,
    ReboticsCLIContext,
    task_runner,
)
from ..advanced import remote_loaders
from ..constants import CvatTaskPriority, CVAT_EXPORT_WORKSPACE
from ..providers import ProviderHTTPClientException, RetailerProvider
from ..utils import download_file, get_filename_from_url, mkdir_p

logger = logging.getLogger(__name__)


@click.group()
@click.option('--api-verbosity', default=0, type=click.IntRange(0, 3), help='Display request detail')
@click.option('-f', '--format', default='table', type=click.Choice(['table', 'id', 'json']))
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-c', '--config', type=click.Path(), default='retailer.json', help="Specify what config.json to use")
@click.option('-r', '--role', default=lambda: read_saved_role('retailer'), help="Key to specify what retailer to use")
@click.version_option()
@click.pass_context
def api(ctx, format, verbose, config, role, api_verbosity):
    """
    Retailer CLI tool to communicate with retailer API
    """
    process_role(ctx, role, 'retailer')

    ctx.obj = ReboticsCLIContext(
        'retailer',
        role,
        format,
        verbose,
        api_verbosity,
        os.path.join(app_dir, config),
        provider_class=RetailerProvider,
        click_context=ctx,
    )


@api.command()
@pass_rebotics_context
def version(ctx):
    """Show retailer backend version"""
    ctx.format_result(ctx.provider.version(), 100)


@api.command()
@click.option('-t', '--input_type')
@click.option('-s', '--store', type=click.INT)
@click.argument('files', nargs=-1, required=True, type=click.File('rb'))
@pass_rebotics_context
def upload_files(ctx, input_type, store, files):
    """
    Upload processing files to the retailer backend, that can be used as processing action inputs
    """
    file_ids = []
    for f_ in files:
        response = ctx.provider.processing_upload(
            store, f_, input_type
        )
        file_ids.append(response['id'])

        if ctx.verbose:
            click.echo(response)  # redirecting this output to stderr
    click.echo(' '.join(map(str, file_ids)))


REQUEUE_TYPES = {
    "facenet_kf": 'requeue_for_facenet_keyframes_key',
    "pt_multiclass": 'REQUEUE_PRICE_TAGS_DETECTION_MULTICLASS',
    "pt_heatmap": 'REQUEUE_PRICE_TAGS_DETECTION_MULTICLASS_HEATMAP',
    "pt_voting": 'REQUEUE_PRICE_TAGS_DETECTION_MULTICLASS_VOTING',
}


@api.command()
@click.argument('processing_ids', required=True, nargs=-1, type=click.INT)
@click.option('-t', '--requeue-type', type=click.Choice(choices=REQUEUE_TYPES.keys()), required=False, default=None)
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def requeue(ctx, processing_ids, requeue_type, concurrency):
    """Requeue processing actions by given IDs"""
    return task_runner(ctx, task_requeue_processing, processing_ids, concurrency, requeue_type=requeue_type)


@api.command()
@click.argument('processing_ids', required=True, nargs=-1, type=click.INT)
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def cancel(ctx, processing_ids, concurrency):
    """Cancel processing of the actions by given IDs"""
    return task_runner(ctx, task_cancel_processing, processing_ids, concurrency)


@api.command()
@click.argument('processing_ids', required=True, nargs=-1, type=click.INT)
@click.option('-b', '--batch-size', type=int, default=3,
              help="The lower the number the slower and more reliable the upload will be")
@pass_rebotics_context
def export_to_dataset(ctx, processing_ids, batch_size):
    if ctx.verbose:
        click.echo("Exporting to dataset with batch size {} scans: {}".format(batch_size, processing_ids), err=True)

    try:
        if ctx.verbose:
            click.echo("Sending request...")
        response = ctx.provider.export_to_dataset(processing_ids, batch_size)
        click.echo('Queued to export to dataset: {}'.format(response))
    except ProviderHTTPClientException as exc:
        if ctx.verbose:
            logger.exception(exc)
        raise click.ClickException(str(exc.response.json()))


@api.command()
@click.argument('processing_ids', required=True, nargs=-1, type=click.INT)
@click.option('-q', '--image-quality', type=int, default=80,
              help="Jpeg image quality between 0 and 100. Default is 80.")
@click.option('-s', '--segment-size', type=int, default=20,
              help="Number of images in job. Set 0 to not split task into jobs.")
@click.option('-w', '--workspace', type=str, default=CVAT_EXPORT_WORKSPACE,
              help='Workspace (organization) name in CVAT. Case sensitive.')
@click.option('-p', '--priority', type=click.Choice(list(CvatTaskPriority.OPTIONS.keys())))
@pass_rebotics_context
def export_to_cvat(ctx, processing_ids, image_quality, segment_size, workspace, priority):
    if ctx.verbose:
        click.echo('Exporting scans to CVAT: {}'.format(processing_ids), err=True)

    try:
        if ctx.verbose:
            click.echo('Sending request...')
        response = ctx.provider.export_to_cvat(
            processing_ids,
            image_quality,
            segment_size,
            workspace,
            CvatTaskPriority.OPTIONS.get(priority),
        )
        click.echo('Queued to export to CVAT: {}'.format(response))
    except ProviderHTTPClientException as exc:
        if ctx.verbose:
            logger.exception(exc)
        raise click.ClickException(str(exc.response.json()))


@api.command()
@click.argument('processing_ids', required=True, nargs=-1, type=click.INT)
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def recalculate(ctx, processing_ids, concurrency):
    """Recalculate processing of the actions by given IDs"""
    return task_runner(ctx, task_recalculate_processing, processing_ids, concurrency)


@api.command()
@click.option('-t', '--input_type')
@click.option('-s', '--store', type=click.INT)
@click.option('-p', '--store-planogram', type=click.INT)
@click.option('--aisle')
@click.option('--section')
@click.option('-l', '--lens-used', is_flag=True, default=False)
@click.argument('files', nargs=-1, required=True, type=click.INT)
@pass_rebotics_context
def create_processing_action(ctx, input_type, store, store_planogram, aisle, section, lens_used, files):
    """Create processing action for store defining files by IDs"""
    response = ctx.provider.create_processing_action(
        store, files, input_type,
        store_planogram=store_planogram,
        aisle=aisle,
        section=section,
        lens_used=lens_used
    )
    if ctx.verbose:
        click.echo(json.dumps(response, indent=2))
    click.echo(response['id'])


@api.command(deprecated=True)
@click.argument('actions', nargs=-1, required=True, type=click.INT)
@click.option('-t', '--target', type=click.Path(exists=True, file_okay=False, path_type=Path), default='.',
              help='Target path to save processing actions data.')
@click.option('-c', '--concurrency', type=int, default=4,
              help='Count of parallel workers for API accessing.')
@pass_rebotics_context
def download_processing_action(ctx, actions: List[int], target: Path, concurrency: int):
    """Download processing actions by given IDs. Deprecated, use `processing-action ... download` instead"""
    processing_action_download_impl(ctx, target, concurrency, actions)


@api.command()
@click.argument('scans', nargs=-1, required=True, type=click.INT)
@click.option('-t', '--target', type=click.Path(), default='.', help='Target path to save JSON files.')
@click.option('-c', '--concurrency', type=int, default=4, help='Count of parallel workers for API accessing.')
@pass_rebotics_context
def download_line_coordinates(ctx, scans, target, concurrency):
    """Download coordinates for a set of lines (shelf and edge) of provided scans."""
    task = partial(task_download_line_coordinates, target=target, ctx=ctx)

    with ThreadPoolExecutor(max_workers=min(concurrency, len(scans))) as executor:
        executor.map(task, scans)


@api.command()
@click.argument('actions', nargs=-1, required=True, type=click.INT)
@click.option('-t', '--target', type=click.Path(), default='.')
@click.option('-c', '--concurrency', type=int, default=4)
@click.option('--template', default="{action_id}_{i}.{ext}")
@pass_rebotics_context
def download_processing_inputs(ctx, actions, target, concurrency, template):
    """Download processing inputs from processing actions"""
    files_to_download = []

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        actions_data = pool.map(partial(task_download_processing_action, ctx), actions)

        if ctx.verbose:
            click.echo('GET API for processing actions completed')

        for data in actions_data:
            for i, input_object in enumerate(data.get('inputs', [])):
                filename = get_filename_from_url(input_object['file'])
                ext = filename.split('.')[-1]
                action_id = data['id']
                files_to_download.append({
                    'filepath': os.path.join(target, template.format(action_id=action_id, i=i, ext=ext)),
                    'url': input_object['file'],
                    'ctx': ctx
                })

        if ctx.verbose:
            click.echo("Task registration completed")

        pool.map(download_file_from_dict, files_to_download)

        if ctx.verbose:
            click.echo('Processing inputs download success')


@api.command()
@click.option('-d', '--delete', is_flag=True)
@click.option('-c', '--concurrency', type=int, default=4)
@click.argument('target', type=click.Path(exists=True), default=os.getcwd())
@pass_rebotics_context
def upload_previews_from_folder(ctx, delete, concurrency, target):
    """
    Upload previews from file system to the server in parallel.
    It has increased retries and timeout.

    You need to have the file structure like this

\b
target_folder/
└── 6925303739454
    ├── preview_1.png
    ├── preview_2.png
    └── preview_3.png
    """
    provider = ctx.provider
    if provider is None:
        raise click.ClickException('You have supplied role that is not correct!')

    ctx.provider.retries = 5
    ctx.provider.timeout = 300
    verbose = ctx.verbose

    tasks = []
    for label in os.listdir(target):
        upc_folder = os.path.join(target, label)
        if not os.path.isdir(upc_folder):
            continue

        if verbose:
            click.echo('Reading folder: %s' % upc_folder)
        task = {
            'ctx': ctx,
            'images_path': [],
            'delete': delete,
            'upc': label
        }

        if label.isdigit():
            if ctx.verbose:
                click.echo('Registering {} folder'.format(upc_folder))
            for filename in os.listdir(upc_folder):
                image_path = os.path.join(upc_folder, filename)

                if os.path.isfile(image_path):
                    task['images_path'].append(image_path)

        if task['images_path']:
            tasks.append(task)

    if verbose:
        click.echo('Number of tasks: {}'.format(len(tasks)))

    # TODO: REB3-13527 reuse HTTP connections to speed up things up to 5 times
    with ThreadPoolExecutor(max_workers=min(concurrency, len(tasks))) as p:
        p.map(upload_preview_task, tasks)
    click.echo('Finished')


PROCESSING_STATUSES = {
    'created': 'action created',
    'done': 'done',
    'error': 'error',
    'interrupted': 'interrupted',
    'progress': "in progress",
}


@api.command()
@click.option('-s', '--store', type=click.INT, help='Store ID')
@click.option('--status', type=click.Choice(list(PROCESSING_STATUSES.keys())))
@click.option('-p', '--page', type=click.INT, default=1)
@click.option('-r', '--page-size', type=click.INT, default=10)
@pass_rebotics_context
def processing_actions(ctx, store, status, page, page_size):
    """Fetches processing actions and renders them in terminal"""
    if ctx.verbose:
        click.echo('Getting list of processing actions')
    try:
        data = ctx.provider.processing_action_list(
            store,
            PROCESSING_STATUSES.get(status),
            page=page,
            page_size=page_size,
        )
        click.echo('Total results: %d' % len(data))
        if ctx.format != 'id':
            format_processing_action_output(data, 'id')
        format_processing_action_output(data, ctx.format)
    except ProviderHTTPClientException as exc:
        if ctx.verbose:
            logger.exception(exc)
        raise click.ClickException('Failed to get list of processing actions')


@api.command()
@click.option('-t', '--token')
@click.argument('url')
@pass_rebotics_context
def set_webhook(ctx, token, url):
    """Setting webhook url for current user"""
    data = ctx.provider.set_webhook(url, token)
    click.echo('Webhook ID on server is : %d' % data['id'])


@api.command()
@click.option('-t', '--title', help='Planogram title', required=True)
@click.option('-d', '--description', help='Planogram description', default='')
@click.argument('planogram_file', type=click.File(mode='rb'))
@pass_rebotics_context
def import_planogram(ctx, planogram_file, title, description):
    """Upload planogram file to retailer instance in a very specific format"""
    try:
        ctx.provider.import_planogram(planogram_file, title, description)
    except (AssertionError, ProviderHTTPClientException) as exc:
        click.echo(exc, err=True)


@api.command()
@click.argument('planogram_assign_file', type=click.File(mode='r'))
@click.option('-d', '--deactivate', is_flag=True, help='Deactivate old planogram')
@pass_rebotics_context
def assign_planogram_through_file(ctx, planogram_assign_file, deactivate):
    """ Assign Planogram through the file """
    try:
        ctx.provider.assign_planogram(planogram_assign_file, deactivate)
    except (AssertionError, ProviderHTTPClientException) as exc:
        click.echo(exc, err=True)


@api.command(deprecated=True)
@click.argument('braincorp_csv', type=click.File(mode='r'))
@click.option('-s', '--store', type=click.INT, help='Store ID')
@click.option('-t', '--target', default='after_processing_upload.csv')
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def upload_brain_corp_images(ctx, braincorp_csv, store, target, concurrency):
    df = pd.read_csv(braincorp_csv, header=None, names=[
        'date', 'time', 'image', 'x', 'y', 'yaw', 'type', 'count', 'note',
    ])
    image_paths = df['image'].tolist()

    with ThreadPoolExecutor(max_workers=min(concurrency, len(image_paths))) as pool:
        processing_actions_ids = pool.map(
            partial(task_create_processing_action_for_image, ctx, store),
            image_paths
        )
    df['action_id'] = processing_actions_ids
    click.echo('Processing upload completed. Please check completion using: ')
    click.echo('retailer processing-actions -s {}'.format(store))
    click.echo(df.head())
    df.to_csv(target)
    click.echo('File is written to {}'.format(target))


@api.command(deprecated=True)
@click.argument('braincorp_csv', type=click.File(mode='r'))
@click.option('-t', '--target', default='after_processing_completed.csv')
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def process_brain_corp_images(ctx, braincorp_csv, target, concurrency):
    df = pd.read_csv(braincorp_csv)
    action_ids = df['action_id'].tolist()

    with ThreadPoolExecutor(max_workers=min(concurrency, len(action_ids))) as pool:
        pr_actions = pool.map(partial(task_download_processing_action, ctx), action_ids)

    def get_product_plu(action):
        if not action:
            return None
        item_upcs = map(lambda x: x['upc'], action['items'])
        return ','.join(set(item_upcs))

    identified_products = list(map(get_product_plu, pr_actions))

    df['identified_products'] = identified_products
    click.echo(df.head())
    df.to_csv(target)
    click.echo('File is written to {}'.format(target))


@api.command()
@click.argument('store_id', type=int)
@pass_rebotics_context
def store_aisles(ctx, store_id):
    """
    This API endpoint returns a list of the aisles and sections for store, accessed by id.
    Allows only GET on detail-route
    Example: get: /api/v4/store/store_planograms/<store_id>/
    """
    aisles = ctx.provider.get_store_aisles(store_id)
    # flatter results
    results = []
    for aisle in aisles:
        sections = aisle.pop('sections')
        for section in sections:
            aisle_section = copy(aisle)
            aisle_section['section'] = section
            results.append(aisle_section)
        else:
            results.append(aisle)

    format_full_table(results)


@api.command()
@pass_rebotics_context
def store_list(ctx):
    """ Return all stores related to the authenticated user"""
    results = ctx.provider.get_stores()
    format_full_table(results)


@api.command()
@click.argument('username')
@pass_rebotics_context
def user_subscriptions(ctx, username):
    """ Returns all subscriptions of the user"""
    ctx.format_result(ctx.provider.user_subscriptions(username))


@api.command()
@click.option('-s', '--store', help='Store ID')
@click.option('-a', '--aisle', help='Aisle')
@click.option('-S', '--section', help='Section')
@click.argument('username')
@pass_rebotics_context
def user_subscribe(ctx, username, store, aisle, section):
    """
    Create a subscription of the user to specific aisle and section scan updates in store alongside with AEON features
    """
    ctx.format_result(ctx.provider.user_subscriptions_create(
        username, store, aisle, section
    ))


def task_upload_and_notify_request(task_def):
    with open(task_def['filepath'], 'rb') as file_io:
        response = remote_loaders.upload(task_def['destination'], file_io)
    status_code = response.status_code

    if 200 <= status_code < 300:
        ctx = task_def['ctx']
        ctx.provider.notify_processing_upload_finished(task_def['id'])
        return task_def['id']
    return None


@api.command()
@click.argument('files', nargs=-1, required=True, type=click.Path(exists=True, dir_okay=False))
@click.option('-c', '--concurrency', type=int, default=4)
@click.option('-t', '--input_type')
@pass_rebotics_context
def upload_processing_files(ctx, files, concurrency, input_type):
    # TODO: REB3-13527 reuse HTTP connections to speed up things up to 5 times
    with ThreadPoolExecutor(max_workers=min(concurrency, len(files))) as pool:
        # Keeping progress bars here is hard, code would be much simpler without them
        url_request_futures = []
        url_future_to_file = {}

        # Request a storage upload URL for each file with `processing_upload_request`
        for file in files:
            filepath = Path(file)
            if input_type is None:
                input_type = guess_input_type(filepath.suffix)

            url_request_future = pool.submit(ctx.provider.processing_upload_request, filepath.name, input_type)
            url_request_futures.append(url_request_future)
            url_future_to_file[url_request_future] = file

        upload_futures = []
        upload_task_ids = []

        # Perform file uploads via task_upload_and_notify_request
        for req_future in tqdm(
            as_completed(url_request_futures),
            'Getting S3 pre-signed post',
            total=len(url_request_futures),
            leave=False,
        ):
            # TODO: handle errors, retry if errors are temporal (like HTTP 500)
            req = req_future.result()

            upload_futures.append(
                pool.submit(task_upload_and_notify_request, {
                    'destination': req['destination'],
                    'id': req['id'],
                    'filepath': url_future_to_file[req_future],
                    'ctx': ctx,
                })
            )
            upload_task_ids.append(req['id'])

        uploaded = []

        for upload_future in tqdm(
            as_completed(upload_futures),
            'Uploading files',
            total=len(upload_futures),
            leave=False,
        ):
            id_ = upload_future.result()

            if id_ is not None:
                uploaded.append(id_)

        click.echo("Uploaded: {}".format(uploaded))
        click.echo("Failed: {}".format(list(
            set(upload_task_ids) - set(uploaded)
        )))


@api.group(invoke_without_command=True)
@click.argument('processing_id', required=True, type=click.STRING)
@pass_rebotics_context
@click.pass_context
def processing_action(click_context, ctx, processing_id):
    """Command group for scans in a format of single entry or list or range.
    Supports following formats:

        1. 1-10

        2. 1,2,3,4,5

        3. 1,2,3-5,6,7,8-10
    """
    try:
        processing_ids = utils.parse_id_range_string(processing_id)
    except ValueError as exc:
        ctx.verbose_log(exc)
        click_context.exit(1)
        return

    setattr(ctx, 'processing_id', processing_ids[0])
    setattr(ctx, 'processing_id_string', processing_id)
    setattr(ctx, 'processing_id_list', processing_ids)

    if click_context.invoked_subcommand is None:
        processing_actions_list = fetch_scans(ctx, processing_ids)
        format_processing_action_output(processing_actions_list, ctx.format)


@processing_action.command(name='realogram')
@pass_rebotics_context
def processing_action_realogram(ctx):
    """Returns processing realogram by processing_id."""
    try:
        result = ctx.provider.processing_action_realogram_detail(ctx.processing_id)
        ctx.format_result(result, keys_to_skip=['banner_id'])
    except ProviderHTTPClientException as exc:
        if ctx.verbose:
            logger.exception(exc)
        click.echo('Failed relogram: %s' % exc)


@processing_action.command(name='download')
@click.option('-t', '--target', type=click.Path(exists=True, file_okay=False, path_type=Path), default='.')
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def processing_action_download(ctx, target: Path, concurrency: int):
    """Download the processing and returns the result of this processing"""
    if ctx.verbose:
        click.echo(f'Downloading processing actions data for {ctx.processing_id_string}..')

    processing_action_download_impl(ctx, target, concurrency, ctx.processing_id_list)


def processing_action_download_impl(ctx, target: Path, concurrency: int, actions: List[int]):
    files_to_download = []

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        actions_data = pool.map(partial(task_download_processing_action, ctx), actions)

        for data in actions_data:
            action_id = data['id']
            processing_action_folder = target / f'ProcessingAction#{action_id}'

            mkdir_p(processing_action_folder)
            results = processing_action_folder / 'results'
            inputs = processing_action_folder / 'inputs'

            mkdir_p(results)
            mkdir_p(inputs)

            for key in ['merged_image_jpeg', 'merged_image', ]:
                files_to_download.append({
                    'url': data[key],
                    'filepath': results / get_filename_from_url(data[key]),
                    'ctx': ctx,
                })

            for input_object in data.get('inputs', []):
                files_to_download.append({
                    'filepath': inputs / get_filename_from_url(input_object['file']),
                    'url': input_object['file'],
                    'ctx': ctx
                })

            with open(processing_action_folder / f'processing_action_{action_id}.json', 'w') as fout:
                json.dump(data, fout, indent=4)

            if ctx.verbose:
                click.echo(f'Downloading files for {action_id}..')

        pool.map(download_file_from_dict, files_to_download)

    if ctx.verbose:
        click.echo('Processing download success')


@processing_action.command(name='requeue')
@click.option('-t', '--requeue-type', type=click.Choice(choices=REQUEUE_TYPES.keys()), required=False, default=None)
@pass_rebotics_context
def processing_action_requeue(ctx, requeue_type):
    """ Requeue the processing action by processing_id """
    try:
        result = ctx.provider.requeue(ctx.processing_id)
        format_processing_action_output([result, ], ctx.format)
    except ProviderHTTPClientException as exc:
        click.echo('Requeue is not allowed %s' % exc)


@processing_action.command(name='cancel')
@pass_rebotics_context
def processing_action_cancel(ctx):
    """Cancel processing calculation by processing_id"""
    try:
        result = ctx.provider.cancel(ctx.processing_id)
        format_processing_action_output([result, ], ctx.format)
    except ProviderHTTPClientException as exc:
        click.echo('Cancel is not allowed: %s' % exc)


@processing_action.command(name='recalculate')
@pass_rebotics_context
def processing_action_recalculate(ctx):
    """Recalculate processing action by processing_id"""
    try:
        result = ctx.provider.recalculate(ctx.processing_id)
        format_processing_action_output([result, ], ctx.format)
    except ProviderHTTPClientException as exc:
        click.echo('Recalculate is not allowed: %s' % exc)


@processing_action.command(name='view')
@pass_rebotics_context
def processing_action_view_in_admin(ctx):
    """View processing action in admin"""
    url = ctx.provider.build_url('/admin/processing/processingaction/{}/change/'.format(ctx.processing_id))

    if ctx.verbose:
        click.echo('Opening processing action in browser: %s' % url)
    webbrowser.open(url)


@processing_action.command(name='delete')
@pass_rebotics_context
def processing_action_delete(ctx):
    """Delete existing processing action by processing_id"""
    try:
        result = ctx.provider.processing_action_delete(ctx.processing_id)
        click.echo('Successfully deactivated processing action %s', result)
    except ProviderHTTPClientException as exc:
        if ctx.verbose:
            logger.exception(exc)
        click.echo('Failed to deactivate: %s' % exc)


@processing_action.command(name='copy')
@click.option('-s', '--store', type=click.INT)
@pass_rebotics_context
def processing_action_copy(ctx, store):
    """Copy of the existing processing action by processing_id into new store"""

    action = ctx.provider.processing_action_detail(ctx.processing_id)

    store_id = action['store_id']
    if store:
        store_id = store

    inputs_id = [i['id'] for i in action['inputs']]

    try:

        result = ctx.provider.create_processing_action(
            store_id,
            files=inputs_id,
            input_type=action.get('input_type', 'image'),
        )
        click.echo('Successfully created processing action')
        format_processing_action_output([result, ], ctx.format)
    except ProviderHTTPClientException as exc:
        if ctx.verbose:
            logger.exception(exc)
        click.echo('Failed to create processing action: %s' % exc)


@processing_action.command(name="report-image")
@click.option('-l', '--label', type=click.Choice([
    "unique_id",
    "product_unique_id",
    "user_selected_unique_id",
    "original_unique_id"
]), default='unique_id')
@click.option('-t', '--target', type=click.Path(), default='.')
@pass_rebotics_context
def processing_action_report_image(ctx, label, target):
    """Download and annotated report image locally."""
    image_url = ctx.provider.build_url("/api/v4/processing/actions/{id}/report_image/".format(id=ctx.processing_id))
    if ctx.verbose:
        click.echo("URL: {}".format(image_url))

    p = '{}_{}.jpeg'.format(ctx.processing_id, label)
    if os.path.isdir(target):
        p = os.path.join(target, p)

    filepath = download_file(image_url, p, label=label)
    click.echo('Saved to {}'.format(filepath))


@processing_action.command(name='realogram-report')
@click.option('-c', '--concurrency', default=4, help='Define how many parallel workers will be used to access API')
@click.option('-d', '--drop-duplicates', is_flag=True, default=False, help="Doesn't work for now")
@click.option('-t', '--target', type=click.Path(file_okay=False), default='.', help='Define specific folder where'
                                                                                    ' the report files will be saved')
@pass_rebotics_context
def processing_action_realogram_report(ctx, concurrency, drop_duplicates, target):
    """
    Function to download processing actions and extract preview from them.
    It will generate three files: scans.csv, realogram_report.csv, and oos_report.csv from given range or
    comma-separated processing action ids

    Typical usage is:

        retailer processing-action 1000-1005,1010-1015,1017 realogram-report


    Be careful with running the report two times, as it will override the data in folder
     if you have not specified the target folder
    """
    processing_action_ids = ctx.processing_id_list
    click.echo('downloading processing actions: {}'.format(processing_action_ids))
    with ThreadPoolExecutor(max_workers=min(concurrency, len(processing_action_ids))) as pool:
        pacs = pool.map(partial(task_download_processing_action, ctx), processing_action_ids)
    processing_actions = [p for p in pacs if p is not None]

    click.echo('Download complete! Generating files...')

    df_scans = pd.DataFrame(dtype=object)
    df_oos = pd.DataFrame(dtype=object)
    df_realogram = pd.DataFrame(dtype=object)

    for processing_action in processing_actions:
        df_bay_reports = pd.DataFrame(processing_action['shelf_bays'], columns=[
            'id',
            'store_planogram_id',
            'aisle',
            'section'
        ], dtype=str)
        realogram = processing_action['items']

        df_realogram_pac = pd.DataFrame(realogram, columns=[
            'unique_id',
            'on_shelf_position', 'display_shelf', 'shelf',
            'position',
            'x_min', 'y_min', 'x_max', 'y_max',
            'shelf_bay_id',
        ], dtype=str)

        df_realogram_pac['processing_action'] = processing_action['id']
        df_realogram_pac['store_id'] = processing_action['store_id']
        df_realogram_pac['store_name'] = processing_action['store_name']
        df_realogram_pac['store_number'] = processing_action['store']['custom_id']
        df_realogram_pac['created'] = processing_action['created']

        df_realogram_pac = df_realogram_pac.merge(
            df_bay_reports, left_on='shelf_bay_id', right_on='id'
        )
        df_realogram = df_realogram.append(df_realogram_pac)

        actions = processing_action.get('report_actions', [])
        oos = [a for a in actions if a['action'] == 'ACTION_ADD']
        df_oos_processing_action = pd.DataFrame(oos, columns=[
            'plu', 'from', 'to', 'from_aisle', 'to_aisle',
            'shelf_bay_id',
        ], dtype=object)

        df_oos_processing_action['processing_action'] = processing_action['id']
        df_oos_processing_action['store_id'] = processing_action['store_id']
        df_oos_processing_action['store_name'] = processing_action['store_name']
        df_oos_processing_action['store_number'] = processing_action['store'].get('custom_id')
        df_oos_processing_action['created'] = processing_action['created']
        df_oos_processing_action = df_oos_processing_action.merge(
            df_bay_reports, left_on='shelf_bay_id', right_on='id'
        )
        df_oos = df_oos.append(df_oos_processing_action)

        df_pac = pd.DataFrame([processing_action, ], columns=[
            'id', 'store_name', 'store_id', 'created', 'used_in_report',
            'category_name', 'category_number',
            'store_planogram_id', 'aisle', 'section',
            'download_report_url',
        ], index=['id'], dtype=object)
        df_pac['user'] = processing_action['user'].get('username', '')
        try:
            df_pac['compliance_rate'] = processing_action['compliance_rates'].get('compliance', '0')
        except Exception:
            df_pac['compliance_rate'] = 0
        df_pac['store_number'] = processing_action['store'].get('custom_id')
        df_scans = df_scans.append(df_pac)

    # if drop_duplicates:
    #     TODO: here should be user definable date or splittable. Extend the API
    # df_oos = df_oos.drop_duplicates(['store_number', 'plu', 'created'])

    dump_path = os.path.join(target, 'reporting_{}'.format(ctx.processing_id_string))
    mkdir_p(dump_path)

    df_realogram.to_csv(
        os.path.join(dump_path, 'realogram_report.csv'),
        quoting=csv.QUOTE_ALL,
        index=False
    )
    df_oos.to_csv(
        os.path.join(dump_path, 'oos_report.csv'),
        quoting=csv.QUOTE_ALL,
        index=False
    )
    df_scans.to_csv(
        os.path.join(dump_path, 'scans.csv'),
        quoting=csv.QUOTE_ALL,
        index=False
    )

    click.echo('Written to {}'.format(dump_path))


@processing_action.command()
@click.option('-t', '--target', type=click.Path(file_okay=False), default='.', help='Define specific folder where'
                                                                                    ' the reverse planogram file will be saved')
@pass_rebotics_context
def reverse_planogram(ctx, target):
    """Get CSV representation of the realogram in a reverse planogram format."""
    if ctx.verbose:
        click.echo("Downloading scan with id #{}".format(ctx.processing_id))

    scan = ctx.provider.processing_action_detail(ctx.processing_id)
    df = make_planogram_df(scan)

    p = 'reverse_planogram_{}.csv'.format(ctx.processing_id)
    if os.path.isdir(target):
        p = os.path.join(target, p)
    df.to_csv(p, index=False, quoting=csv.QUOTE_ALL)
    click.echo("Saved into {}".format(p))


@processing_action.command('spacial')
@click.option('-t', '--target', type=click.Path(file_okay=True, dir_okay=True), default=None,
              help="Save into file, if none provided, will print to STDOUT")
@pass_rebotics_context
def processing_spacial(ctx, target):
    """Download spacial result. Doesn't support multiple processing ids"""
    data = ctx.provider.get_spacial_data(ctx.processing_id)

    if target is None:
        # printing to STDOUT
        click.echo(json.dumps(data, indent=2))
        return

    target = Path(target)
    if target.is_dir():
        target /= "spacial_{}_{}.json".format(ctx.processing_id, datetime.now().strftime("%Y-%m-%d"))
    with open(target, 'w') as fout:
        json.dump(data, fout)
    click.echo("Saved into {}".format(target))


def download_processing_core_result(scan_id, ctx, target):
    scan_data = ctx.provider.get_scan_info(scan_id)  # processing_id is the scan id

    ctx.verbose_log(f"Scan data: {scan_data}")
    processing_action_id = scan_data['active_processing_action']
    task_list = ctx.provider.get_task_list_for_action(processing_action_id)

    ctx.verbose_log(f"Number of tasks are: {len(task_list)}")

    for i, task in enumerate(task_list):
        try:
            core_result = ctx.provider.get_core_result(processing_action_id, task['id'])
        except json.JSONDecodeError:
            ctx.verbose_log(f"Task {task['id']} has no core result...")
            continue

        if not core_result:
            click.echo("No core result for this scan")
            return

        if target is None:
            # printing to STDOUT
            click.echo(json.dumps(core_result, indent=2))
            return

        target = Path(target)
        if target.is_dir():
            if i == 0:
                target /= "core_result_{}_{}.json".format(scan_id, datetime.now().strftime("%Y-%m-%d"))
            if i > 0:
                target /= "core_result_{}_{}_{}.json".format(scan_id, i, datetime.now().strftime("%Y-%m-%d"))
        else:
            # because multiple processing action tasks can be downloaded, we need to append the task id to the file name
            target = Path(str(target).replace('.json', f'_{task["id"]}.json'))

        with open(target, 'w') as fout:
            json.dump(core_result, fout, indent=2)
        click.echo(f"Saved into {target.absolute()}")


@processing_action.command('core-result')
@click.option('-t', '--target', type=click.Path(file_okay=True, dir_okay=True), default=None,
              help="Save into file, if none provided, will print to STDOUT")
@click.option('-c', '--concurrency', default=4, help='Define how many parallel workers will be used to access API')
@pass_rebotics_context
def processing_core_result(ctx, target, concurrency):
    """Download core result for scan and save it into json file"""
    click_ctx = get_current_context()

    if target is not None:
        target = Path(target)
        if not target.is_dir():
            if target.suffix != '.json':
                click.echo("Target must be a directory or a json file")
                click_ctx.exit(1)
                return

            if len(ctx.processing_id_list) > 1:
                click.echo("Target must be a directory if you want to download in a batch")
                click_ctx.exit(1)
                return

    if len(ctx.processing_id_list) == 1:
        download_processing_core_result(ctx.processing_id, ctx, target)
        return

    ctx.verbose_log("Downloading core result for multiple scans")
    with ThreadPoolExecutor(max_workers=min(concurrency, len(ctx.processing_id_list))) as executor:
        for _ in executor.map(
            partial(download_processing_core_result, ctx=ctx, target=target),
            ctx.processing_id_list
        ):
            pass
    executor.shutdown(wait=True)


@processing_action.command('for-voting')
@click.option('-a', '--all-data', type=click.BOOL, is_flag=True, default=False,
              help='Flag to not filter realogram products without UPC from User')
@pass_rebotics_context
def processing_action_for_voting(ctx, all_data: bool):
    """
    Usage:
        retailer -r epsilon processing-action id1,id2,id3 for-voting -a
    """
    if len(ctx.processing_id_list) > 200:
        raise click.ClickException('The request is limited to 200 scans at a time.')

    ctx.verbose_log('Exporting scans/realogram products data...')
    try:
        response = ctx.provider.get_voting_data(ctx.processing_id_list, all_data)
    except ProviderHTTPClientException as exc:
        raise click.ClickException(str(exc))

    ctx.verbose_log('Successfully exported the following data:')
    ctx.format_result(response, force_format='json')


@api.group(name='fv')
def feature_vectors():
    """
    Feature vector flow
    """
    pass


@feature_vectors.command('list')
@pass_rebotics_context
def feature_vectors_list(ctx):
    fve = ctx.provider.feature_vectors_export()
    data = fve.get()
    if data:
        ctx.format_result(data)


@feature_vectors.command('export')
@click.option('-b', '--batch-size', type=click.INT, default=50000)
@click.option('-s', '--source-model', default='')
@click.option('-r', '--result-model', default='previews-backup')
@pass_rebotics_context
def feature_vectors_export(ctx, source_model, result_model, batch_size):
    fve = ctx.provider.feature_vectors_export()
    result = fve.export(source_model=source_model, result_model=result_model, batch_size=batch_size)
    ctx.format_result(result)


@api.group(name='copy')
def copy_group():
    """Various copy operations"""
    pass


def task_copy_scan(scan_id, ctx, from_retailer, store):
    try:
        processing_action_id = int(scan_id)
    except (ValueError, TypeError):
        ctx.verbose_log(f"Incorrect value for the id: {scan_id}")
        return

    source_provider = get_provider('retailer', from_retailer)
    ctx.verbose_log('Downloading processing action {}'.format(processing_action_id))
    data = source_provider.processing_action_detail(processing_action_id)

    files = []
    for input_object in data.get('inputs', []):
        # upload the input to the new retailer
        response = ctx.provider.processing_upload_by_reference(
            file_url=input_object['file'],
            input_type='image',
        )
        files.append(response['id'])

    ctx.verbose_log(f"Files: {files}")

    if store is None:
        store = data['store_id']
        ctx.verbose_log(f'Store is not provided, Copying to the same store {store}')
    else:
        store = int(store)

    copied_scan = ctx.provider.create_processing_action(
        store, files=files, input_type='image',
        aisle=data.get('aisle'),
        section=data.get('section'),
    )
    click.echo(f"Copied! {from_retailer}: {data['id']} -> {copied_scan['id']} {ctx.role}")


@copy_group.command('scans')
@click.option('-f', '--from-retailer', type=click.STRING,
              required=True, help='Retailer codename to copy from')
@click.option('-s', '--store', type=click.INT, default=None, required=False,
              help='Store ID to copy to. If left empty, will copy to the same store')
@click.option('-c', '--concurrency', type=click.INT, default=4,
              help='Count of parallel workers for API accessing')
@click.argument('scan_ids', required=True, type=click.STRING)
@pass_rebotics_context
def copy_group_scans(ctx, from_retailer, store, scan_ids, concurrency):
    """
    Copy scans from one retailer to another. Preferably using the same store from production to staging instances.
    usage:

    retailer -r qktpdev copy scans -f qktp -c 12 --store=123 <scan_ids in a format>

        1. 1-10  -- range from 1 to 10
        2. 1,2,3,4,5 --  scans separated by comma
        3. 1,2,3-5,6,7,8-10  -- partial ranges and comma separated values

    """
    # validate that from_retailer configuration is correct and exists in the system

    source_provider = get_provider('retailer', from_retailer)
    if source_provider is None:
        click.echo(
            f'Invalid retailer codename: {from_retailer}.\n'
            f'Run `retailer roles` to see all correct roles.\n'
            f'Or use `retailer -r {from_retailer} configure` to configure the role.\n'
            f'Consult with `retailer configure --help` or \n'
            f'`retailer set_token --help`',
            err=True)
        return

    scan_id_list = utils.parse_id_range_string(scan_ids)
    ctx.verbose_log(f"Processing scan_id list: {scan_id_list}")

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        pool.map(
            partial(task_copy_scan, ctx=ctx, from_retailer=from_retailer, store=store),
            scan_id_list
        )

    click.echo("Done!")


api.add_command(shell, 'shell')
api.add_command(roles, 'roles')
api.add_command(configure, 'configure')
api.add_command(set_token, 'set_token')
