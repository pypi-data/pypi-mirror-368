from zwergetl.engine.nodes import Node
from zwergetl.engine.enums import Result
import csv
import logging
import os
import time

class DummyWriter(Node):

    def __init__(
        self,
        node_id,
        graph,
        delay: int=0,
        print_record=False
    ):
        super().__init__(node_id, graph)
        self.delay = delay
        self.print_record = print_record

    # This node cannot receive input records.
    # It can be executed as the first node of the graph.
    def execute(self):
        res = Result.FINISHED_OK
        input_port = self.get_input_port(0)
        # An array for storing input records
        rec = None
        rec = input_port.read_record(rec)

        while rec and not self.is_stop_it():
            # all is well
            if self.delay > 0:
                time.sleep(self.delay)
            if self.print_record:
                print(rec)
            rec = input_port.read_record(rec)

        # check if something bad has happened upstream
        #if input_port.producer_node_result != Result.FINISHED_OK:
        #    logging.warning("Node %s: upstream node finished with result: %s", self.node_id,
        #        input_port.producer_node_result.name)
        #    res = Result.ABORTED

        return res
