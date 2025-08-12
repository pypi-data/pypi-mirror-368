from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class ModelDataExchangeS3Storage(S3Boto3Storage):
    def __init__(self, base_dir="", *args, **kwargs):
        kwargs["bucket_name"] = settings.MODEL_DATA_EXCHANGE_S3_BUCKET_NAME
        super().__init__(*args, **kwargs)
        base_path = getattr(settings, "MODEL_DATA_EXCHANGE_S3_BASE_PATH", "")
        self.location = f"{base_path}/{base_dir}" if base_path else base_dir
