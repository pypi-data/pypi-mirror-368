import sys
if "pytest" in sys.modules:
    from s3_bucket.S3Bucket import S3Bucket
else:
    from bgp_data_interface.s3_bucket.S3Bucket import S3Bucket

import pandas as pd
from typing import Dict, Any

class S3:

    _s3bucket: S3Bucket

    def __init__(self, access_key: str, secret_key: str, bucket: str) -> None:
        self._s3bucket = S3Bucket(access_key, secret_key, bucket)

    def retrieve(self, params: Dict[str, Any]={}) -> pd.DataFrame:
        return self._s3bucket.retrieve(params)

    def store(self, data: pd.DataFrame, key: str) -> None:
        self._s3bucket.store(data, key)

    def object_exists(self, key: str) -> bool:
        return self._s3bucket.object_exists(key)

    def delete_object(self, key: str) -> None:
        self._s3bucket.delete_object(key)
