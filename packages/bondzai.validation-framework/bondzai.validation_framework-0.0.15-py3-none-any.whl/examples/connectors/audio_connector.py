from bondzai.validation_framework.connector_handler import Connector
from bondzai.validation_framework.log_handler import logger
import sounddevice as sd
import sys

class AudioConnector(Connector):
    """
    Example of connector for audio stream (PC microphone)
    """
    def __init__(self):
        self.stream = None
        self.chunk_size = None
        super(AudioConnector, self).__init__()

    def open(self):
        """
        Open connection to sensor
        """
        default_device_idx = sd.default.device
        fs = 16000
        channel_nb = 1
        self.chunk_size = 1024

        try:
            self.stream = sd.InputStream(samplerate=fs, channels=channel_nb, device=default_device_idx,
                                         blocksize=self.chunk_size, dtype="int16")
            self.stream.start()
        except Exception:
            self.stream = None
            logger.error("Could not open stream, please check your device index / number of channels")
            sys.exit(1)

    def read(self, timeout: float = None):
        data = (self.stream.read(self.chunk_size)[0]).astype(float) / (2 ** 15)
        data = data.flatten().tolist()
        return data

    def close(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
