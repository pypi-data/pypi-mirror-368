#! python

import math

from enum import IntFlag
from pathlib import Path
from time import time

from checksum import chksum16
from hsspi_master import Hsspi
from radio_config import Radio_config


MAX_SPI_RX = 4092
MAX_CIR_LEN = 1024
CIA_REGS_SIZE = 43  # 0xA8>>2
DIAG_SIZE_SINGLE_RX = (5+(13*5))   # 20B + (13 DIAG_REG* 5 CIRs)
RADAR_DATA_MIN_SIZE = (4 + CIA_REGS_SIZE + DIAG_SIZE_SINGLE_RX)*4


class SPICmd(IntFlag):
    GET_CONFIG = 0x00
    GET_CONFIG_RESP_LEN = 24
    RADAR = 0x01
    GET_REG_DUMP = 0x02
    GET_REG_DUMP_RESP_LEN = 1708
    SET_CONFIG = 0x03


class RadarSubCmd(IntFlag):
    START = 0x00
    IS_DATA_AVAILABLE = 0x01
    IS_DATA_AVAILABLE_RSP_LEN = 0x04
    GET_DATA = 0x02
    STOP = 0x03


class TimerClkDiv(IntFlag):
    DWT_XTAL = 0         # 38.4 MHz
    DWT_XTAL_DIV2 = 1    # 19.2 MHz
    DWT_XTAL_DIV4 = 2    # 9.6 MHz
    DWT_XTAL_DIV8 = 3    # 4.8 MHz
    DWT_XTAL_DIV16 = 4   # 2.4 MHz
    DWT_XTAL_DIV32 = 5   # 1.2 MHz
    DWT_XTAL_DIV64 = 6   # 0.6 MHz
    DWT_XTAL_DIV128 = 7  # 0.3 MHz


class FrameLogMode(IntFlag):
    WINDOW = 0
    FIRST_PATH_CENTRIC = 1


def int16_to_list(x):
    return [x & 0xFF, (x >> 8) & 0xFF]


def list_byte_to_int(data, offset, size, signed, width):
    return [int.from_bytes(data[i:i+width], 'little', signed=signed)
            for i in range(offset, size+offset, width)]


