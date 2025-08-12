class RCDB:
    EXPORT_CREATED = 'EXPORT_CREATED'
    EXPORT_DONE = 'EXPORT_DONE'
    EXPORT_IN_PROGRESS = 'EXPORT_IN_PROGRESS'
    EXPORT_ERROR = 'EXPORT_ERROR'

    EXPORT_STATUS_CHOICES = (
        (EXPORT_CREATED, "Export created"),
        (EXPORT_IN_PROGRESS, "Export in progress"),
        (EXPORT_DONE, "Export Done"),
        (EXPORT_ERROR, "Export error"),
    )

    ZIP = 'zip'
    CLASSIFICATION_DATABASE = 'rcdb'
    VIRTUAL_CLASSIFICATION_DATABASE = 'vrcdb'
    JSON = 'json'

    EXTENSION_CHOICES = (
        (ZIP, 'zip archive'),
        (CLASSIFICATION_DATABASE, 'Rebotics database format'),
        (VIRTUAL_CLASSIFICATION_DATABASE, 'Rebotics virtual database format'),
        (JSON, "Flat json of image urls and labels"),
    )

    FEATURE_VECTORS = 'feature_vectors'
    FEATURE_PREVIEWS = 'feature_previews'
    HEAT_MAP = 'heat_map'
    SIZES = 'sizes'
    BACKUP_TYPES = (
        (FEATURE_VECTORS, 'Feature Vectors'),
        (FEATURE_PREVIEWS, 'Feature vectors + Previews'),
        (HEAT_MAP, 'Heat map information'),
        (SIZES, 'Sizes information'),
    )


class DownloadImagesFormat(object):
    FULL = "full"
    IMAGES = "images"
    ANNOTATIONS = "annotations"
    OPTIONS = [
        FULL,
        IMAGES,
        ANNOTATIONS,
    ]


class CvatTaskPriority:
    LOWEST = 10
    LOW = 20
    MEDIUM = 30
    HIGH = 40
    HIGHEST = 50
    OPTIONS = {
        'lowest': LOWEST,
        'low': LOW,
        'medium': MEDIUM,
        'high': HIGH,
        'highest': HIGHEST,
    }


CVAT_EXPORT_WORKSPACE = 'RetechLabs'


class RCDBBaseFileNames:
    LABELS = 'labels.txt'
    FEATURES = 'features.txt'
    FEATURES_BINARY = 'features.eba'
    META = 'meta.json'


class CameraGroupActionStatusType:
    CREATED = 'CR'
    PENDING = 'PD'
    EXECUTED = 'EX'

    CHOICES = (CREATED, PENDING, EXECUTED,)
