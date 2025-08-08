from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class File:
    """A class to manage S3 file as a local file.

    Parameters
    ----------
    path : str | Path
        The path of the file. A local path, path to the S3 (s3://...), or URL
        (http(s)://...) can be used.
    file_name : str | None
        The name of the file. If None, the name of the file is extracted from
        the path.
    profile_name : str | None
        AWS profile name.
    aws_access_key_id : str | None
        AWS access key id.
    aws_secret_access_key : str | None
        AWS secret access key.
    aws_session_token : str | None
        AWS session token.
    region_name : str | None
        AWS region name.
    role_arn : str | None
        AWS role arn for Assume role. If this is set, aws_access_key_id,
        aws_secret_access_key, aws_session_token are replaced by Assume role.
    session_name : str
        AWS session name. Default is "s3_reader".
    retry_mode : str
        Retry mode for failed requests. Default is "standard".
    max_attempts : int
        Maximum number of retry attempts for failed requests. Default is 10.
    max_trials : int
        Maximum number of trials to retry after retrieving credential error.
        Default is 10.

    """

    path: str | Path
    file_name: str | None = None
    profile_name: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_session_token: str | None = None
    region_name: str | None = None
    role_arn: str | None = None
    session_name: str = 's3_reader'
    retry_mode: str = 'standard'
    max_attempts: int = 10
    max_trials: int = 10

    def __post_init__(self) -> None:
        self.log = logging.getLogger(__name__)
        self.path = self.fix_path(self.path)
        self.orig_path = self.path
        self.load()

    def __del__(self) -> None:
        self.cleanup()

    def load(self) -> None:
        if self.file_name is None:
            self.file_name = Path(self.path).name
        self.temp_dir: tempfile.TemporaryDirectory[str] | None = None
        self.path = str(self.path)
        if self.path.startswith('s3:'):
            self.download_s3_file()
        elif self.path.startswith('http:') or self.path.startswith('https:'):
            self.download_http_file()

    def cleanup(self) -> None:
        if self.temp_dir is not None:
            self.temp_dir.cleanup()
            self.temp_dir = None

    @staticmethod
    def fix_path(path: str | Path) -> str:
        if not path:
            return ''
        # remove double slash during the path (other than starting of s3://)
        if ':/' in str(path):
            pathes = str(path).split(':/')
            return f'{pathes[0]}:/{Path(pathes[1])}'
        return str(Path(path))

    @staticmethod
    def extract_s3_info(path: str | Path) -> tuple[str, str]:
        path = str(path)
        split_path = path.split('/')
        bucket_name = split_path[2]
        key = '/'.join(split_path[3:])
        return bucket_name, key

    def download_s3_file(self) -> None:
        # boto3.session.Session(profile_name=self.s3_profile).resource("s3") uses random.
        # To avoid unnoticed change of random state, restore random state after the process.
        import random
        from time import sleep

        from boto3_session import Session
        from botocore.exceptions import ClientError, CredentialRetrievalError

        state = random.getstate()

        bucket_name, key = self.extract_s3_info(self.orig_path)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = f'{self.temp_dir.name}/{self.file_name}'

        err = None
        trials = 0
        while trials < self.max_trials:
            try:
                s3 = Session(
                    profile_name=self.profile_name,
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    aws_session_token=self.aws_session_token,
                    region_name=self.region_name,
                    role_arn=self.role_arn,
                    session_name=self.session_name,
                    retry_mode=self.retry_mode,
                    max_attempts=self.max_attempts,
                ).resource('s3')
                bucket = s3.Bucket(bucket_name)
                bucket.download_file(key, self.path)
                break
            except (CredentialRetrievalError, ClientError) as e:
                err = e
                self.log.debug(
                    'Failed to retrieve credentials. Retrying to download the file.'
                )
                trials += 1
                sleep(1)
                continue
        else:
            msg = f'Failed to download the file: {self.orig_path}.'
            self.log.error(msg)
            if err is not None:
                raise err
            msg = 'Unknown error occurred. Failed to download the file.'
            raise ValueError(msg)

        random.setstate(state)

    def download_http_file(self) -> None:
        import urllib.request

        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = f'{self.temp_dir.name}/{self.file_name}'

        if not self.orig_path.startswith(('http:', 'https:')):
            msg = f'The path should start with http: or https:. (path={self.orig_path})'
            raise ValueError(msg)
        with (
            urllib.request.urlopen(self.orig_path) as orig_file,  # noqa: S310
            Path(self.path).open('wb') as dest_file,
        ):
            dest_file.write(orig_file.read())
