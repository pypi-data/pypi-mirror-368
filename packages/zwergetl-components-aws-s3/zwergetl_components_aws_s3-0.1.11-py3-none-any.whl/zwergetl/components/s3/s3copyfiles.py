import logging
import io
import os
import uuid
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

class S3CopyFiles(Node):
    """ Copies files between S3 folders of buckets in two steps:
        First - downloads a file to a temporary folder,
        then - uploads downloaded file to the target bucket.
        A list of files must come into input port 0. Field 0 must contain source file path,
        field 1 - target file path. Source and target bucket names must be specified
        as parameters.
    """
    def __init__(
        self,
        node_id,
        graph,
        source_s3_conn_id,
        target_s3_conn_id,
        source_bucket_name,
        target_bucket_name,
        temp_folder_path,
        skip_missing_files=True # if False, will stop with error
    ):
        super().__init__(node_id, graph)
        self.source_s3_conn_id = source_s3_conn_id
        self.target_s3_conn_id = target_s3_conn_id
        self.source_bucket_name = source_bucket_name
        self.target_bucket_name = target_bucket_name
        self.temp_folder_path = temp_folder_path
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
        src_conn = self.graph.get_connection(self.source_s3_conn_id)
        tgt_conn = self.graph.get_connection(self.target_s3_conn_id)

        src_client = src_conn.get_conn()
        tgt_client = tgt_conn.get_conn()

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
                
        # set up a name for the temporary file. The name is a random uuid.
        # The name is reused for all files being copied during the job
        #temp_file_name = str(uuid.uuid4())
        #temp_file_path = os.path.join(self.temp_folder_path, temp_file_name)

        # TODO: check correctness of metadata
        while input_rec and not self.is_stop_it():
            source_key = input_rec[0];
            target_key = input_rec[1];

            #fn, ext = os.path.splitext(source_key)
            base_file_name = os.path.basename(source_key)
            #temp_file_name_with_ext = temp_file_name + ext
            temp_file_path = os.path.join(self.temp_folder_path, base_file_name)

            # Download
            try:
                src_client.download_file(
                    self.source_bucket_name,
                    source_key,
                    temp_file_path
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
                            
                        input_rec = input_port.read_record(input_rec)
                        continue


                    else:
                        raise FileNotFoundException("File " + source_key + " not found.")
                else:
                    # all other ClientError exceptions will pop up here
                    raise
            
            try:
                file_size = os.path.getsize(temp_file_path)
                #logging.info("file_size: " + str(file_size))
                # it will break on any exception
                #with open(temp_file_path, 'rb') as file_handle:
                #    file_data = file_handle.read()
                #    tgt_client.put_object(
                #        Bucket=self.target_bucket_name,
                #        Key=target_key,
                #        Body=file_data,
                #        ContentLength=len(file_data),
                #        ContentType='application/octet-stream'
                #    )

                tgt_client.upload_file(temp_file_path, self.target_bucket_name, target_key)
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
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
