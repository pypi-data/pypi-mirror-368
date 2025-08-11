import logging
import io
import csv
from zwergetl.engine.edges import Edge
from zwergetl.engine.nodes import Node
from zwergetl.engine.nodes import NodeConfigError
from zwergetl.engine.enums import Result
from zwergetl.engine.exceptions import FileNotFoundException
from botocore.exceptions import ClientError

# This metadata is used to output missing files
MISSING_FILES_STANDARD_METADATA = [
    {'name': 'source_file_path', 'type': 'string'},
]

class S3CopyFilesDirect(Node):
    """ Copies files between S3 folders of buckets without downloading them. A list of files
        must come into input port 0. Field 0 must contain source file path,
        field 1 - target file path. Source and target bucket names must be specified
        as parameters.
    """
    def __init__(
        self,
        node_id,
        graph,
        s3_conn_id,
        source_bucket_name,
        target_bucket_name,
        skip_missing_files=True # if False, will stop with error
    ):
        super().__init__(node_id, graph)
        self.s3_conn_id = s3_conn_id
        self.source_bucket_name = source_bucket_name
        self.target_bucket_name = target_bucket_name
        self.skip_missing_files = skip_missing_files

    def check_config(self):
        # one output edge
        try:
            p = self.get_input_port(0)
        except KeyError:
            raise NodeConfigError("Input port 0 is not assigned.")


    def execute(self)->int:
        """
        Reads records from input port 0 and copies each source file specified in 
        field 0 to the target filename specified in field 1.
        """
        conn = self.graph.get_connection(self.s3_conn_id)

        client = conn.get_conn()

        res = Result.FINISHED_OK
        input_port = self.get_input_port(0)
        input_rec = None
        input_rec = input_port.read_record(input_rec)

        missing_files_port = self.output_ports.get(1)
        if missing_files_port is not None:
            if missing_files_port.metadata is None:
                missing_files_port.metadata = MISSING_FILES_STANDARD_METADATA

        # array of one value that is used to output missing records
        # to output port 1
        myrow = [None]
                

        # TODO: check correctness of metadata
        while input_rec and not self.is_stop_it():
            source_key = input_rec[0];
            target_key = input_rec[1];
            # Define the source object
            copy_source = {
                'Bucket': self.source_bucket_name,
                'Key': source_key
            }

            # Perform the copy
            try:
                client.copy(
                    CopySource=copy_source,
                    Bucket=self.target_bucket_name,
                    Key=target_key
                )
            except ClientError as e:
                error_response = e.response
                error_code = error_response['Error']['Code']
                #print(type(error_code))
                #print("Error code: " + error_code)
                if error_code == "404":
                    if self.skip_missing_files is True:
                        # just continue
                        #print("File not found: " + source_key)
                        logging.debug("File not found: " + source_key)
                        if missing_files_port is not None:
                            myrow[0] = source_key
                            missing_files_port.write_record(myrow)

                    else:
                        raise FileNotFoundException("File " + source_key + " not found.")
                else:
                    # all other ClientError exceptions will pop up here
                    raise
            
            
            input_rec = input_port.read_record(input_rec)

        return res
    

    def set_output_node_for_missing_files(self, node, metadata=None):
        """
        Connects the output port 1 of this node to
        the input port 0 of the next node.

        :param node: the downstream node that will be receiving the output of
            this node on input port 0
        :param metadata: metadata for the output port. If not specfied,
            metadata is created automatically by this node.
        """
        edge = Edge(metadata)
        self.graph.add_node(node)
        self.set_output_port(edge, 1)
        node.set_input_port(edge, 0)
