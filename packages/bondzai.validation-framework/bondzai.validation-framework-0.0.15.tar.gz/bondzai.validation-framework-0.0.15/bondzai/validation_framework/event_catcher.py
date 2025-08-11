import time
import queue
from .log_handler import logger
from bondzai.gateway_sdk.agent import Agent
from enum import Enum

DEFAULT_POLLING_TIME = 0.005  # pooling time for events (in seconds)
DEFAULT_TIMEOUT_LIMIT = 10  # Timeout default limit (in seconds)


def accurate_wait(duration: float, get_now: callable = time.perf_counter):
    """
    Wait for a certain duration (accurate but is blocking)
    Args:
        duration: waiting duration (in seconds)
        get_now: wait function
    """
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()


class Singleton(type):
    """
    Meta class for Singleton implementation
    """
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance[cls]


class EventType(Enum):
    """
    Different waiting type, linked to <event>_done callback functions
    """
    TRAINING = "training"
    INFERENCE = "inference"
    FINAL_PROCESS = "final_process"


class AgentEventCatcher:
    """
    Class to handle specific events data catch for one agent
    """

    def __init__(self, agent: Agent, maxsize: int = 10):
        self.agent = agent
        self.maxsize = maxsize
        self.remover = {
            EventType.INFERENCE: self.agent.on_inference_result(self._inference_done),
            EventType.TRAINING: self.agent.on_training_done(self._training_done),
            EventType.FINAL_PROCESS: self.agent.on_final_process_result(self._final_process_done)
        }
        self.done = {}
        self.data = {}
        for event_type, callback in self.remover.items():
            self.done[event_type] = False
            self.data[event_type] = queue.Queue(maxsize=self.maxsize)

    def _stop_wait(self, data: dict, event_type: EventType):
        """
        Internal method this is used at <event>_done callback to stop wait
        Args:
            data: event data dict
            event_type: event_type
        """
        self.done[event_type] = True
        if self.data[event_type].full():
            self.data[event_type].get()
        self.data[event_type].put(data)

    def _training_done(self, agent, data):
        """
        Callback from training done event
        """
        self._stop_wait(data, EventType.TRAINING)

    def _inference_done(self, agent, data):
        """
        Callback from inference done event
        """
        self._stop_wait(data, EventType.INFERENCE)

    def _final_process_done(self, agent, data):
        """
        Callback from final process done event
        """
        self._stop_wait(data, EventType.FINAL_PROCESS)

    def _remove_callback(self):
        """
        Remove callback
        """
        for remover in self.remover.values():
            if remover is not None:
                remover()

    def get_data_list(self, event_type: EventType) -> list[dict]:
        """
        Get list of data dict from event done (for async application)
        Args:
            event_type: EventType object
        Returns:
            data_list : list of data dict from event

        """
        data_list = []
        while len(data_list) < self.data[event_type].qsize() or not self.data[event_type].empty():
            data_list.append(self.data[event_type].get())
        return data_list

    def wait(self, event_type: EventType, timeout: float = DEFAULT_TIMEOUT_LIMIT,
             polling_time: float = DEFAULT_POLLING_TIME) -> (float, dict):
        """
        Wait for one event to end
        Args:
            event_type: EventType
            timeout: Stop and send warning if wait time reaches this limit
            polling_time: Interval to check if process is done or not

        Returns:
            wait_time: Effective time of wait (in seconds), None if timeout is reached
            data: event data dict obtained at <event>_done event
        """
        wait_time = 0
        timed_out = False
        now = time.time()
        while not self.done[event_type]:
            if wait_time > timeout:  # stop infinite loop
                logger.warn(f"{event_type.value} wait timed out after {timeout}s")
                timed_out = True
                break
            time.sleep(polling_time)
            wait_time += time.time() - now
            now = time.time()
        data = None if timed_out else self.data[event_type].get()
        self.done[event_type] = False
        return wait_time, data

    def __del__(self):
        self._remove_callback()


