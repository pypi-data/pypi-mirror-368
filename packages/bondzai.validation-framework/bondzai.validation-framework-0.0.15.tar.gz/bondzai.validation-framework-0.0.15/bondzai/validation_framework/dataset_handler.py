# All that is needed to load the dataset

import yaml
import struct
from pathlib import Path
from .tar_handler import Tar
from bondzai.gateway_sdk.agent import Agent
from bondzai.gateway_sdk.enums import AgentAIType
from .result_handler import ResultGatherer
from typing import Union

UNKNOWN = "unknown"


class Data:
    """
    Class representing one recording to be end for inference, enrollment or correction, generated exclusively by Dataset
    """
    def __init__(self,  id: str, agent_input: list[float] = [], agent_output: list[float] = [],
                 agent_source: int = None, metadata: dict = {}, output: dict = {}):
        self.id = id
        self.agent_input = agent_input
        self.agent_output = agent_output
        self.agent_source = agent_source
        self.metadata = metadata
        self.output = output

    def send_input_to_agent(self, agent: Agent, chunk_size: int = 1024, chunk_rate: int = 10):
        """
        Send input data to given agent
        Args:
            agent: Agent object
            chunk_size: size of one chunk
            chunk_rate: rate in chunk / s
        """
        agent.send_data(self.agent_source, self.agent_input, chunk_size, chunk_rate)

    def send_correction_to_agent(self, agent: Agent, position: int = 0, remove: bool = False):
        """
        Send known output of data to agent for correction
        Args:
            agent: Agent object
            position: position of the data in the agent database, by default 0 representing last inference
            remove: If True, remove correction instead
        """
        agent.correct(self.agent_output, self.agent_source, position, remove)

    def add_to_expected_result(self, result: ResultGatherer):
        """
        Add current data output to expected section of ResultGatherer
        Args:
            result: ResultGatherer object
        """
        for key, value in self.output.items():
            result.add_expected(self.id, key, value)

    def add_to_predicted_result(self, result: ResultGatherer):
        """
        Add current data output to predicted section of ResultGatherer
        Args:
            result: ResultGatherer object
        """
        for key, value in self.output.items():
            result.add_predicted(self.id, key, value)
    
    def copy(self):
        return Data(self.id, self.agent_input, self.agent_output, self.agent_source, self.metadata, self.output)
    
    def split_data(self, frame_len: int, hop_len: int) -> list:
        parts = 0
        data_list = []
        data = self.copy()
        data.id = data.id + "." +str(parts)
        data.agent_input = self.agent_input[0: frame_len]
        data_list.append(data)
        idx = frame_len
        parts += 1       
        while idx + hop_len <= len(self.agent_input):
            data = self.copy()
            data.id = data.id + "." +str(parts)
            data.agent_input = self.agent_input[idx: idx + hop_len]
            data_list.append(data)
            idx +=hop_len
            parts += 1

        return data_list



