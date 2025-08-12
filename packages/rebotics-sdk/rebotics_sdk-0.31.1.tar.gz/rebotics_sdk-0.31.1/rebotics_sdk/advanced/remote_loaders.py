import os
from collections import OrderedDict
from io import BytesIO
from typing import BinaryIO

import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from tqdm import tqdm


class ProgressBar(tqdm):

    def update_to(self, n):
        """
        identical to update, except `n` should be current value and not delta.
        """
        self.update(n - self.n)


PRESERVED_ORDER_V1 = ("policy", "AWSAccessKeyId", "key", "signature")
PRESERVED_SIGNATURE_V4 = (
    "key", "success_action_status",
    "policy", "x-amz-credential", "x-amz-algorithm",
    "x-amz-date", "x-amz-signature"
)
HTTP_TIMEOUTS = (30, 60)  # first is connection, second is for reading


def _order_upload_keys(fields, keys):
    output_fields = OrderedDict()
    for key in keys:
        if fields.get(key):
            output_fields[key] = fields[key]
    return output_fields


def format_request_body(fields):
    if len(fields.keys()) == 0:
        return fields
    elif set(fields.keys()).issubset(set(PRESERVED_ORDER_V1)):
        return _order_upload_keys(fields, PRESERVED_ORDER_V1)
    elif set(fields.keys()).issubset(set(PRESERVED_SIGNATURE_V4)):
        return _order_upload_keys(fields, PRESERVED_SIGNATURE_V4)
    else:
        return fields


def upload(destination: dict, file: BinaryIO, progress_bar: bool = False,
           filename: str = 'features_backup.rcdb') -> requests.Response:
    """

    :param dict destination: an S3 presigned upload object
    :param file: File-like object that has read
    :param progress_bar: display progress bar or not
    :param str filename: name of file when doing the upload
    :return:
    """
    url = destination["url"]
    provider = destination.get('provider', 'aws-s3')
    if provider not in {'aws-s3', 'azure-blob', 'aws-s3-put'}:
        raise ValueError('File upload destination is not configured')  # Don't ignore if provider is incorrect

    if provider == 'aws-s3':
        fields = destination.get('fields', None)
        if fields is None:
            fields = dict()

        # apply sorting required for the AWS
        fields = format_request_body(fields)

        fields["file"] = (filename, file)
        encoder = MultipartEncoder(fields=fields)

        headers = {"Content-Type": encoder.content_type}
        headers.update(destination.get('headers', {}))

        if not progress_bar:
            return requests.post(
                url,
                data=encoder,
                headers=headers,
                timeout=HTTP_TIMEOUTS,
            )

        with ProgressBar(total=encoder.len, unit="bytes", unit_scale=True, leave=False) as bar:
            monitor = MultipartEncoderMonitor(
                encoder,
                lambda monitor: bar.update_to(monitor.bytes_read)
            )
            return requests.post(
                url,
                data=monitor,
                headers=headers,
                timeout=HTTP_TIMEOUTS,
            )
    elif provider == 'azure-blob' or provider == 'aws-s3-put':
        if not progress_bar:
            return requests.put(
                url,
                data=file,
                headers=destination.get('headers'),
                timeout=HTTP_TIMEOUTS,
            )

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        with tqdm.wrapattr(file, 'read', total=file_size) as wrapped_file:
            return requests.put(
                url,
                data=wrapped_file,
                headers=destination.get('headers'),
                timeout=HTTP_TIMEOUTS,
            )


def download(source, destination=None, progress_bar=False):
    r = requests.get(
        source,
        stream=True,
        allow_redirects=True,
        timeout=HTTP_TIMEOUTS,
    )
    r.raise_for_status()
    return process_file_response(r, destination, progress_bar)


def process_file_response(response, destination, progress_bar=False):
    is_file = False

    if destination is None:
        fp = BytesIO()
    elif hasattr(destination, 'write') and hasattr(destination, 'read'):
        # it is a file-like object
        fp = destination
    else:
        fp = open(destination, 'wb')
        is_file = True

    content_length = response.headers.get('content-length')
    if content_length:
        total_length = int(content_length)
    else:
        total_length = 0
        progress_bar = False

    chunk, chunk_size = 1, 1024

    for chunk in tqdm(
        response.iter_content(chunk_size), leave=False, disable=not progress_bar,
        unit='iB', unit_scale=True, miniters=1, unit_divisor=1024, total=total_length,
    ):
        fp.write(chunk)

    if is_file:
        fp.close()
        return destination
    return fp
