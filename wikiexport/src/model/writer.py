from typing import Iterable, Tuple
from datetime import  datetime
from os import path
from urllib import parse

from src.utils import repeat_if_exception

import boto3


class Writer:
    @classmethod
    def instantiate_writer(cls, output_path: str, aws_access_key_id: str = None, aws_secret_access_key: str = None) -> 'Writer':
        if aws_secret_access_key and aws_access_key_id:
            return S3Writer(s3_dir_path=output_path, aws_access_key_id= aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key)
        else:
            return LocalWriter(output_path)

class LocalWriter(Writer):

    FILE_PATTERN = '%Y%m%dT%H:%M:%S'
    HEADER = 'domain,page_title,pageview_count\n'

    def __init__(self, output_dir):
        self.output_dir = output_dir

    @repeat_if_exception(message='Something went wrong when writing data in local storage', nb_times=3)
    def write_pageviews(self, pageviews: Iterable['Pageview'], dt: datetime) -> str:
        file_name = f'{dt.strftime(self.FILE_PATTERN)}.csv'
        file_path = path.join(self.output_dir, file_name)
        with open(file_path, 'wt') as f:
            f.write(self.HEADER)
            for pageview in pageviews:
                f.write(f'{pageview.domain},{pageview.page_title},{pageview.view_count}\n')

        return file_path

class S3Writer(LocalWriter):

    LOCAL_PATH = '/tmp'

    def __init__(self, s3_dir_path: str, aws_access_key_id: str, aws_secret_access_key: str) -> None:
        super().__init__(output_dir=S3Writer.LOCAL_PATH)
        self.s3_dir_path = s3_dir_path
        self.s3_client = boto3.Session(aws_access_key_id=aws_access_key_id,
                                       aws_secret_access_key=aws_secret_access_key).client('s3')

    @repeat_if_exception(message='Something went wrong when writing data to S3', nb_times=3)
    def write_pageviews(self, pageviews: Iterable['Pageview'], dt: datetime) -> str:
        local_file_path = super().write_pageviews(pageviews, dt)
        bucket, object_name = self._get_bucket_and_object(dt)
        self.s3_client.upload_file(local_file_path, bucket, object_name)
        return f'{bucket}/{object_name}'

    def _get_bucket_and_object(self, dt: datetime) -> Tuple[str, str]:
        parsed_url = parse.urlparse(self.s3_dir_path)
        bucket, dir_path = parsed_url.netloc, parsed_url.path
        dt_str = dt.strftime(S3Writer.FILE_PATTERN)
        return bucket, f'{dir_path}/{dt_str}'