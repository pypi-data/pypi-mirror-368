import base64
import hmac
from collections import OrderedDict
from hashlib import sha256
from typing import TYPE_CHECKING

from rebotics_sdk.advanced import remote_loaders
from rebotics_sdk.providers import PageResult, ReboticsBaseProvider, remote_service

if TYPE_CHECKING:
    from requests.models import Response


class FVMProvider(ReboticsBaseProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.codename = None
        self.secret_key = None

    def set_retailer_identifier(self, codename: str, secret_key: str) -> None:
        self.headers['x-retailer-codename'] = codename
        self.headers['x-retailer-secret-key'] = secret_key
        self.codename = codename
        self.secret_key = secret_key

    @remote_service('/api/synchronization/')
    def send_products_file_to_fvm(self, retailer_codename: str, products_count: int, file_url: str) -> OrderedDict:
        json = {
            'retailer_codename': retailer_codename,
            'products_count': products_count,
            'file': file_url
        }
        return self.session.post(data=json)

    @remote_service('/api/token-auth/', raw=True)
    def token_auth(self, username, password, verification_code=None):
        payload = dict(
            username=username,
            password=password,
        )
        if verification_code is not None:
            payload['verification_code'] = verification_code

        response = self.session.post(data=payload)
        self.headers['Authorization'] = 'Token %s' % response.json()['token']
        return response

    @remote_service('/api/files/virtual/')
    def create_virtual_upload(self, filename):
        return self.session.post(
            json={
                "filename": filename
            }
        )

    @remote_service('/api/files/{pk}/finish/')
    def finish(self, pk):
        return self.session.post(pk=pk)

    def upload_file(self, file_io, filename, progress_bar=False):
        file_io.seek(0)
        request = self.create_virtual_upload(filename)
        remote_loaders.upload(
            request['destination'],
            file_io,
            progress_bar=progress_bar,
        )
        return self.finish(request['id'])

    @remote_service('/api/previews/{barcode}/')
    def get_preview_permalink(self, barcode):
        assert barcode.isdigit()
        url = self.build_url(self.session.url.format(barcode=barcode))
        if self.secret_key and self.codename:
            token = self.generate_token(url)
            return f'{url}?token={token}&codename={self.codename}'
        else:
            return url

    def generate_token(self, path):
        # You need this function to generate a token to use it, for example, in the authentication
        # You should call this function with an arg "path" for example: 'api/previews/'
        # With codename, path and secret_key, it will generate a token
        # Token will contain numbers, letters and symbols

        if self.secret_key is None or self.codename is None:
            raise AttributeError(
                "Identifiers for token generation are not present. Set secret_key and codename attributes or call .set_retailer_identifier method")
        lhmac = hmac.new(self.secret_key.encode('utf-8'), digestmod=sha256)
        string_to_sign = f'{self.codename}/{path}'
        lhmac.update(string_to_sign.encode('utf-8'))
        b64 = base64.urlsafe_b64encode(lhmac.digest())
        return b64

    @remote_service('/api/previews/')
    def upload_preview(self, barcode, image_url):
        return self.session.post(json={
            'barcode': barcode,
            'image_url': image_url
        })

    @remote_service('/api/products/')
    def get_products_list(self, page=1, page_size=100):
        params = {
            'page': page,
            'page_size': page_size,
        }
        return PageResult(self.session.get(params=params))

    @remote_service('/api/products/')
    def create_product(self, code, title):
        return self.session.post(json={
            'code': code,
            'title': title,
        })

    @remote_service('/api/products/{id}/')
    def update_product(self, id_, code, title):
        return self.session.put(
            id=id_,
            json={
                'code': code,
                'title': title,
            }
        )

    @remote_service('/api/rcdb/latest/')
    def get_latest_rcdb(self, model_codename, retailer_codename=None, with_images=False):
        payload = {
            'model_codename': model_codename,
            'with_images': with_images,
        }
        if retailer_codename is not None and self.codename is None:
            payload['retailer_codename'] = retailer_codename
        return self.session.post(json=payload)

    @remote_service('/api/rcdb/refresh/')
    def rcdb_refresh(self, model_codename, retailer_codename, with_images=False):
        # only admin can do that
        return self.session.post(json={
            'model_codename': model_codename,
            'retailer_codename': retailer_codename,
            'with_images': with_images,
        })

    @remote_service('/api/rcdb/{id}/')
    def get_rcdb_by_id(self, id_):
        return self.session.get(id=id_)

    @remote_service('/api/rcdb/')
    def save_rcdb(self, file_id, features_count, archive_size, model_codename, retailer_codename, with_images=False):
        return self.session.post(json={
            'file_id': file_id,
            'features_count': features_count,
            'archive_size': archive_size,
            'with_images': with_images,
            'model_codename': model_codename,
            'retailer_codename': retailer_codename,
        })

    @remote_service('/', raw=True, retries=5)
    def download(self, url, destination=None, progress_bar=False):
        if not url.startswith(self.host):
            url = self.build_url(url)

        def process_file_response(resp: 'Response', **request_arguments) -> None:
            downloaded_file = None
            if resp.ok:
                downloaded_file = remote_loaders.process_file_response(resp, destination, progress_bar)
            resp._downloaded_file = downloaded_file

        response = self.session.get(url=url, stream=True, hooks={'response': process_file_response})
        return response._downloaded_file  # noqa
