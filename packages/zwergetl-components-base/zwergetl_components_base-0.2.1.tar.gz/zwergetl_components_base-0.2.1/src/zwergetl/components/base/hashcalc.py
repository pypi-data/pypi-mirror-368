from zwergetl.engine.nodes import Node
from zwergetl.engine.nodes import NodeConfigError
from zwergetl.engine.edges import Edge
from zwergetl.engine.enums import Result
from zwergetl.engine.records import Record
import zwergetl.engine.utils as utils

import hashlib
import logging


class HashCalc(Node):
    def __init__(
        self,
        node_id,
        graph,
        key_fields,
        key_hash_field_name='key_hash',
        value_hash_field_name='value_hash',
        ignore_fields=['dtime_inserted', 'dtime_updated']
    ):
        super().__init__(node_id, graph)
        self.key_fields = key_fields
        self.key_hash_field_name = key_hash_field_name
        self.value_hash_field_name = value_hash_field_name
        self.ignore_fields = ignore_fields


    def check_config(self):
        # one input edge
        try:
            p = self.get_input_port(0)
        except KeyError:
            raise NodeConfigError("Input port 0 is not assigned.")

        # at least one output edge
        try:
            p = self.get_output_port(0)
        except KeyError:
            raise NodeConfigError("Output port 0 is not assigned.")


    def set_output_node(self, node, metadata, output_port=0, input_port=0):
        """
        Connects the given output port of this node to
        the given input port of the downstream node.

        :param node: the downstream node
        :param metadata: record metadata for that connection.
        :param output_port: output port of this node
        :param input_port: input port of the downstream node
        """
        edge = Edge(metadata)
        self.graph.add_node(node)
        self.set_output_port(edge, output_port)
        node.set_input_port(edge, input_port)


    def create_input_output_field_map(self, input_metadata, output_metadata):
        """
        Creates a map of input fields to output fields by field name
        and returns it
        """
        res = None
        if input_metadata is not None:
            res = []
            for input_field in input_metadata:
                input_field_name = input_field.get("name")
                out_idx = -1
                for output_field in output_metadata:
                    out_idx += 1
                    output_field_name = output_field.get("name")
                    if input_field_name == output_field_name:
                        break
                res.append(out_idx)
        return res

    def create_input_key_hash_field_map(self, input_metadata):
        """
        Returns a list of field indexes in input metadata for fields that constitute key_hash
        """
        res = None
        if input_metadata is not None:
            res = []
            keys_list = utils.convert_to_list_if_its_not(self.key_fields)
            if len(keys_list) == 0:
                raise NodeConfigError("key_fields attribute is not set")

            for key in keys_list:
                key_index = utils.get_field_index(key, input_metadata)
                if key_index == -1:
                    raise NodeConfigError("Field %s not found in input metadata" % key)
                input_field_metadata = input_metadata[key_index]
                data_type = input_field_metadata.get("type")
                res.append((key_index, data_type))
        return res

    def create_input_value_hash_field_map(self, input_metadata):
        """
        Returns a list of field indexes in input metadata for fields that constitute value_hash
        """
        res = None
        if input_metadata is not None:
            res = []
            keys_list = utils.convert_to_list_if_its_not(self.key_fields)
            ignore_list = utils.convert_to_list_if_its_not(self.ignore_fields)
            # Traverse all the input fields and check if they exist in key_fields fields or ignore fields fields
            idx = 0
            while idx < len(input_metadata):
                cur_field = input_metadata[idx]
                field_name = cur_field.get("name")
                is_key = utils.get_index(field_name, keys_list) != -1
                is_ignore = utils.get_index(field_name, ignore_list) != -1
                if not is_key:
                    if not is_ignore:
                        input_field_metadata = input_metadata[idx]
                        field_name = input_field_metadata.get("name")
                        if field_name != self.key_hash_field_name:
                            if field_name != self.value_hash_field_name:
                                data_type = input_field_metadata.get("type")
                                res.append((idx, data_type))
                                #print(input_field_metadata.get("name"))
                idx += 1

        return res
        

    def execute(self):
        res = Result.FINISHED_OK
        input_port = self.get_input_port(0)
        in_md = input_port.metadata

        output_port = self.get_output_port(0)
        out_md = output_port.metadata

        # a reusable array to store output record values
        rec_array = [None] * len(output_port.metadata)

        # Metadata on input port may not be available
        # until the producer produces the first record
        input_rec = None
        # let the input port allocate the record for us
        # and we'll reuse it later
        input_rec = input_port.read_record(input_rec)


        # Establish a map between input record and output record by field name
        input_output_field_map = self.create_input_output_field_map(in_md, out_md)

        # Establish a map for key_hash fields
        input_key_hash_field_map = self.create_input_key_hash_field_map(in_md)

        # index of the field in output record that stores key_hash
        output_key_hash_field_index = utils.get_field_index(self.key_hash_field_name, out_md)

        # a list that stores all input record field indexes that go into value_hash
        input_value_hash_field_map = self.create_input_value_hash_field_map(in_md)

        # index of the field in output record that stores value_hash
        output_value_hash_field_index = utils.get_field_index(self.value_hash_field_name, out_md)

        # reading the input records
        while input_rec and not self.is_stop_it():
            # in case input metadata was created after the first record has been created
            if input_output_field_map is None:
                input_output_field_map = self.create_input_output_field_map(in_md, out_md)

            if input_key_hash_field_map is None:
                input_key_hash_field_map = self.create_input_key_hash_field_map(in_md)
        
            if input_value_hash_field_map is None:
                input_value_hash_field_map = self.create_input_value_hash_field_map(in_md)

            
            # Set None to all output fields
            idx = 0
            while idx < len(rec_array):
                rec_array[idx] = None
                idx += 1

            # copy all values to output rec
            idx = 0
            while idx < len(input_output_field_map):
                out_idx = input_output_field_map[idx]
                rec_array[out_idx] = input_rec[idx]
                idx += 1
                
            # key_hash
            key_hash_str = ''
            delimiter = ''
            for map_item in input_key_hash_field_map:
                idx = map_item[0]
                data_type = map_item[1]
                key_hash_str = key_hash_str + delimiter + utils.any2str(input_rec[idx], data_type)
                delimiter = '-'

            key_hash = hashlib.md5(key_hash_str.encode("utf-8")).hexdigest()

            rec_array[output_key_hash_field_index] = key_hash

            # value hash
            value_hash_str = ''
            delimiter = ''
            for map_item in input_value_hash_field_map:
                idx = map_item[0]
                data_type = map_item[1]
                value_hash_str = value_hash_str + delimiter + utils.any2str(input_rec[idx], data_type)
                delimiter = '-'
                #print(str(idx) + ", data type: " + data_type)

            #value_hash = value_hash_str
            value_hash = hashlib.md5(value_hash_str.encode("utf-8")).hexdigest()

            rec_array[output_value_hash_field_index] = value_hash
            
            # output        
            self.write_record(rec_array, 0)
                
            # read the next record
            input_rec = input_port.read_record(input_rec)
        return res
