import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Pool
from urllib.parse import urlparse, unquote

import click
import tqdm

from rebotics_sdk.advanced import remote_loaders
from rebotics_sdk.cli.renderers import format_processing_action_output
from rebotics_sdk.utils import download_file


class GroupWithOptionalArgument(click.Group):
    def parse_args(self, ctx, args):
        if args:
            if args[0] in self.commands:
                if len(args) == 1 or args[1] not in self.commands:
                    args.insert(0, '')
        super(GroupWithOptionalArgument, self).parse_args(ctx, args)


def task_runner(ctx, task_func, ids, concurrency, **kwargs):
    task_arguments = []

    for id_ in ids:
        arguments = {
            'ctx': ctx,
            'id': id_,
        }
        arguments.update(kwargs)
        task_arguments.append(arguments)

    with ThreadPoolExecutor(max_workers=min(concurrency, len(task_arguments))) as pool:
        data_list = list(pool.map(task_func, task_arguments))

    format_processing_action_output(data_list, ctx.format)


def download_file_from_dict(d):
    ctx = d['ctx']
    if ctx.verbose:
        click.echo('>> Downloading file into %s' % d['filepath'], err=True)
    result = download_file(d['url'], d['filepath'])
    click.echo('<< Downloaded file into %s' % d['filepath'], err=True)
    return result


class UnrecognizedInputTypeByExtension(Exception):
    pass


def guess_input_type(ext):
    if ext.startswith('.'):
        ext = ext.strip('.')
    if ext in [
        'jpeg', 'jpg', 'png',
    ]:
        return 'image'
    elif ext in [
        'mp4', 'mov', 'avi'
    ]:
        return 'video'
    else:
        raise UnrecognizedInputTypeByExtension('File with extension %s is given' % ext)


def fetch_scans(ctx, processing_ids):
    processing_actions_list = []
    with ThreadPoolExecutor(max_workers=len(processing_ids)) as executor:
        futures = [executor.submit(ctx.provider.processing_action_detail, scan_id) for scan_id in processing_ids]
        for future in tqdm.tqdm(
            as_completed(futures),
            total=len(processing_ids),
            desc='Fetching scans',
            disable=not ctx.do_progress_bar(),
        ):
            processing_actions_list.append(future.result())
    return processing_actions_list


def downloads_with_threads(ctx, files, concurrency):
    with ThreadPoolExecutor(concurrency) as executor:
        futures = [
            executor.submit(remote_loaders.download, file[0], file[1])
            for file in files
        ]
        for _ in tqdm.tqdm(
            as_completed(futures), total=len(files), desc='Downloading files', disable=not ctx.do_progress_bar()
        ):
            pass


def refresh_urls_in_threads(ctx, file_urls):
    results = []
    refresh_url_func = ctx.provider.refresh_url

    with ThreadPoolExecutor(min(32, len(file_urls))) as executor:
        futures = [
            executor.submit(refresh_url_func, file_url)
            for file_url in file_urls
        ]
        for future in tqdm.tqdm(
            as_completed(futures),
            leave=False,
            total=len(file_urls),
            desc='Refreshing urls',
            disable=not ctx.do_progress_bar()
        ):
            results.append(future.result()['url'])
    return results


def run_with_processes(invoked, iterable, concurrency):
    with Pool(min(concurrency, len(iterable))) as pool:
        for _ in tqdm.tqdm(
            pool.starmap(invoked, iterable)
        ):
            pass
        pool.close()
        pool.join()


def get_segmentation(segmentation_filepath):
    with open(segmentation_filepath, 'r') as fd:
        segmentation_file = json.load(fd)
    return segmentation_file['per_image']


def get_segmentation_mode(segmentation):
    mode = 'items'
    if segmentation[0].get('remote_url') is not None:
        mode = 'remote_url'
    return mode


def save_masks(ctx, root_folder, urls):
    path_to_save_masks = root_folder / 'all_masks'
    path_to_save_masks.mkdir(parents=True, exist_ok=True)

    list_with_downloaded_mask = [
        [url, path_to_save_masks / str(urlparse(unquote(url)).path).lstrip('/').split('/')[-1]]
        for url in urls
    ]

    downloads_with_threads(ctx, list_with_downloaded_mask, concurrency=len(list_with_downloaded_mask))
