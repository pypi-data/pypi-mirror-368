from zwergetl.engine.edges import Edge
from zwergetl.engine.nodes import Node
from zwergetl.engine.enums import Result
import csv
from decimal import Decimal
import os
import logging
import datetime

DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

class CsvReader(Node):

    def __init__(
        self,
        node_id,
        graph,
        input_dir_name: str,
        input_file_name: str,
        encoding='utf-8',
        delimiter=',',
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL,
        skip_rows=1

    ):
        super().__init__(node_id, graph)
        self.input_dir_name = input_dir_name
        self.input_file_name = input_file_name
        self.encoding = encoding
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.quoting = quoting
        self.skip_rows = skip_rows

    def convert_to(self, value, col_metadata):
        ret_val = value
        col_type = col_metadata.get('type')
        #print("type: " + col_type)
        #print("name: " + col_metadata.get('name'))
        #print("value: " + value)
        if col_type == 'integer':
            if value == "":
                ret_val = None
                #print('!!!')
            else:
                ret_val = int(value)
        elif col_type == 'decimal':
            if value == "":
                ret_val = None
            else:
                ret_val = Decimal(value)
        elif col_type == 'string':
            if value == "":
                ret_val = None
        elif col_type == 'date':
            if value == "":
                ret_val = None
            else:
                fmt = col_metadata.get('format')
                if fmt is None:
                    fmt = DEFAULT_DATE_FORMAT
                ret_val = datetime.datetime.strptime(value, fmt) 
        
        if value == "":
            ret_val = None
        
        return ret_val

    # This node cannot receive input records.
    # It can be executed as the first node of the graph.
    def execute(self):
        res = Result.FINISHED_OK

        full_filename = os.path.join(self.input_dir_name, self.input_file_name)

        row_counter = 0
        row_batch = []
        output_port = self.get_output_port(0)
        md = output_port.metadata
        with open(full_filename, newline='', encoding=self.encoding) as f:
            reader = csv.reader(f, delimiter=self.delimiter, quotechar=self.quotechar, quoting=self.quoting)
            #if self.skip_rows > 0:
            #    for x in range(self.skip_rows - 1):
            #        next(reader, None)

            rownum = 0
            for o in reader:
                if rownum < self.skip_rows:
                    rownum += 1
                    continue

                if output_port.is_stop_it():
                    res = Result.ABORTED
                    break

                # convert strings to data types specified in metadata
                i = 0
                for col in md:
                    o[i] = self.convert_to(o[i], col)
                    i += 1
                    
                # This thread will be blocked immediately after the following line
                #print(o)
                output_port.write_record(o)
        
        return res

    def set_output_node(self, node, metadata, input_port_number=0):
        """
        Connects the output port 0 of this node to
        the input port 0 of the passed in node, creating
        a new edge as required

        :param node: the node that will be receiving the output of
            this node on input port 0
        :param metadata: field metadata for output records
        :param input_port_number: input port number of output node. default 0
        """
        edge = Edge(metadata)
        # TODO: If it has been added already?
        #self.graph.add_node(node)
        self.set_output_port(edge, 0)
        node.set_input_port(edge, input_port_number)
