import argparse
import importlib
import inspect
from pathlib import Path
import time
from bondzai.validation_framework.event_catcher import EventCatcher

from bondzai.validation_framework.log_handler import logger
from bondzai.validation_framework.connector_handler import Connector
from bondzai.gateway_sdk.enums import AgentRecordMode
from bondzai.gateway_sdk.agent import Agent, AgentTriggerType, AgentAIMode
from bondzai.gateway_sdk import Gateway
from scenario import R, force_train, kill, set_callbacks, wait_for_agent
import keyboard

class Keyboard_Listener:
    """
    Abstract keyboard listener object, for each OS, a child class must b defined
    """
    def __init__(self):
        """
        Initialise listener
        """
        self.agent_dict = {}
        self.hook = None
        self.to_stop = False
        self.event_catcher = EventCatcher()
        self.agent_dict = {}
    
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
                self.agent_dict[(agent.device_name, source_id)] = {"agent": agent, 
                                                                   "trigger": AgentTriggerType.TRIGGER_OFF}

    def start(self):

        def listen(keyEvent):
            result = None
            if keyEvent.event_type == keyboard.KEY_DOWN:
                result = self.on_press(keyEvent.name)
            elif keyEvent.event_type == keyboard.KEY_UP:
                result = self.on_release(keyEvent.name)
            return result

        self.hook = keyboard.hook(listen)
        while not self.to_stop:
            time.sleep(0.5)
        self.stop()

    def stop(self):
        keyboard.unhook(self.hook)

    def on_press(self, key: str):
        """
        Define event triggered when a key is pressed
        Args:
            key: pressed key
        """
        if key == "space":
            for (agent_name, source_id), source_data in self.agent_dict.items():
                agent = source_data["agent"]
                trigger = source_data["trigger"]
                if trigger == AgentTriggerType.TRIGGER_OFF:
                    agent.set_ai_mode(AgentAIMode.APP_AI_MODE_INFERENCE)  
                    agent.set_record_mode(AgentRecordMode.DAVINSY_RECORD_SUBJECT, source_id)
                    agent.trigger(AgentTriggerType.TRIGGER_ON, source_id)
                    self.agent_dict[(agent_name, source_id)]["trigger"] = AgentTriggerType.TRIGGER_ON

    def on_release(self, key: str):
        """
        Define event triggered when a key is released
        Args:
            key: released key
        """
        if key == "q":
            self.to_stop = True
        if key == "space":
            for (agent_name, source_id), source_data in self.agent_dict.items():
                agent = source_data["agent"]
                trigger = source_data["trigger"]
                if trigger == AgentTriggerType.TRIGGER_ON:
                    agent.trigger(AgentTriggerType.TRIGGER_OFF, source_id)
                    wait_time, infer_result = self.event_catcher.wait_final_process(agent)
                    self.agent_dict[(agent_name, source_id)]["trigger"] = AgentTriggerType.TRIGGER_OFF
                    delimiter_str = "\n-----------------------------------------------------------\n"
                    logger.info(f"{delimiter_str}INFERENCE : {int(infer_result['label'])} (in {round(wait_time, 2)}s){delimiter_str}")
                    agent.set_record_mode(AgentRecordMode.DAVINSY_RECORD_BACKGROUND, source_id)


def load_module_from_file(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def get_connector_from_path(connector_path: Path) -> Connector:
    try:
        module = load_module_from_file(connector_path, connector_path.stem)
    except ImportError as e:
        print(f"Error importing module: {e}")
        return None

    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, Connector) and obj != Connector:
            return obj()


def live_workflow(agent: Agent, connector: Connector):
    set_callbacks(agent)
    force_train(agent)
    keyboard_listen = Keyboard_Listener()
    keyboard_listen.subscribe_agent(agent)
    connector.subscribe_agent(agent)
    connector.open()
    connector.start()
    connector.start_sending()
    keyboard_listen.start()
    connector.stop_sending()
    kill(agent)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Run standard scenario")
    parser.add_argument("connector", type=Path, help="Path of the connector python file to use")
    parser.add_argument("-ag", "--agent",type=str, default=None, help="Agent Name")
    parser.add_argument("-gh", "--host", type=str, default="127.0.0.1", help="Gateway host")
    parser.add_argument("-gp", "--port", type=int, default=8765, help="Gateway port")
    parser.add_argument("-i", "--incremental", action="store_true",
                        help="If given, run incremental learning scenario instead")
    args = parser.parse_args()

    R.gateway = Gateway(args.host, args.port, secure=args.port == 443)
    R.gateway.connect()
    logger.info("WAITING")

    wait_for_agent(args.agent)
    if R.current_agent is not None:
        logger.info("STARTING")
        R.current_agent.subscribe()
        connector = get_connector_from_path(args.connector)
        live_workflow(R.current_agent, connector)
    time.sleep(0.1)
    R.gateway.close()
