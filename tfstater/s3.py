import boto3

from botocore.client import Config
from emmett_crypto.symmetric import encrypt_b64, decrypt_b64

from . import app
from .helpers import run_in_loop

s3client = boto3.resource(
    "s3",
    endpoint_url=app.config.object_storage.endpoint,
    region_name=app.config.object_storage.region,
    aws_access_key_id=app.config.object_storage.access_key,
    aws_secret_access_key=app.config.object_storage.secret_key,
    config=Config(
        signature_version="s3v4"
    )
)
s3bucket = s3client.Bucket(app.config.object_storage.bucket)


async def list_path_contents(path):
    if app.config.object_storage.path_prefix:
        path = f"{app.config.object_storage.path_prefix}/{path}"
    objs = await run_in_loop(
        list,
        args=[
            s3bucket.objects.filter(Prefix=path)
        ]
    )
    return [obj.key[len(path) + 1:] for obj in objs]


def put_object(key: str, obj: bytes):
    if app.config.object_storage.path_prefix:
        key = f"{app.config.object_storage.path_prefix}/{key}"
    if app.config.object_storage.encrypt_data:
        obj = encrypt_b64(obj, app.config.auth.hmac_key).encode("utf8")
    return run_in_loop(
        s3bucket.put_object,
        kwargs={"Key": key, "Body": obj}
    )


def _obj_reader(key: str) -> bytes:
    obj = s3bucket.Object(key).get()
    return obj["Body"].read()


async def get_object(key: str) -> bytes:
    if app.config.object_storage.path_prefix:
        key = f"{app.config.object_storage.path_prefix}/{key}"
    rv = await run_in_loop(_obj_reader, args=[key])
    if app.config.object_storage.encrypt_data:
        rv = decrypt_b64(app.config.auth.hmac_key)
    return rv
