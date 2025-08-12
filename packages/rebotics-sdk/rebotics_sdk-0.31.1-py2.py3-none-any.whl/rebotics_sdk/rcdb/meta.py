import typing
from datetime import datetime, timezone

from pydantic import BaseModel, field_validator, model_validator

import rebotics_sdk


# `model_` is the protected namespace, so to supress warnings on `model_type` and `model_codename` doing this
BaseModel.model_config['protected_namespaces'] = ()


# noinspection PyNestedDecorators
class Metadata(BaseModel):
    packed: typing.Optional[str] = datetime.now().isoformat()  # datetime of packing in %c format
    model_type: typing.Optional[str] = None
    model_codename: typing.Optional[str] = None
    sdk_version: typing.Optional[str] = rebotics_sdk.__version__
    core_version: typing.Optional[str] = None
    fvm_version: typing.Optional[str] = None
    packer_version: typing.Optional[int] = 0
    count: int = 0
    batch_size: int = 0
    images_links_expiration: typing.Optional[datetime] = None  # iso data format

    additional_files: typing.Optional[typing.List[typing.List[str]]] = None  # additional files in archive
    images: typing.Optional[typing.List[str]] = None  # images in archive

    # new field for metadata
    files: typing.List[dict] = []

    @field_validator('images_links_expiration')
    @classmethod
    def make_images_links_expiration_aware(cls, images_links_expiration: typing.Optional[datetime]
                                           ) -> typing.Optional[datetime]:
        if images_links_expiration is None:
            return None

        if images_links_expiration.utcoffset() is None:
            images_links_expiration = images_links_expiration.replace(tzinfo=timezone.utc)

        return images_links_expiration

    @model_validator(mode='after')
    def compute_model_type(self):
        if not self.model_type:
            codename = self.model_codename or ''
            if 'arcface' in codename:
                self.model_type = 'arcface'
            else:
                self.model_type = 'facenet'
        return self
