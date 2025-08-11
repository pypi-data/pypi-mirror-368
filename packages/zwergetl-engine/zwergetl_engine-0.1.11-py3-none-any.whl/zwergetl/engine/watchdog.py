import datetime
import time
import logging
from zwergetl.engine.enums import Result

WATCH_INTERVAL = 1
# Number of seconds given to a node
# to stop on it's own in case a stop_it signal
# is sent.
STOP_TIMEOUT = 120

class GraphRunError(Exception):
    pass

class WatchDog:
    """This class is used to execute graph."""

    def __init__(self, graph, logging_interval=30):
        self._graph = graph
        self._logging_interval = logging_interval


    def run_graph(self):
        """run the graph"""
        passes = 0

        tracking_prefix = "Tracking - "
        phase_starting = "Starting up all nodes in Phase [%d]"
        phase_started = "Successfully started all nodes in phase [%d]."
        #phase_finished = "Phase finished with result: %s. Elapsed time (sec): %d"
        phase_finished = "Phase [%d] finished with result: %s"
        #          123456789012345678901234567890123456789012345678901234567890
        #          0        1         2         3         4         5         6
        header1 = "----------------** Start of tracking Log **----------------"
        header2 = " Time: %s"
        header3 = " NODE                      PORT       RECORDS        REC/S"
        header4 = "-----------------------------------------------------------"
        #           reader                                            RUNNING
        #                                    Out:0         12000          256 
        footer1 = "---------------------** End of Log **----------------------"

        #                      123456789012345678901234567890123456789012345678901234567890
        #                      0        1         2         3         4         5         6
        final_header1 =       "---------** Final tracking Log for phase [%d] **-----------"
        final_footer_ok  =    "Graph execution result: %s. Elapsed time (sec): %d"
        final_footer_error  = "Graph execution result: %s. Elapsed time (sec): %d"
        summary_of_phases_1 = "------------** Summary of Phases execution **--------------"
        summary_of_phases_2 = "Phase#     Finished Status                     RunTime(sec)"

        final_result = Result.FINISHED_OK


        stop_it_time = None
        start_time = datetime.datetime.now()
        #phase_start_time = start_time
        last_tracking_time = start_time
        check_time = None
        delta_since_graph_start = None
        delta_since_phase_start = 0
        
        phases = self._graph.get_phases()
        for phase in phases:
            all_done = False
            phase_start_time = datetime.datetime.now()
            # Check every WATCH_INTERVAL seconds for errors. Log every self._log_interval seconds.
            # On error send "stop_it" to all nodes. Mark the time when stop_it was sent.
            # TODO: Keep checking until timeout for each node (65 seconds).
            # Kill remaining unfinished nodes.



            nodes = phase.get_nodes()
            logging.info(phase_starting, phase.phase_number)
            
            # checks
            for key, node in nodes.items():
                node.check_config()

            # start all nodes, the order doesn't matter
            for key, node in nodes.items():
                node.start()
                #logging.info("Node %s: started", node.node_id)

            logging.info(phase_started, phase.phase_number)

            stop_it = False

            while not all_done:
                time.sleep(WATCH_INTERVAL)
                check_time = datetime.datetime.now()
                delta_since_phase_start = check_time - phase_start_time
                finished_nodes = 0
                # Error checks
                for node_id, node in nodes.items():
                    if node.result_code == Result.ERROR and stop_it is False:
                        stop_it = True
                        stop_it_time = datetime.datetime.now()


                    # Mark all nodes with stop_it flag at each check
                    # if any node in the graph has failed with ERROR,
                    # all other nodes should abandon their work and
                    # finish with ABORTED. They should periodically 
                    # check the stop_it flag themselves, watchdog is not interfering.
                    if stop_it and node.result_code == Result.RUNNING and not node.is_stop_it():
                        #if len(node.input_ports) == 0: # other nodes will receive eof with aborted flag
                        node.set_stop_it()
                        #logging.debug("Sending stop_it to node %s", node.node_id)

                    if node.result_code != Result.RUNNING:
                        finished_nodes += 1
                        #logging.debug("Finished nodes: %s, %s", node.node_id, node.result_code.name)
                        #logging.debug("finished_nodes: %d", finished_nodes)
                #~for loop over nodes
                
                if finished_nodes == len(nodes):
                    all_done = True
                
                # logging - tracking log.
                # Watchdog checks the status once a second. logging_interval is, say, 30 secs.
                # At each check we are checking how many seconds have elapsed since last check.
                # If current delta_since_start >= last_tracking_time + logging_interval,
                # output tracking and reset last_tracking_time. Also track each start of phase
                # and end of phase.
                delta_since_last_check = check_time - last_tracking_time
                if self._logging_interval > 0 and delta_since_last_check.seconds >= self._logging_interval:
                    last_tracking_time = check_time

                    logging.info(tracking_prefix + header1)
                    logging.info(tracking_prefix + header2, check_time.strftime('%Y-%m-%d %H:%M:%S'))
                    logging.info(tracking_prefix + header3)
                    logging.info(tracking_prefix + header4)
                    # loop through all nodes
                    for node_id, node in nodes.items():
                        logging.info(tracking_prefix + " %-45s %11s", node_id, node.result_code.name)
                        for key, port in node.input_ports.items():
                            records_per_sec = 0
                            if port.record_counter > 0:
                                records_per_sec = port.record_counter / delta_since_phase_start.seconds
                            logging.info(tracking_prefix + " %30s %13d %12d", "in:" + str(key), port.record_counter, records_per_sec)
                        for key, port in node.output_ports.items():
                            records_per_sec = 0
                            if port.record_counter > 0:
                                records_per_sec = port.record_counter / delta_since_phase_start.seconds
                            logging.info(tracking_prefix + " %30s %13d %12d", "out:" + str(key), port.record_counter, records_per_sec)
                    logging.info(tracking_prefix + footer1)
            #end of while not all done


            # tracking log for the finished phase
            if self._logging_interval > 0:
                #logging.info(phase_finished)
                logging.info(tracking_prefix + final_header1, phase.phase_number)
                logging.info(tracking_prefix + header2, check_time.strftime('%Y-%m-%d %H:%M:%S'))
                logging.info(tracking_prefix + header3)
                logging.info(tracking_prefix + header4)
                # loop through all nodes
                final_result = Result.FINISHED_OK
                for node_id, node in nodes.items():
                    logging.info(tracking_prefix + " %-45s %11s", node_id, node.result_code.name)
                    if node.result_code != Result.FINISHED_OK:
                        final_result = Result.ERROR
                    for key, port in node.input_ports.items():
                        records_per_sec = 0
                        if port.record_counter > 0:
                            records_per_sec = port.record_counter / delta_since_phase_start.seconds
                        logging.info(tracking_prefix + " %30s %13d %12d", "in:" + str(key), port.record_counter, records_per_sec)
                    for key, port in node.output_ports.items():
                        records_per_sec = 0
                        if port.record_counter > 0:
                            records_per_sec = port.record_counter / delta_since_phase_start.seconds
                        logging.info(tracking_prefix + " %30s %13d %12d", "out:" + str(key), port.record_counter, records_per_sec)

                logging.info(tracking_prefix + footer1)
                #logging.info(tracking_prefix + phase_finished, final_result.name, delta_since_phase_start.seconds)
            # if tracking log

            # all nodes have finished
            # check and log their statuses
            #for node_id, node in nodes.items():
            #    logging.info("Node %s finished with result: %s", node.node_id, node.result_code.name)
            # a message for the finished phase
            logging.info(phase_finished, phase.phase_number, final_result.name)
            
            # for the next phase:
            phase_start_time = datetime.datetime.now()
            
            if final_result != Result.FINISHED_OK:
                break

        
        # --- end of loop through phases ---
        check_time = datetime.datetime.now()
        delta_since_graph_start = check_time - start_time
        #if final_result == Result.FINISHED_OK:
        #    logging.info(final_footer_ok, final_result.name, delta_since_graph_start.seconds)
        #else:
        #    logging.info(final_footer_error, final_result.name, delta_since_graph_start.seconds)

        return final_result

    def run_graph_or_fail(self):
        """Run graph. If it fails, return a GraphRunError"""
        res = self.run_graph()

        if res != Result.FINISHED_OK:
            raise GraphRunError("Graph finished with result: %s" % res.name)