class EventCatcher(metaclass=Singleton):
    """
    Global event catcher, handles agent selection
    """

    def __init__(self):
        self.waiter_dict = {}

    def _wait(self, agent: Agent, event_type: EventType, timeout: float = DEFAULT_TIMEOUT_LIMIT,
              polling_time: float = DEFAULT_POLLING_TIME) -> (float, dict):
        """
        Wait for one event to end
        Args:
            agent: Agent object
            event_type: EventType object
            timeout: Stop and send warning if wait time reaches this limit
            polling_time: Interval to check if process is done or not
        Returns:
            wait_time: Effective time of wait (in seconds), None if timeout is reached
            data: event data dict obtained at <event>_done event

        """
        if agent not in self.waiter_dict.keys():
            self.waiter_dict[agent] = AgentEventCatcher(agent)
        return self.waiter_dict[agent].wait(event_type=event_type, timeout=timeout, polling_time=polling_time)

    def _get_data_list(self, agent: Agent, event_type: EventType):
        """
        Get list of data dict from event done (for async application)
        Args:
            agent: Agent object
            event_type: EventType object
        Returns:
            data_list : list of data dict from event
        """
        if agent not in self.waiter_dict.keys():
            self.waiter_dict[agent] = AgentEventCatcher(agent)
        return self.waiter_dict[agent].get_data_list(event_type=event_type)

    def wait_training(self, agent: Agent, timeout: float = DEFAULT_TIMEOUT_LIMIT,
                      polling_time: float = DEFAULT_POLLING_TIME) -> (float, dict):
        """
        Wait for training event
        Args:
            agent: Agent object
            timeout: Stop and send warning if wait time reaches this limit
            polling_time: Interval to check if process is done or not

        Returns:
            wait_time: Effective time of wait (in seconds), None if timeout is reached
            data: event data dict obtained at <event>_done event
        """
        return self._wait(agent=agent, event_type=EventType.TRAINING, timeout=timeout, polling_time=polling_time)

    def wait_inference(self, agent: Agent, timeout: float = DEFAULT_TIMEOUT_LIMIT,
                       polling_time: float = DEFAULT_POLLING_TIME) -> (float, dict):
        """
        Wait for inference event
        Args:
            agent: Agent object
            timeout: Stop and send warning if wait time reaches this limit
            polling_time: Interval to check if process is done or not

        Returns:
            wait_time: Effective time of wait (in seconds), None if timeout is reached
            data: event data dict obtained at <event>_done event
        """
        return self._wait(agent=agent, event_type=EventType.INFERENCE, timeout=timeout, polling_time=polling_time)

    def wait_final_process(self, agent: Agent, timeout: float = DEFAULT_TIMEOUT_LIMIT,
                           polling_time: float = DEFAULT_POLLING_TIME) -> (float, dict):
        """
        Wait for final process event
        Args:
            agent: Agent object
            timeout: Stop and send warning if wait time reaches this limit
            polling_time: Interval to check if process is done or not

        Returns:
            wait_time: Effective time of wait (in seconds), None if timeout is reached
            data: event data dict obtained at <event>_done event
        """
        return self._wait(agent=agent, event_type=EventType.FINAL_PROCESS, timeout=timeout, polling_time=polling_time)

    def get_training_data(self, agent: Agent):
        """
        Get list of data dict from training event done (for async application)
        Args:
            agent: Agent object
        Returns:
            data_list : list of data dict from event
        """
        return self._get_data_list(agent, EventType.TRAINING)

    def get_inference_data(self, agent: Agent):
        """
        Get list of data dict from inference event done (for async application)
        Args:
            agent: Agent object
        Returns:
            data_list : list of data dict from event
        """
        return self._get_data_list(agent, EventType.INFERENCE)

    def get_final_process_data(self, agent: Agent):
        """
        Get list of data dict from final process event done (for async application)
        Args:
            agent: Agent object
        Returns:
            data_list : list of data dict from event
        """
        return self._get_data_list(agent, EventType.FINAL_PROCESS)
