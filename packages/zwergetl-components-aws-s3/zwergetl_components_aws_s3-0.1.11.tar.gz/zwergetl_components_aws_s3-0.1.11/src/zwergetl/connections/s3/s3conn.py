import io
import json

from zwergetl.engine.connections import Connection
import boto3
from botocore.config import Config


class S3Connection(Connection):
    """
    Provides connection to S3.

    :param conn_id: String identifier of the connection within the graph
    :param endpoint_url: endpoint URL
    :param region_name: region name
    :access_key_id: key id
    :secret_access_key: access key
    :config: an object of type botocore.config.Config if additional config parameters are required
    """
    def __init__(
        self,
        conn_id:str,
        endpoint_url:str,
        region_name:str,
        access_key_id:str,
        secret_access_key:str,
        config:Config=None
    ):
        super().__init__(conn_id, host="", port="", database="", username="", password="")
        self.endpoint_url = endpoint_url
        self.region_name = region_name
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.config = config
        
        # internal variables
        self.s3_client = None


    def get_conn(self):
        """Returns a boto3.client object."""

        if self.s3_client is None:
            self.s3_client = boto3.client(
                's3',
                endpoint_url = self.endpoint_url,
                region_name = self.region_name,
                aws_access_key_id = self.access_key_id,
                aws_secret_access_key = self.secret_access_key,
                config=self.config
            )

        return self.s3_client

