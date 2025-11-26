from storages.backends.s3boto3 import S3Boto3Storage

class S3StaticStorage(S3Boto3Storage):
    location = "static"
    default_acl = None

class S3MediaStorage(S3Boto3Storage):
    location = "media"
    file_overwrite = False
    default_acl = None
