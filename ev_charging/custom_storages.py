from storages.backends.s3boto3 import S3Boto3Storage

# Define custom storage classes for static and media files
# with specific locations in the S3 bucket.
class StaticStorage(S3Boto3Storage):
    location = "static"
    default_acl = "public-read"

class MediaStorage(S3Boto3Storage):
    location = "media"
    file_overwrite = False
    default_acl = "public-read"
