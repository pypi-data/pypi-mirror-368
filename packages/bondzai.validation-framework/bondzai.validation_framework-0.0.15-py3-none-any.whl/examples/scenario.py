import threading
import time
import json

import numpy as np
from bondzai.gateway_sdk import Gateway, Agent
from bondzai.gateway_sdk.enums import EventOperationID, DBMTable, AgentAIMode, AgentTriggerType, AgentRecordMode
from bondzai.validation_framework.log_handler import array_to_str, logger
from bondzai.validation_framework.result_handler import EXPECTED, PREDICTED
from bondzai.validation_framework.dataset_handler import Dataset, Data
from bondzai.validation_framework.event_catcher import EventCatcher
from bondzai.validation_framework.result_handler import ResultGatherer, NumpyEncoder
from pathlib import Path
import argparse


# To be run with OCR agent
DEFAULT_CHUNK_RATE = 500
DEFAULT_CHUNK_SIZE = 1024


def training_is_done(agent: Agent, status):
    logger.info(f"EVT TRAIN : {status}")


def log_print(agent: Agent, log_message):
    logger.info(log_message)


def print_event(agent: Agent, event_id: EventOperationID, data: dict):
    logger.info(f"EVT {event_id.name} : {data}")


def print_event_final(agent: Agent, data: dict):
    logger.info(f"EVT FINALE {data}")


def print_event_infer(agent: Agent, data: dict):
    logger.info(f"EVT INFER {data}")

def print_event_datatransform(agent: Agent, data: dict):
    logger.info(f"EVT DT {data}")
    # result = data.get("result")

def set_callbacks(agent: Agent):
    # Set callbacks
    agent.on_log(log_print)
    agent.on_event(print_event)
    agent.on_training_done(training_is_done)
    agent.on_inference_result(print_event_infer)
    agent.on_final_process_result(print_event_final)
    agent.on_data_transform_result(print_event_datatransform)


def force_train(agent: Agent):
    """
    Force agent to train
    """
    event_catcher = EventCatcher()
    # wait to allow davinsy to finish previous all tasks
    time.sleep(0.01)
    agent.train()
    event_catcher.wait_training(agent)
    # wait to allow davinsy to finish all training tasks
    time.sleep(0.01)


def infer_one(agent: Agent, data: Data, start_trigger: AgentTriggerType = AgentTriggerType.TRIGGER_ON,
              end_trigger: AgentTriggerType = AgentTriggerType.TRIGGER_ON,
              chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_rate: int = DEFAULT_CHUNK_RATE):
    """
    Perform one inference
    Args:
        agent: Agent object
        data: Data object
        start_trigger: If needed, define function used for start trigger
        end_trigger: If needed, define function used for end trigger
        chunk_size: Size of one chunk
        chunk_rate: chunk rate (in chunk/s)
    """
    if start_trigger is not None:
        agent.trigger(start_trigger,data.agent_source)
    data.send_input_to_agent(agent, chunk_size, chunk_rate)
    if end_trigger is not None:
        agent.trigger(end_trigger,data.agent_source)


def infer_all(agent: Agent, dataset: Dataset, start_trigger: AgentTriggerType = AgentTriggerType.TRIGGER_ON,
              end_trigger: AgentTriggerType = AgentTriggerType.TRIGGER_OFF, chunk_size: int = DEFAULT_CHUNK_SIZE,
              chunk_rate: int = DEFAULT_CHUNK_RATE, save_path: Path = None) -> dict:
    """

    Args:
        agent: Agent object
        dataset: dataset object
        start_trigger: If needed, define function used for start trigger
        end_trigger: If needed, define function used for end trigger
        chunk_size: Size of one chunk
        chunk_rate: chunk rate (in chunk/s)
        save_path: path of JSON file to save data
    Returns:
        results: results as dict
    """
    res = ResultGatherer(agent)
    event_catcher = EventCatcher()
    data_len = len(dataset.data_list)
    i = 0
    logger.info(f"AIMode: inference, RecordMode:subject")
    agent.set_ai_mode(AgentAIMode.APP_AI_MODE_INFERENCE)
    current_id = ""
    for data in dataset.iter_source():
        new_id_woparts =  data.id.rsplit(".",1)[0]
        if new_id_woparts != current_id:
            # TODO : flush
            agent.set_record_mode(AgentRecordMode.DAVINSY_RECORD_BACKGROUND,data.agent_source)
            agent.set_record_mode(AgentRecordMode.DAVINSY_RECORD_SUBJECT,data.agent_source)
            current_id = new_id_woparts
        infer_one(agent, data, start_trigger, end_trigger, chunk_size, chunk_rate)
        wait_time, infer_result = event_catcher.wait_final_process(agent)
        logger.info(f"New inference, result received after {np.round(wait_time, 2)}s")
        if infer_result is None:
            logger.warning("Missed inference")
        else:
            infer_data = dataset.update_data_from_event(data, infer_result)
            data.add_to_expected_result(res)
            infer_data.add_to_predicted_result(res)
        
        i += 1
        send_to_clients({
            "data-type": "run-progress",
            "progress": (i * 100) / data_len
        })
    results = res.get_results(save_path)
    return results