class Dataset:
    """
    Dataset.yml loader and handler
    """
    def __init__(self, tar_path: Path, agent: Agent):
        """
        Init object
        Args:
            tar_path: path of the tar.gz file containing binary data + dataset.yml
            agent: Agent object
        """
        self.tar = Tar(tar_path)
        file = self.tar.get_file("dataset.yml")
        data_dict = yaml.safe_load(file)
        self.outputs = data_dict["outputs"]
        self.data_list = data_dict["dataset"]
        self.source = None
        asl_meta = agent.get_asl_meta()
        self.lookup_table = asl_meta["apps"][0]["meta"]["tables"]
        self.source_config_table = asl_meta["apps"][0]["meta"]["sources"]
        self.reversed_lookup_table = self.reverse_dict(self.lookup_table)
        self.reversed_outputs = self.reverse_dict(self.outputs)

    @staticmethod
    def reverse_dict(initial_dict: dict) -> dict:
        """
        Reverse dictionary sub dict as correspondence are one to one
        Args:
            initial_dict: initial dict
        Returns:
            reversed_dict: reversed version of the dict

        """
        reversed_dict = {}
        for key, value_dict in initial_dict.items():
            reversed_dict[key] = {_value: _key for _key, _value in value_dict.items()}
        return reversed_dict

    def iter_source(self, source_name: str = None):
        """
        Iterator to get Data objects for a given source
        Args:
            source_name: name of the source to get data from
        """
        for raw_data_dict in self.data_list:
            hop_len = 0
            frame_len = 0
            if source_name is None or raw_data_dict.get("source_id", None) == source_name:
                source_id = str(self.source_name_to_id(raw_data_dict.get("source_id", None)))
                if source_id in self.source_config_table:
                    hop_len = self.source_config_table[source_id]["hop_len"]
                    frame_len = self.source_config_table[source_id]["frame_len"]
                data = self.get_data_from_dict(raw_data_dict)
                if hop_len == 0:
                    data_list = [data]
                else:
                    data_list = data.split_data(frame_len, hop_len)
                for data in data_list:
                    yield data

    def get_sources_list(self) -> list:
        """
        Get list of all sources in dataset
        """
        return list(set([raw_data_dict["source_id"] for raw_data_dict in self.data_list]))

    def get_output_type_list(self) -> list:
        """
        Get list of all output types in dataset
        """
        output_type_list = []
        for raw_data_dict in self.data_list:
            for key in raw_data_dict["output"].keys():
                if key not in output_type_list:
                    output_type_list.append(key)
        return output_type_list

    def translate(self, event_dict: dict) -> dict:
        """
        Translate an event_dict to plain string labels and values
        Args:
            event_dict: event dict send by the gateway
        Returns:
            translated_dict: translated dict replacing index and ID by plain strings
        """
        translated_dict = {}
        label_name = self.lookup_table["labels"][str(event_dict.get("label_type", 0))]
        for key, value in event_dict.items():
            if key == "ai_type":
                translated_dict[key] = AgentAIType(value)
            elif key == "label_type":
                translated_dict[key] = label_name
            elif key == "step":
                translated_dict[key] = self.lookup_table["steps"].get(str(value), "Undefined")
            elif key == "confidences":
                confidences = {self._label_int_to_name(label_name, _key): _value for _key, _value in value.items()}
                translated_dict[key] = confidences
            elif key == "label":
                translated_dict[key] = self._label_int_to_name(label_name, int(value))
            else:
                translated_dict[key] = value
        return translated_dict

    # ------------ DATA OBJECTS RELATED FUNCTIONS ------------

    def get_data_from_dict(self, raw_data_dict: dict) -> Data:
        """
        Convert data dict from dataset.yml to Data object
        Args:
            raw_data_dict: data dict as in yml file
        Returns:
            data: Data object

        """
        file_name = Path(raw_data_dict["data"]).name
        bin_data = self.tar.get_file(file_name).read()
        in_data = [_[0] for _ in struct.iter_unpack("<f", bin_data)]
        source_id = self.source_name_to_id(raw_data_dict.get("source_id", None))
        out_data = self._output_dict_to_list(raw_data_dict["output"])
        data = Data(id=file_name, agent_input=in_data, agent_output=out_data, agent_source=source_id,
                    metadata=raw_data_dict["metadata"], output=raw_data_dict["output"])
        return data

    def get_data_by_file_name(self, file_name: str) -> Data:
        """
        Get data dict from file name
        Args:
            file_name: name of the file
        Returns:
            data: Data object
        """
        data = None
        for raw_data_dict in self.data_list:
            if Path(raw_data_dict["data"]).name == file_name:
                data = self.get_data_from_dict(raw_data_dict)
                break
        return data

    def update_data_from_event(self, data: Data, *event_dict_list: dict) -> Data:
        """
        Transform given data object according to inference messages
        Args:
            data: Data object
            event_dict_list: list of event dict send by the gateway
        Returns:
            data: new Data object with updated output values
        """
        output_dict = {}
        for event_dict in event_dict_list:
            label_name = self._label_type_id_to_name(event_dict["label_type"])
            label = self._label_int_to_name(label_name, int(event_dict["label"]))
            output_dict[label_name] = label

        output_list = self._output_dict_to_list(output_dict)

        new_data = Data(id=data.id, agent_input=data.agent_input,
                        agent_output=output_list, agent_source=data.agent_source,
                        metadata=data.metadata, output=output_dict)
        return new_data

    # ------------ INTERNAL CONVERSION FUNCTIONS ------------

    def _output_dict_to_list(self, output_dict) -> list[float]:
        """
        Convert output dict to output list readable by agent
        Args:
            output_dict: output dict
        Returns:
            output_list: output as list of float to be read by agent
        """
        output_list = []
        # TODO : handle regression
        for label_type, label in output_dict.items():
            label_type_id = self._label_type_name_to_id(label_type)
            label_value = self._label_name_to_int(label_type, label)
            output_list += [label_type_id, label_value]
        return output_list

    def _label_type_name_to_id(self, label_type: str) -> int:
        """
        Convert a given label type from name to id
        Args:
            label_type: type of the label

        Returns:
            label_type_id: ID of type of the label

        """
        label_type_id = int(self.reversed_lookup_table["labels"].get(label_type, 0))
        return label_type_id

    def _label_type_id_to_name(self, label_type_id: int) -> str:
        """
        Convert a given label type from id to name
        Args:
            label_type_id: ID of type of the label

        Returns:
            label_type: type of the label

        """
        label_type = self.lookup_table["labels"].get(str(label_type_id), UNKNOWN)
        return label_type

    def _label_int_to_name(self, label_type: str, value: int) -> str:
        """
        Convert a given label from int to string
        Args:
            label_type: type of the label
            value: value of the label as used by agent (int)

        Returns:
            label: label value as string

        """
        label_dict = self.reversed_outputs.get(label_type, {})
        label = label_dict.get(value, UNKNOWN)
        return label

    def _label_name_to_int(self, label_type: str, label: str) -> int:
        """
        Convert a given label from string to int
        Args:
            label_type: type of the label
            label: label value as string

        Returns:
            value: value of the label as used by agent (int)

        """
        label_dict = self.outputs.get(label_type, {})
        value = int(label_dict.get(label, 0))
        return value

    def source_name_to_id(self, source_name: Union[str, None]) -> int:
        """
        Convert given source from name to ID
        Args:
            source_name: name of the source as string
        Returns:
            source_id: ID of the source as used in agent
        """
        source_dict = self.reversed_lookup_table.get("sources", {})
        source_id = int(source_dict.get(source_name, 0))
        return source_id
