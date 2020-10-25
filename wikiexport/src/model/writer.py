from typing import Iterable, Tuple
from datetime import  datetime
from os import path
import boto3

class Writer:
    @classmethod
    def get_writer(cls, output_path: str) -> 'Writer':
        pass


class LocalWriter(Writer):

    FILE_PATTERN = '%Y%m%dT%H:%M:%S'
    HEADER = 'domain,page_title,pageview_counts\n'

    def __init__(self, output_dir):
        self.output_dir = output_dir

    def write_pageviews(self, pageviews: Iterable['Pageview'], dt: datetime) -> str:
        file_name = f'{dt.strftime(self.FILE_PATTERN)}.csv'
        file_path = path.join(self.output_dir, file_name)
        with open(file_path, 'wt') as f:
            f.write(self.HEADER)
            for pageview in pageviews:
                f.write(f'{pageview.domain},{pageview.page_title},{pageview.view_counts}\n')

        return file_path

class S3Writer(LocalWriter):

    LOCAL_PATH = '/tmp'

    def __init__(self, s3_dir_path: str) -> None:
        super().__init__(output_dir=S3Writer.LOCAL_PATH)
        self.s3_dir_path = s3_dir_path
        self.s3_client = boto3.client('s3')

    def write_pageviews(self, pageviews: Iterable['Pageview'], dt: datetime) -> None:
        local_file_path = super().write_pageviews(pageviews, dt)
        bucket, object_name = self._get_bucket_and_object(dt)
        self.s3_client.upload_file(local_file_path, bucket, object_name)

    def _get_bucket_and_object(self, dt: datetime) -> Tuple[str, str]:
        pass