def infer_all_no_wait(agent: Agent, res: ResultGatherer, dataset: Dataset,
                      start_trigger: AgentTriggerType = AgentTriggerType.TRIGGER_ON,
                      end_trigger: AgentTriggerType = AgentTriggerType.TRIGGER_OFF,
                      chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_rate: int = DEFAULT_CHUNK_RATE):
    agent.set_ai_mode(AgentAIMode.APP_AI_MODE_INFERENCE)  
    current_id = ""
    for data in dataset.iter_source():
        new_id_woparts =  data.id.rsplit(".",1)[0]
        if new_id_woparts != current_id:
            agent.set_record_mode(AgentRecordMode.DAVINSY_RECORD_BACKGROUND,data.agent_source)
            agent.set_record_mode(AgentRecordMode.DAVINSY_RECORD_SUBJECT,data.agent_source)
            current_id = new_id_woparts
        infer_one(agent, data, start_trigger, end_trigger, chunk_size, chunk_rate)
        data.add_to_expected_result(res)
    time.sleep(0.5)
    data.add_to_expected_result(res)


def infer_all_async(agent: Agent, dataset: Dataset, start_trigger: AgentTriggerType = AgentTriggerType.TRIGGER_ON,
                    end_trigger: AgentTriggerType = AgentTriggerType.TRIGGER_OFF, chunk_size: int = DEFAULT_CHUNK_SIZE,
                    chunk_rate: int = DEFAULT_CHUNK_RATE, save_path: Path = None):
    res = ResultGatherer(agent)
    event_catcher = EventCatcher()
    infer_thread = threading.Thread(target=lambda: infer_all_no_wait(agent, res, dataset, start_trigger,
                                                                     end_trigger, chunk_size, chunk_rate), daemon=True)
    infer_thread.start()
    empty_counter = 0
    stop = False
    data_list = []
    while not stop:
        if not infer_thread.is_alive():
            stop = True
        time.sleep(0.5)
        _data_list = event_catcher.get_final_process_data(agent)
        if len(_data_list) == 0:
            empty_counter += 1
        data_list += _data_list
    res_dict = res.get_results_as_list()
    nb_infer_sent = len(list(res_dict.values())[0])
    nb_infer_received = len(data_list)

    if nb_infer_received < nb_infer_sent:
        missed_number = nb_infer_sent - nb_infer_received
        loss_percent = np.round(100 * missed_number / nb_infer_sent, 2)
        logger.warning(f"{missed_number} inferences missed among {nb_infer_sent} inferences ({loss_percent}% loss)")
    else:
        label_type_number = len(dataset.outputs)
        for index, data in enumerate(dataset.iter_source()):
            infer_list = data_list[index * label_type_number: (index + 1) * label_type_number]
            infer_data = dataset.update_data_from_event(data, *infer_list)
            infer_data.add_to_predicted_result(res)
    results = res.get_results(save_path)
    return results


def standard(dataset_path: Path, agent: Agent, sync: bool = True, chunk_size: int = DEFAULT_CHUNK_SIZE,
             chunk_rate: int = DEFAULT_CHUNK_RATE, save_path: Path = None):
    set_callbacks(agent)

    logger.info("---- Switch to infer ----")
    force_train(agent)

    logger.info("---- Get KPI ----")
    kpi = agent.get_kpi()
    logger.info(kpi)

    logger.info("---- Start inferences ----")
    dataset = Dataset(dataset_path, agent)

    if sync:
        results = infer_all(agent=agent,
                            dataset=dataset,
                            save_path=save_path,
                            start_trigger=AgentTriggerType.TRIGGER_ON,
                            end_trigger=AgentTriggerType.TRIGGER_OFF,
                            chunk_size=chunk_size,
                            chunk_rate=chunk_rate)
    else:
        results = infer_all_async(agent=agent,
                                  dataset=dataset,
                                  save_path=save_path,
                                  start_trigger=AgentTriggerType.TRIGGER_ON,
                                  end_trigger=AgentTriggerType.TRIGGER_OFF,
                                  chunk_size=chunk_size, chunk_rate=chunk_rate)

    for key, value in results.items():
        accuracy = np.round(value['accuracy'] * 100, 2) if value["accuracy"] is not None else None
        logger.info(f"\n{key}\n{array_to_str(value['confusion_matrix'])}"
                    f"\n\nAccuracy : {accuracy}%")

    kill(agent)

    return results


