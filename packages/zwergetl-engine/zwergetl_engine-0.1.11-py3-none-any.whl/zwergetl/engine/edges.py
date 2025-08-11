import copy
import logging
import threading
from zwergetl.engine.enums import Result

class PortClosedError(Exception):
    pass

class Edge:
    """
    A port is an object that connects two nodes and is used to pass records between them
    """
    def __init__(self, metadata):
        self.metadata = metadata

        self.record_counter = 0
        self.record = None

        # Threading
        self.record_is_written = threading.Event()
        self.record_is_read = threading.Event()

        # Set initial state of events.
        # The producer can write records,
        # the consumer - cannot read records yet.
        # Setting record_is_read to True allows the producer
        # to write it's first record
        self.record_is_read.set()
        self._eof = False
        self._stop_it = False
        # Current status of the producer Node
        self.producer_node_result = Result.N_A
        self.consumer_node_result = Result.N_A

    def set_eof(self, result):
        """Sets eof flag, which means there will be no more records."""
        # This method returns immediately without waiting for
        # record_is_read event to be set. It means that when eof is reached
        # the producing node does not wait for the consuming node
        # to set the record_is_read event.
        # The consuming node may still be reading the last record.
        # If it
        self.record_is_read.wait()
        #self.record = None
        self._eof = True
        self.producer_node_result = result
        # This will notify consumer
        self.record_is_written.set()
        self.record_is_read.clear()

        
    def set_stop_it(self, result):
        """Sets stop_it flag on the edge if something went wrong with the consumer node."""
        self._stop_it = True
        self.consumer_node_result = result
        # This line will wake up the producer if it is waiting for
        # this event
        self.record_is_read.set()

    def is_stop_it(self):
        return self._stop_it

    def is_eof(self):
        return self._eof

    def write_record(self, record):
        """Writes record to the edge."""
        # Initially record_is_read is set to True
        self.record_is_read.wait()
        if self.record is None:
            self.record = [None] * len(self.metadata)

        # if the consumer has set a stop_it flag on the edge, it means
        # something went wrong, the edge is closed
        # and we can't write anything to it.
        # In this case a PortClosedError is raised. If this error
        # is not processed by a particular node implementation, it will be
        # at least processed by Node class. A Node implementation may check is_stop_it() 
        # on the edge before trying to write to it
        # and thus stop gracefully without exceptions.
        if self._stop_it:
            raise PortClosedError("The port was closed by the downstream node.")

        # copying every element of record
        self.record[:] = record

        self.record_counter += 1
        
        self.record_is_read.clear()
        # Signal to the consumer
        self.record_is_written.set()
        
    def read_record(self, rec):
        """
        Reads a record from the edge and returns it's copy.

        This method is called by the consumer node to get a
        copy of the record that was written to the edge by the producer node.
        This method blocks the calling thread
        until the event "record_is_written" is set on the edge.

        :param rec: a reference to the array that will hold the copy of the record's values.
            If rec is None, a new array is allocated. This array can be reused
            later on by passing it in again and again.
        :return: the same reference that was passed in as rec parameter or None
            if there are no more records (eof is set on the edge by the producer node).
            If rec parameter was None, the return value is the reference to the
            newly created array (or None if no record exists).
        """
        self.record_is_written.wait()
        if not self._eof:
            if rec is None:
                rec = [None] * len(self.metadata)
            # We are making a shallow copy - i.e. copying every element
            # from the source list to the target list.
            # Therefore every element of the source list should be immutable (which it normally is).
            # In case elements of the source list are mutable (dicts and arrays)
            # it may be a problem if they are mutated by the producing node,
            rec[:] = self.record
        else:
            rec = None
        self.record_is_written.clear()
        # The producer thread will wake up immediately after the following line
        self.record_is_read.set()
        # clean up
        return rec

