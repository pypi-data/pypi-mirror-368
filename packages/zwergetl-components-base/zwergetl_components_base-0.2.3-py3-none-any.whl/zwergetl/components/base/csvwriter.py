#import codecs
#import binascii
import csv
from enum import Enum
import logging
import os
import time
from zwergetl.engine.nodes import Node
from zwergetl.engine.nodes import NodeConfigError
from zwergetl.engine.enums import Result
from zwergetl.engine.records import Record


class CsvWriter(Node):
    """
    Writes records from input port 0 to csv file.

    :param output_dir_name: Path to output directory
    :param output_file_name: Output file name without directory name.
    """
    def __init__(
        self,
        node_id,
        graph,
        output_dir_name: str,
        output_file_name: str,
        encoding='utf-8',
        delimiter=',',
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL,
        output_field_names=True,
        lineterminator="\n"
    ):
        super().__init__(node_id, graph)
        self.output_dir_name = output_dir_name
        self.output_file_name = output_file_name
        self.encoding = encoding
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.quoting = quoting
        self.output_field_names = output_field_names
        self.lineterminator = lineterminator


    def check_config(self):
        # 1. input port
        try:
            p = self.get_input_port(0)
        except KeyError:
            raise NodeConfigError("Input port 0 is not assigned.")


    def execute(self):
        res = Result.FINISHED_OK
        input_port = self.get_input_port(0)

        input_rec = None
        input_rec = input_port.read_record(input_rec)

        md = input_port.metadata
        md_out = md

        output_rec = [None] * len(md)
        date_cols_with_fmt = list()
        byte_cols_with_fmt = list()
        i = 0
        for field in md:
            if field.get('type') == 'date':
                fmt = field.get('format')
                if fmt is not None:
                    date_cols_with_fmt.append([i, fmt])
            elif field.get('type') == 'bytes':
                byte_cols_with_fmt.append([i, 'hex'])
            i += 1

        out_fn = self.output_file_name

        full_filename = os.path.join(self.output_dir_name, out_fn)
        csvfile = open(full_filename, 'w', newline='', encoding=self.encoding)
        writer = csv.writer(csvfile, delimiter=self.delimiter,
                            quotechar=self.quotechar, quoting=self.quoting, lineterminator=self.lineterminator)

        if self.output_field_names:
            header_record = []
            for field in md_out:
                header_record.append(field['name'])

            writer.writerow(header_record)
            
        
        # actual records
        while input_rec and not self.is_stop_it():
            # convert datetime fields according to format, if it is defined
            for date_md in date_cols_with_fmt:
                field_index = date_md[0]
                field_fmt = date_md[1]
                field_val = input_rec[field_index]
                if field_val is not None:
                    input_rec[field_index] = field_val.strftime(field_fmt)

            # convert bytes to hex or TODO: base64 or whatever else
            for byte_md in byte_cols_with_fmt:
                field_index = byte_md[0]
                field_fmt = byte_md[1]
                field_val = input_rec[field_index]
                if field_val is not None:
                    input_rec[field_index] = field_val.decode('ascii')
                
            writer.writerow(input_rec)
            input_rec = input_port.read_record(input_rec)

        csvfile.close()
        
        if input_port.producer_node_result != Result.FINISHED_OK:
            res = Result.ABORTED

        return res