class Radar():
    def __init__(self, spi_driver, device, clock_rate, idx_cir_start, idx_cir_end,
                 timer_clk_div, timer_period, frame_log_mode):
        ret = spi_driver.get_channel_info()
        self.hsspi = Hsspi(spi_driver)
        self.hsspi.open_channel(ret[device])
        self.hsspi.init_channel(clock_rate=clock_rate, latency_timer=1)
        self.clock_rate = clock_rate
        self.idx_cir_start = idx_cir_start
        self.idx_cir_end = idx_cir_end
        self.timer_clk_div = timer_clk_div
        self.timer_period = timer_period
        self.frame_log_mode = frame_log_mode
        if (frame_log_mode == FrameLogMode.FIRST_PATH_CENTRIC):
            if ((idx_cir_end - idx_cir_start > MAX_CIR_LEN) or (idx_cir_end < idx_cir_start)):
                idx_cir_start = -32
                idx_cir_end = 32
            self.data_tx_size = RADAR_DATA_MIN_SIZE + (idx_cir_end - idx_cir_start) * 8
        else:
            if (idx_cir_start >= MAX_CIR_LEN):
                idx_cir_start = 0

            if (idx_cir_end > MAX_CIR_LEN):
                idx_cir_end = MAX_CIR_LEN

            if ((idx_cir_end - idx_cir_start > MAX_CIR_LEN) or (idx_cir_start > idx_cir_end)):
                idx_cir_start = 0
                idx_cir_end = MAX_CIR_LEN

            self.data_rx_size = RADAR_DATA_MIN_SIZE + (idx_cir_end - idx_cir_start) * 8
        self.frame_size = idx_cir_end - idx_cir_start
        self.timeout = 1  # 1 second timeout

        self.data = []
        self.stopped = False

    def _is_data_available(self):
        msg = [SPICmd.RADAR, RadarSubCmd.IS_DATA_AVAILABLE, 0x00, 0x00]
        rx = self.hsspi.write_read(msg, RadarSubCmd.IS_DATA_AVAILABLE_RSP_LEN)
        # print(f'rx read: {[hex(i) for i in rx]}')
        if not rx:
            return 0
        else:
            crc1 = int.from_bytes(rx[:2], 'little', signed=False)
            crc2 = chksum16(rx[2:4])
            if crc1 == crc2:
                return int.from_bytes(rx[:2], 'little', signed=False)
            else:
                print('rad.is_data_available() CRC Error:'
                      f'{hex(crc1)} (transfered) != {hex(crc2)} (computed)')
                if self.hsspi._spi._logger:
                    self.hsspi._spi._logger.log_str('is_data_available: CRC error')
                return 0

    def _get_data(self, size):
        # print(f'size {size}')
        rem = size
        offset = 0
        data = []
        offsets = []
        while offset < size:
            offsets.append(offset)
            rx_len = min(rem, MAX_SPI_RX)
            msg = ([SPICmd.RADAR, RadarSubCmd.GET_DATA]
                   + int16_to_list(offset)
                   + int16_to_list(rx_len)
                   + [0x00, 0x00])
            rx = self.hsspi.write_read(msg, rx_len)
            # print(f'len(rx) {len(rx)} rem {rem}')
            if not rx:
                # wait a little bit and retry...
                self.hsspi.delay_us(200)
            elif len(rx) == rx_len:
                # d = [hex(_d, ) for _d in rx]
                data += rx
                rem -= rx_len
                offset += rx_len
        crc1 = int.from_bytes(data[:2], 'little', signed=False)
        crc2 = chksum16(data[2:])
        if not crc1 == crc2:
            print(f'offsets: {offsets}')
            print(f'CRC Error: {hex(crc1)} (transfered) != {hex(crc2)} (computed)')
            if self.hsspi._spi._logger:
                self.hsspi._spi._logger.log_str('get_data: CRC error')
            err_dat = []
            for i, d in enumerate(data):
                if not d == 0x33:
                    err_dat += [i, hex(d)]
            print(f'err_dat: {err_dat}')
            return []
        # GET_DATA with LEN == 0 does not get data but dequeue (and drop) a frame
        # in the QM35 internal queue
        msg = [SPICmd.RADAR, RadarSubCmd.GET_DATA] + [0x00, 0x00] + [0x00, 0x00] + [0x00, 0x00]
        self.hsspi.write(msg)

        return data[4:]

    def _parse_data_to_entry(self, frame_num: int, data: list):
        entry = {}
        entry['Frame'] = frame_num
        offset = 0
        entry['Frame Ok Counter'] = hex(int.from_bytes(data[offset:4], 'little', signed=False))
        offset += 4
        entry['Frame Error Counter'] = hex(int.from_bytes(data[offset:8], 'little', signed=False))
        offset += 4
        entry['Timestamps'] = {'TX Timestamp': hex(int.from_bytes(data[offset:12],
                               'little', signed=False))}
        offset += 4
        cia_regs = list_byte_to_int(data, offset, CIA_REGS_SIZE*4, False, 4)
        entry['CIA Registers'] = {f'{hex(0x0C0000 + i * 4)}': hex(d)
                                  for i, d in enumerate(cia_regs)}
        offset += CIA_REGS_SIZE*4
        cia_diag = list_byte_to_int(data, offset, DIAG_SIZE_SINGLE_RX*4, False, 4)
        entry['CIA Diagnostics'] = {f'{hex(0x150000 + i * 4)}': hex(d)
                                    for i, d in enumerate(cia_diag)}
        offset += DIAG_SIZE_SINGLE_RX*4
        cia_data = list_byte_to_int(data, offset, len(data)-offset, True, 4)
        ip_cir_re = []
        ip_cir_im = []
        ip_cir_z = []
        for i in range(0, len(cia_data), 2):
            re = cia_data[i]
            im = cia_data[i+1]
            ip_cir_re.append(re)
            ip_cir_im.append(im)
            ip_cir_z.append(math.sqrt(re*re + im*im))
        entry['Ipatov CIR'] = {'re': ip_cir_re, 'im': ip_cir_im, 'z': ip_cir_z}
        entry['STS CIRS'] = []

        return entry

    def start(self) -> None:
        self.hsspi.delay_us(3000)
        msg = ([SPICmd.RADAR, RadarSubCmd.START]
               + int16_to_list(self.idx_cir_start)
               + int16_to_list(self.idx_cir_end)
               + [self.timer_clk_div & 0xFF]
               + int16_to_list(self.timer_period)
               + [self.frame_log_mode & 0xFF]
               + [0x00, 0x00])
        _ = self.hsspi.write(msg)
        self.frame_nb = 0

    def stop(self):
        self.hsspi.delay_us(1000)
        msg = [SPICmd.RADAR, RadarSubCmd.STOP] + [0x00, 0x00]
        _ = self.hsspi.write(msg)

    def get_CIR(self) -> dict:
        now = time()
        while (time() - now) < self.timeout:
            self.hsspi.delay_us(750)
            dlen = self._is_data_available()
            # print(f'{len(self.frames["Frames"])} rad.is_data_available() = {dlen}')
            if dlen:
                d = self._get_data(dlen)
                if len(d):
                    entry = self._parse_data_to_entry(self.frame_nb, d)
                    self.frame_nb += 1
                    return entry
        return None

    def get_config(self):
        rx = self.hsspi.write_read([SPICmd.GET_CONFIG, 0x00, 0x00, 0x00],
                                   SPICmd.GET_CONFIG_RESP_LEN)
        assert(rx)
        cfg = {}
        offset = 0
        cfg['chan'] = hex(int.from_bytes(rx[offset:offset+2], 'little', signed=False))
        offset += 2
        cfg['txPreambLength'] = hex(int.from_bytes(rx[offset:offset+2], 'little', signed=False))
        offset += 2
        cfg['rxPAC'] = hex(rx[offset])
        offset += 1
        cfg['txCode'] = hex(rx[offset])
        offset += 1
        cfg['rxCode'] = hex(rx[offset])
        offset += 1
        cfg['sfdType'] = hex(rx[offset])
        offset += 1
        cfg['dataRate'] = hex(rx[offset])
        offset += 1
        cfg['phrMode'] = hex(rx[offset])
        offset += 1
        cfg['phrRate'] = hex(rx[offset])
        offset += 1
        cfg['sfdTO'] = hex(int.from_bytes(rx[offset:offset+2], 'little', signed=False))
        offset += 2
        cfg['stsMode'] = hex(rx[offset])
        offset += 1
        cfg['stsLength'] = hex(rx[offset])
        offset += 1
        cfg['pdoaMode'] = hex(rx[offset])
        offset += 1
        cfg['PGdly'] = hex(rx[offset])
        offset += 1
        cfg['power'] = hex(int.from_bytes(rx[offset:offset+4], 'little', signed=False))
        offset += 4
        cfg['PGcount'] = hex(int.from_bytes(rx[offset:offset+2], 'little', signed=False))
        return cfg

    def set_config(self, cfg: dict):
        # Validate provided configuration
        valid_conf = Radio_config(cfg)
        to_send = []
        to_send += [valid_conf['chan']]
        to_send += [0]
        to_send += [valid_conf['txPreambLength'] & 0xFF]
        to_send += [(valid_conf['txPreambLength'] >> 8) & 0xFF]
        to_send += [valid_conf['rxPAC']]
        to_send += [valid_conf['txCode']]
        to_send += [valid_conf['rxCode']]
        to_send += [valid_conf['sfdType']]
        to_send += [valid_conf['dataRate']]
        to_send += [valid_conf['phrMode']]
        to_send += [valid_conf['phrRate']]
        to_send += [valid_conf['sfdTO'] & 0xFF]
        to_send += [(valid_conf['sfdTO'] >> 8) & 0xFF]
        to_send += [valid_conf['stsMode']]
        to_send += [valid_conf['stsLength']]
        to_send += [valid_conf['pdoaMode']]
        to_send += [valid_conf['PGdly']]
        to_send += [valid_conf['power'] & 0xFF]
        to_send += [(valid_conf['power'] >> 8) & 0xFF]
        to_send += [(valid_conf['power'] >> 16) & 0xFF]
        to_send += [(valid_conf['power'] >> 24) & 0xFF]
        to_send += [valid_conf['PGcount'] & 0xFF]
        to_send += [(valid_conf['PGcount'] >> 8) & 0xFF]
        to_send += [0]
        self.hsspi.write([SPICmd.SET_CONFIG, 0x00, 0x00, 0x00] + to_send)

    def get_reg_dump(self, fname):
        script_dir = Path(__file__).parent.absolute()
        with open(script_dir / 'regdump_template.txt', 'r') as f:
            regdump_lines = f.readlines()
            self.hsspi.delay_us(1000)
            rx = self.hsspi.write_read([SPICmd.GET_REG_DUMP, 0x00, 0x00, 0x00],
                                       SPICmd.GET_REG_DUMP_RESP_LEN)
            assert(rx)
            regs = []
            offset = 0
            while(offset < len(rx)):
                regs.append(hex(int.from_bytes(rx[offset:offset+4], 'little', signed=False)))
                offset += 4
            new_lines = []
            for i in range(len(regdump_lines)):
                new_line = regdump_lines[i].format(str(regs[i])).upper()
                new_lines.append(new_line)
        with open(fname, 'w') as f:
            f.writelines(new_lines)
