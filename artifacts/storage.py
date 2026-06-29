from storages.backends.s3boto3 import S3Boto3Storage
from botocore.exceptions import ClientError

class ARS3Storage(S3Boto3Storage):
    """
    Custom S3 storage to force correct MIME types for 3D models.
    """
    def get_object_parameters(self, name):
        params = super().get_object_parameters(name).copy()
        
        # Force MIME types based on file extension
        if name.lower().endswith('.glb'):
            params['ContentType'] = 'model/gltf-binary'
        elif name.lower().endswith('.usdz'):
            params['ContentType'] = 'model/vnd.usdz+zip'
            
        return params

    def exists(self, name):
        try:
            return super().exists(name)
        except ClientError as e:
            # S3/MinIO returns 403 Forbidden/AccessDenied for HeadObject if the object does not exist
            # and the user does not have ListBucket or GetObject permission on the path,
            # or if there is a proxy-related signature mismatch on HEAD requests.
            # In these cases, we safely treat the file as not existing so that django-storages can write it.
            code = e.response.get('Error', {}).get('Code', '')
            status_code = e.response.get('ResponseMetadata', {}).get('HTTPStatusCode', 0)
            if code in ('403', 'AccessDenied', 'Forbidden', 'SignatureDoesNotMatch') or status_code == 403:
                return False
            raise

    def url(self, name, parameters=None, expire=None):
        url = super().url(name, parameters, expire)
        import os
        public_url = os.getenv("AWS_S3_PUBLIC_URL")
        if public_url:
            internal_url = os.getenv("AWS_S3_ENDPOINT_URL")
            if internal_url and internal_url in url:
                url = url.replace(internal_url, public_url)
        return url

