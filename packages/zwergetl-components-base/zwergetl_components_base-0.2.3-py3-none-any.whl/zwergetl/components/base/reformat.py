from zwergetl.engine.nodes import Node
from zwergetl.engine.nodes import NodeConfigError
from zwergetl.engine.edges import Edge
from zwergetl.engine.enums import Result
from zwergetl.engine.records import Record

import inspect
import logging

class RecordTransform:
    def init(self):
        pass

    def transform(self, input_record, output_records):
        pass

class Reformat(Node):
    """
    Receives records from port 0, executes user-defined transformation
    function for each record, outputs results to any number of output ports.

    :param transform_func: A user-defined function object that does the transformation.
        The signature of the function must be: func_name(input, output1, output2,...output_n),
        where input is an array of input values on input port 0.
        output1 - output_n are arrays of values corresponding to each output port connected
        to the node in the ascending order of port numbers.
        The same arrays are used for every function call, so all the fields must be explicitly
        set every time by the transform function, otherwise fields will contain values from previous call.
    :param transform_obj: An object that implements RecordTransform interface.
        Either transform_func or transform_obj must be set but not both of them.
        Assigning both parameters will cause an error during node execution.
    """
    def __init__(
        self,
        node_id,
        graph,
        transform
    ):
        super().__init__(node_id, graph)
        self._init_func = None
        self._transform_func = None
        self._transform_obj = None
        if inspect.isfunction(transform):
            self._transform_func = transform
        else:
            # assuming it's an object
            #if hasattr(transform, 'transform') and callable(getattr(transform, 'transform')):
                #self._transform_func = getattr(transform, 'transform')
            #if hasattr(transform, 'init') and callable(getattr(transform, 'init')):
                #self._transform_func = getattr(transform, 'init')
            self._transform_obj = transform


    """
    Return codes for transform functions
    """
    # the record will be sent to all the output ports
    ALL = 1000;
    # the record will be sent to the first output port
    OK = 0;
    # the record will be skipped
    SKIP = -1;
    # all values lesser or equal this value are considered as errors
    STOP = -2;
    # Values > 0 are considered as port numbers. Ports with the same numbers
    # must be assigned, otherwise an error is raised.

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

        # TODO: If metadata is not set, it should be propagated from
        # input port 0. Metadata propagation should be logged as DEBUG
        for key, port in self.output_ports.items():
            if port.metadata is None:
                raise NodeConfigError("Metadata is not set for output port %d" % key)

        if (self._transform_func is None) and (self._transform_obj is None):
            raise NodeConfigError("`transform` parameter is not set.")

        check_func = None
        one_extra_arg = 0
        if self._transform_func is not None:
            check_func = self._transform_func
        else:
            check_func = self._transform_obj.transform
            one_extra_arg = 1 # add one arg for "self"

        transform_args = inspect.getfullargspec(check_func)
        transform_args_count = len(transform_args.args) # positional args
        out_ports_count = len(self.output_ports)
        if transform_args_count != (out_ports_count + 1 + one_extra_arg):
            raise NodeConfigError("The number of arguments of `transform` function (or method) should be "
                                  "equal to the number of output ports + one (the first one) "
                                  "argument for the input port 0. Currently the function is declared "
                                  "with %d arguments and the node %s "
                                  "has %d output ports." % (transform_args_count, self.node_id, out_ports_count))
                
            
    
    def execute(self):
        res = Result.FINISHED_OK
        input_port = self.get_input_port(0)

        # Establish an array of output records - one per each
        # output port
        output_records = dict()
        for port_num, output_port in self.output_ports.items():
            # create a wrapper for each output record
            wrapper = Record(output_port.metadata)
            # a reusable array to store record values
            rec_array = [None] * len(output_port.metadata)
            wrapper.set_values(rec_array)
            output_records[port_num] = wrapper

        # user defined init function
        if self._transform_obj is not None:
            self._transform_obj.init()
       
        output_port_count = len(self.output_ports)

        # Metadata on input port may not be available
        # until the producer produce the first record
        input_rec = None
        # let the input port allocate the record for us
        # and we'll reuse it later
        input_rec = input_port.read_record(input_rec)

        # record wrapper allows transform_func code to address fields by name
        # rather than by index
        input_record_wrapper = None
        if input_rec:
            input_record_wrapper = Record(input_port.metadata)
            
        # prepare parameter list for calling transform function
        transform_func_param_list = [None] * (1 + len(self.output_ports)) # +one for input

        while input_rec and not self.is_stop_it():
            transform_res = Reformat.SKIP
            input_record_wrapper.set_values(input_rec)
            transform_func_param_list[0] = input_record_wrapper
            cnt = 1
            for key, rec in output_records.items():
                transform_func_param_list[cnt] = rec
                cnt += 1
                
            if self._transform_func is not None:
                transform_res = self._transform_func(*transform_func_param_list)
            else:
                transform_res = self._transform_obj.transform(*transform_func_param_list)
                
            #transform_res = self._transform_func(input_record_wrapper, output_records)


            #logging.debug("reformat res: %d", transform_res)
            if transform_res <= Reformat.STOP:
                # an error.
                msg = "Record transform function returned %d error code." % (transform_res)
                raise Exception(msg)
            elif transform_res == Reformat.SKIP:
                pass
            elif transform_res == Reformat.ALL: # send to all output ports
                if output_port_count == 1:
                    rec = output_records[0].get_values()
                    self.write_record(rec, 0)
                else:
                    # this is slower than direct write, so we are doing
                    # this loop only in case there is more than one output port connected
                    for key, port in self.output_ports.items():
                        rec = output_records[key].get_values()
                        port.write_record(output_records[key])
            elif transform_res == Reformat.OK: # write to port 0 only
                rec = output_records[0].get_values()
                self.write_record(rec, 0)
            else: # write to one non-zero output port
                rec = output_records[transform_res].get_values()
                self.write_record(rec, transform_res)

            # read the next record
            input_rec = input_port.read_record(input_rec)
        return res

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
