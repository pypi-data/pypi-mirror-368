import datetime
import threading
import logging

from zwergetl.engine.enums import Result
from zwergetl.engine.edges import PortClosedError

class NodeConfigError(Exception):
    pass

class Node(threading.Thread):
    """
    The base Node class.
    """
    def __init__(self, node_id, graph) -> None:
        super().__init__()
        self.node_id = node_id
        self.graph = graph
        self.phase = None
        graph.add_node(self)
        self.input_ports = dict()
        self.output_ports = dict()
        self.result_lock = threading.Lock()
        self.result_code = Result.N_A
        self.result_message = ''
        # A variable that can be set to True by the watchdog thread
        # telling this thread to stop. It should be checked
        # periodically
        self._stop_it = False
        self._stop_it_time = None
        self.node_thread = None

    def set_result_code(self, result_code):
        """
        Sets instance variable result_code.
        This variable is checked periodically by watchdog
        """
        self.result_lock.acquire()
        self.result_code = result_code
        self.result_lock.release()

    def set_result_message(self, result_message):
        """
        Sets instance variable result_message.
        """
        self.result_message = result_code

    def set_node_thread(self, node_thread):
        if not node_thread is None:
            if self.node_thread != node_thread:
                self.node_thread = node_thread

    def broadcast_eof(self, result=Result.FINISHED_OK):
        """
        Send eof to all connected output ports
        """
        for key, port in self.output_ports.items():
            # There can be stop_it flag that came from one of output ports
            # which caused this broadcast in the first place, skip it.
            if not port.is_stop_it():
                port.set_eof(result)
        pass
            
    def broadcast_stop_it(self, result):
        """
        Send stop_it to all connected input ports
        """
        for key, port in self.input_ports.items():
            port.set_stop_it(result)
            logging.debug("broadcast_stop_it %s", self.node_id)
        pass
            

    def get_input_port(self, port_num):
        """
        Returns an input edge if there is one or None
        """
        return self.input_ports.get(port_num)

    def set_input_port(self, edge, port_num):
        self.input_ports[port_num] = edge

    def get_output_port(self, port_num):
        """
        Returns an output edge if there is one or None
        """
        return self.output_ports[port_num]

    def set_output_port(self, edge, port_num):
        self.output_ports[port_num] = edge
        
    def write_record(self, rec, port_num):
        """
        Writes record to output port.

        :param row: array of field values
        :param port: Port number (int).
        """
        edge = self.get_output_port(port_num)
        edge.write_record(rec)
        
    def read_record(self, port_num, rec):
        """A wrapper for that calls Edge.read_record"""
        edge = self.get_input_port(port_num)
        return edge.read_record(rec)

    def set_stop_it(self):
        # TODO: remove the method?
        # The node may be waiting for the consumer node at the moment,
        # so setting _stop_it on the node may not work. We must set stop_it on all
        # output ports and after that - on the node itself.
        #for key, port in self.output_ports.items():
        #    port.set_eof(Result.ERROR)

        #for key, port in self.input_ports.items():
        #    port.set_stop_it(Result.ERROR)

        self._stop_it = True
        self._stop_it_time = datetime.datetime.now()
    
    def is_stop_it(self):
        """
        Check if the node has been asked to stop through
        one of output nodes or directly by setting it's stop_it
        property
        """
        res = False
        #for key, port in self.output_ports.items():
        #    if port.is_stop_it():
        #        res = True
        #        return res

        if self._stop_it:
            res = True

        return res


    def abort(self):
        """
        Finishes node excecution in case of an external error.
        This method is called when another node in the
        graph has failed with error.
        """
        # This method is called from another thread.
        # It finds and terminates the thread that is used to run
        # this node
        # TODO: to be concluded
        pass
        

    def check_config(self):
        """
        Called before starting the graph. 
        In this method the node should check for required input/output
        ports and other configuration parameters (i.e. availability of connection
        parameters in graph connections). Actual connections with data stores
        should not be attempted here, it should be done in execute() method instead.
        In case something went wrong this method should raise NodeConfigError.
        """
        pass

    def execute(self)->int:
        """
        Main method that executes whatever the node is doing.
        This method does nothing in Node class and must be implemented in
        descendant classes.

        :return: See nodes2.engne.enums.Result for possible values.
            in base Node class the method is not implemented and returns Result.ERROR
        """
        return Result.ERROR

    def run(self):
        logging.info("Node %s: started", self.node_id)
        res = Result.RUNNING
        self.set_result_code(res)

        # TODO: call init
        try:
            # remember the thread used to run this node
            # in case we'll need to terminate it later
            self.set_node_thread(threading.current_thread())
            res = self.execute()
        except PortClosedError as e:
            logging.exception("%s: error writing to output port. Stopping node execution.", self.node_id)
            res = Result.ABORTED
        except Exception as e:
            # The exception could have been handled inside execute() method.
            # If it wasn't we handle it here and don't let it be passed further up.
            # If working under Airflow, the watchdog thread raises a new Exception
            # when it comes upon a node that has finished with an exception.
            logging.exception("Exception while executing node %s", self.node_id)
            res = Result.ERROR

        
        if self.is_stop_it():
            res = Result.ABORTED

        # A situation when we received eof with error or aborted from upstream node
        # but our execute() didn't handle it
        if res == Result.FINISHED_OK:
            for key, port in self.input_ports.items():
                if port.producer_node_result in (Result.ERROR, Result.ABORTED):
                    res = Result.ABORTED
        
        self.set_result_code(res)

        # close all input ports in case of error
        if res == Result.ERROR:
            self.broadcast_stop_it(res)

        # This may block indefinitely if one of downstream nodes has failed already
        self.broadcast_eof(res)

        logging.info("Node %s finished with result: %s", self.node_id, self.result_code.name)
        

