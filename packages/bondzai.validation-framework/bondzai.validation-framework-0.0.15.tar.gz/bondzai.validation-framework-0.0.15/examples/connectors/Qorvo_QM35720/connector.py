import json
from pathlib import Path
import sys
from bondzai.validation_framework.connector_handler import Connector
from bondzai.validation_framework.log_handler import logger
sys.path.append((Path(__file__).parent / "resources" / "Radar").as_posix())
from spi.spi_Cheetah import SpiCheetah
from radar import Radar

DEFAULT_SETTING_WINDOW = {"device": "Dev0", "clock_rate": 15000000,
                          "idx_cir_start": 745, "idx_cir_end": 809,
                          "timer_clk_div": 7, "timer_period": 1666,
                          "run_time": 10, "frame_log_mode": 0}


class QorvoConnector(Connector):
    def __init__(self, configPath: Path = None):
        # spi_log_name = f"spi-{datetime.datetime.now().strftime('%y-%m-%d-%Hh%Mm%Ss')}.log"
        # spi_logger = SpiLog(spi_log_name)
        spi_logger = None
        try:
            if configPath is not None:
                with open(configPath, 'r') as f:
                    radar_settings = json.load(f)
            else:
                radar_settings = DEFAULT_SETTING_WINDOW
        except Exception as e:
            logger.info(f"Invalid Radar Settings.\n{e}")
            radar_settings = None
        if radar_settings:
            driver = SpiCheetah(spi_logger)
            logger.info("Using Cheetah SPI to USB interface")
            self._radar = Radar(spi_driver=driver, device=radar_settings['device'],
                                clock_rate=radar_settings['clock_rate'],
                                idx_cir_start=radar_settings['idx_cir_start'],
                                idx_cir_end=radar_settings['idx_cir_end'],
                                timer_clk_div=radar_settings['timer_clk_div'],
                                timer_period=radar_settings['timer_period'],
                                frame_log_mode=radar_settings['frame_log_mode'])

        self.frame_size = radar_settings['idx_cir_end'] - radar_settings['idx_cir_start']
        self.cfg = self._radar.get_config()
        # self._radar.get_reg_dump('radar_before_config.regdump')
        super(QorvoConnector, self).__init__()

    def open(self, **kwargs):
        # self._radar.get_reg_dump('radar_after_config.regdump')
        self._radar.start()

    def read(self, timeout: float = None):
        data = self._radar.get_CIR()
        chunk = data["Ipatov CIR"]["re"] + data["Ipatov CIR"]["im"]
        return chunk

    def write(self):
        pass

    def close(self):
        self._radar.stop()
        # self._radar.get_reg_dump('radar_after_stop.regdump')