def incremental_learning(dataset_path: Path, agent: Agent, chunk_size: int = DEFAULT_CHUNK_SIZE,
                         chunk_rate: int = DEFAULT_CHUNK_RATE):
    CORRECTION_RATIO_THRESHOLD = 0.20
    ACCURACY_THRESHOLD = 0.9

    set_callbacks(agent)

    logger.info("---- Switch to infer ----")
    force_train(agent)

    logger.info("---- Get KPI ----")
    kpi = agent.get_kpi()
    logger.info(kpi)

    logger.info("---- Start inferences ----")
    dataset = Dataset(dataset_path, agent)
    label_type = dataset.get_output_type_list()[0]
    event_catcher = EventCatcher()
    accuracy_vect = [0]
    correction_percent = 0
    exclusion_list = []
    to_correct = True
    counter = 0
    while to_correct and correction_percent < CORRECTION_RATIO_THRESHOLD and accuracy_vect[-1] < ACCURACY_THRESHOLD:
        counter += 1
        to_correct = False
        # Test on all dataset
        results = infer_all(agent, dataset, start_trigger=AgentTriggerType.TRIGGER_ON,
                            end_trigger=AgentTriggerType.TRIGGER_OFF, chunk_size=chunk_size, chunk_rate=chunk_rate)
        result_list = results[label_type]["raw_results"]
        accuracy_vect.append(results[label_type]["accuracy"])
        infer_nb = len(result_list)
        if len(exclusion_list) == infer_nb:
            break
        for key, element in result_list.items():
            if key not in exclusion_list:
                # If not needed to be corrected add to exclusion list
                exclusion_list.append(key)
                # If mismatch between prediction and expectation, perform correction
                if element[PREDICTED] != element[EXPECTED]:
                    correction_percent += 1 / infer_nb
                    to_correct = True
                    data = dataset.get_data_by_file_name(key)
                    infer_one(agent, data, start_trigger=AgentTriggerType.TRIGGER_ON,
                              end_trigger=AgentTriggerType.TRIGGER_OFF, chunk_rate=DEFAULT_CHUNK_RATE)
                    event_catcher.wait_final_process(agent)
                    data.send_correction_to_agent(agent, position=0)
                    force_train(agent)
                    break
                
    # wait last results
    time.sleep(0.5)
    logger.info(f" accuracy_vect {accuracy_vect[1:]}")

    agent.kill()

    return {"accuracy": accuracy_vect[1:]}


def kill(agent: Agent):
    agent.kill()


def export_dataset(agent: Agent):
    data = agent.export_table_data(DBMTable.DBM_DAT)
    logger.info(data)

    agent.kill()


class R:
    gateway: Gateway = None
    current_agent: Agent = None


def send_to_clients(data):
    if not R.gateway:
        return
    R.gateway.send_to_clients(data)

def wait_for_agent(agent_name: str = None):
    if agent_name is None:
        agents = R.gateway.wait_for_agents()
        agent = agents[0]
    else:
        agent = R.gateway.wait_for_agent(agent_name=agent_name)
    R.current_agent = agent
 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Run standard scenario")
    parser.add_argument("dataset", type=Path, help="Path of the dataset tar.gz file")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="Path of the JSON file where inference results are saved")
    parser.add_argument("-s", "--size", type=int, default=DEFAULT_CHUNK_SIZE,
                        help=f"Chunk size (by default {DEFAULT_CHUNK_SIZE})")
    parser.add_argument("-r", "--rate", type=int, default=DEFAULT_CHUNK_RATE,
                        help=f"Chunk rate (by default {DEFAULT_CHUNK_RATE})")
    parser.add_argument("-a", "--asynchro", action="store_true",
                        help="If given, run scenario in async mode")
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

    results = None
    if R.current_agent is not None:
        logger.info("STARTING")
        R.current_agent.subscribe()
        if args.incremental:
            logger.info("incremental_learning")
            results = incremental_learning(dataset_path=args.dataset,
                                 agent=R.current_agent,
                                 chunk_size=args.size,
                                 chunk_rate=args.rate)
        else:
            logger.info("Standard")
            results = standard(dataset_path=args.dataset,
                        agent=R.current_agent,
                        sync=not args.asynchro,
                        save_path=args.output,
                        chunk_size=args.size,
                        chunk_rate=args.rate)
            
    if results:
        try:
            # TMP Solution to pass numy object to gateway JSON encoder
            results_json = json.dumps(results, cls=NumpyEncoder)
            send_to_clients({
                "data-type": "scenario-results",
                "data": json.loads(results_json)
            })
        except Exception as e:
            logger.error(f"Unable to send results to gateway : {str(e)}")
    time.sleep(0.1)
    R.gateway.close()
