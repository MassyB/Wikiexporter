from typing import Iterable, Tuple
from datetime import  datetime
from os import path
from urllib import parse
from abc import ABC, abstractmethod

from src.utils import repeat_if_exception

import boto3


class Writer(ABC):
    """
    This class is responsible of writing CSV to storage
    """

    HEADER = 'domain,page_title,pageview_count'
    FILE_PATTERN = '%Y%m%dT%H:%M:%S'


    @classmethod
    def instantiate_writer(cls, output_path: str, aws_access_key_id: str = None,
                           aws_secret_access_key: str = None) -> 'Writer':
        """ A factory method to choose which type of Writer to instantiate. If AWS credentials are not null
        priority is given to S3Writer

        :param: output_path: path where to save the result CSV can be local or on S3 dir path (s3://mybucket/my_dir
        """

        if aws_secret_access_key and aws_access_key_id:
            return S3Writer(s3_dir_path=output_path, aws_access_key_id= aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key)
        else:
            return LocalWriter(output_path)


    @abstractmethod
    def write_pageviews(self, pageviews: Iterable['Pageview'], dt: datetime) -> str:
        """ Abstract method to write pageviews to storage

        :param pageviews: collection of pageviews
        :param dt: datetime of the request
        :return: path where the CSV is saved
        """

        pass


class LocalWriter(Writer):
    """
    Class that writes CSV files in local storage
    """


    def __init__(self, output_dir: str) -> None:
        """ instantiates a new LocalWriter

        :param output_dir: directory where to wright the resulting CSV
        """

        self.output_dir = output_dir if not output_dir.endswith('/') else output_dir[:-1]


    @repeat_if_exception(message='Something went wrong when writing data in local storage', nb_times=3)
    def write_pageviews(self, pageviews: Iterable['Pageview'], dt: datetime) -> str:
        """ Write the pageviews in local storage

        :param pageviews: collection of pagesviews
        :param dt: datetime of the request
        :return: path where the pageviews were written
        """

        file_name = f'{dt.strftime(self.FILE_PATTERN)}.csv'
        file_path = path.join(self.output_dir, file_name)
        with open(file_path, 'wt') as f:
            f.write(f'{self.HEADER}\n')
            for pageview in pageviews:
                f.write(f'{pageview.domain},{pageview.page_title},{pageview.view_count}\n')

        return file_path


class S3Writer(Writer):
    """
    Class that writes CSV files in S3 without staging data in local storage
    """


    def __init__(self, s3_dir_path: str, aws_access_key_id: str, aws_secret_access_key: str) -> None:
        """

        :param s3_dir_path: the bucket and direcory where to save CSV files. Example: s3://mybucket/mydir
        :param aws_access_key_id:
        :param aws_secret_access_key:
        """

        self.s3_dir_path = s3_dir_path if not s3_dir_path.endswith('/') else s3_dir_path[:-1]
        self.s3_client = boto3.Session(aws_access_key_id=aws_access_key_id,
                                       aws_secret_access_key=aws_secret_access_key).client('s3')


    @repeat_if_exception(message='Something went wrong when writing data to S3', nb_times=3)
    def write_pageviews(self, pageviews: Iterable['Pageview'], dt: datetime) -> str:
        """ Write objects to S3 without saving them in local storage.

        :param pageviews: collection of pageviews
        :param dt: datetime of the request
        :return: S3 path of the newly uploaded object
        """

        csv_lines = [S3Writer.HEADER] + list(f'{pageview.domain},{pageview.page_title},{pageview.view_count}'
                                             for pageview in pageviews)
        csv_content = '\n'.join(csv_lines)
        bucket, object_name = self._get_bucket_and_object(dt)
        object_path = f's3://{bucket}/{object_name}'
        response = self.s3_client.put_object(Body=csv_content, Bucket=bucket, Key=object_name)

        if response.get('ResponseMetadata').get('HTTPStatusCode', None) != 200:
            raise Exception(f'Object upload to {object_path} failed')

        return object_path


    def _get_bucket_and_object(self, dt: datetime) -> Tuple[str, str]:
        """ Computes the bucket name and object path

        :param dt: datetime of the request
        :return: bucket, object path in the bucket
        """

        parsed_url = parse.urlparse(self.s3_dir_path)
        bucket, dir_path = parsed_url.netloc, parsed_url.path[1:]
        dt_str = dt.strftime(S3Writer.FILE_PATTERN)

        return bucket, f'{dir_path}/{dt_str}.csv'
