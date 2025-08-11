import queue
import threading
import time
import atexit
from .log_handler import logger
from bondzai.gateway_sdk import Agent


class Connector:
    """
    Connector abstract class to set up read and write data on external sensor
    """
    def __init__(self):
        atexit.register(self.stop)
        self.queue = queue.Queue()
        self.stop_run = False
        self.isRunning = False
        self.send_mode = False
        self.startTime = None
        self.agent_dict = {}

    # ----- ABSTRACT METHODS -----

    def open(self, **kwargs):
        """
        Start communication
        """
        pass

    def read(self, timeout: float = None):
        """
        Read data from sensor (one chunk)
        Args:
            timeout: time out in seconds
        Returns:
            data: read chunk
        """
        logger.info("Reading")
        time.sleep(0.5)
        return 0

    def write(self, data):
        """
        Write data on device
        Args:
            data: data to be written
        """
        pass

    def close(self):
        """
        Close device connection
        """
        pass

    # ----- INTERNAL METHODS -----

    def subscribe_agent(self, agent: Agent):
        """
        Add agent to receive connector data
        Args:
            agent: Agent object
        """
        lookup_table = agent.get_asl_meta()["apps"][0]["meta"]["tables"]
        for source_id, src_name in lookup_table["sources"].items(): 
            source_id = int(source_id)
            if (agent.device_name, source_id) not in self.agent_dict.keys():
                self.agent_dict[(agent.device_name, source_id)] = agent


    def start_sending(self):
        """
        Send instruction to start sending data to subscribed agent
        """
        self.send_mode = True

    def stop_sending(self):
        """
        Send instruction to stop sending data to subscribed agent
        """
        self.send_mode = False

    def is_sending(self) -> bool:
        """
        Check whether device is sending data
        """
        return self.send_mode

    def _run(self):
        """
        Run instance, need a stop condition to be stopped
        """
        self.isRunning = True
        self.stop_run = False
        while not self.stop_run:
            chunk = self.read()
            if self.send_mode:
                self._send_chunk(chunk)
        self.isRunning = False

    def start(self):
        """
        Function to start continuous streaming in a thread
        Returns:

        """
        runThread = threading.Thread(target=self._run)
        runThread.daemon = True
        runThread.start()

    def stop(self):
        """
        Function to run to stop properly connector
        """
        self.stop_run = True
        time.sleep(0.05)
        self.close()

    def _send_chunk(self, chunk: list[float]):
        """
        Send chunk to subscribed agents
        Args:
            chunk: data chunk
        """
        for (agent_name, source_id), agent in self.agent_dict.items():
            agent.send_chunk(source_id, chunk)
