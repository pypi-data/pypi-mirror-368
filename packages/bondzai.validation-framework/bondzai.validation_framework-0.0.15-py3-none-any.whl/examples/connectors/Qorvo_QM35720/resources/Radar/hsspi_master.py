#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""hsspi_master.py: A python HSSPI compatible spi driver

Provides a class allowing read/write/open/close a SPI adapter,
and adding the correct STC header to the payload corresponding to the transation.

"""

from enum import IntFlag
from typing import Tuple

from spi.spi_config import SpiCSPol, SpiMode


class SOC_STC_FLAG(IntFlag):
    SOC_SPI_DATA_WAITING_BIT = 0x88
    SOC_SPI_OUT_ACTIVE_BIT = 0x44
    SOC_SPI_RDY_BIT = 0x22
    SOC_SPI_ERROR_BIT = 0x11


class HOST_STC_FLAG(IntFlag):
    HOST_SPI_WRITE_BIT = 0x80
    HOST_SPI_PREREAD_BIT = 0x40
    HOST_SPI_READ_BIT = 0x20


def make_stc_header(flags: HOST_STC_FLAG, length: int = 0) -> Tuple[int]:
    assert length <= (2**16-1)
    return flags.value, 0x05, length & 0xFF, (length >> 8) & 0xFF


def parse_stc_header(header: Tuple) -> Tuple[SOC_STC_FLAG, int]:
    length = int.from_bytes(header[2:4], 'little', signed=False)
    flags = SOC_STC_FLAG(header[0])
    return flags, length


class Hsspi():
    def __init__(self, SpiDriver):
        self._spi = SpiDriver
        self.DELAY_us = 1

    def open_channel(self, device: dict):
        return self._spi.open_channel(device)

    def init_channel(self,
                     clock_rate: int = 10000000,
                     latency_timer: int = 255,
                     mode: SpiMode = SpiMode.MODE_0,
                     cs_polarity: SpiCSPol = SpiCSPol.ACTIVE_LOW):
        return self._spi.init_channel(clock_rate, latency_timer, mode, cs_polarity)

    def close_channel(self):
        return self._spi.close_channel()

    def write(self, write_data) -> int:
        flag = 0
        # print('Polling Ready Bit')
        while not flag & SOC_STC_FLAG.SOC_SPI_RDY_BIT:
            flag, _ = self.read_stc()
            self.delay_us(self.DELAY_us)
        # Write command.
        ret = self._cmd_write(write_data)
        self._spi.delay_us(self.DELAY_us)
        return ret

    def read(self, size: int) -> list:
        # write a preread,
        # poll for the SOC_SPI_DATA_WAITING_BIT,
        # write a read but do not toggle CS at the end of transaction
        # read.
        # print('Polling Data Waiting Bit')
        flag = 0
        retry = 0
        while not (flag & SOC_STC_FLAG.SOC_SPI_DATA_WAITING_BIT):
            flag, _ = self.read_stc()
            retry += 1
            if retry > 20:
                return None
            self.delay_us(self.DELAY_us)
        self._cmd_preread()
        self._spi.delay_us(self.DELAY_us)
        self._cmd_read(size)
        data = self._spi.read(size, True, True)
        # At times the OUTPUT_ACTIVE BITS are still set after reading.
        self._spi.delay_us(self.DELAY_us)
        flag, _ = self.read_stc()
        self._spi.delay_us(self.DELAY_us)
        # if (flag & SOC_STC_FLAG.SOC_SPI_OUT_ACTIVE_BIT):
        #     #Do a dummy read to clear this flag.
        #     self._cmd_read(size)
        #     self._spi.read(size, True, True)
        return data

    def read_stc(self):
        data = self._spi.read(4)
        # print(f'rx stc: {[hex(i) for i in data]}')
        return parse_stc_header(data)

    def _cmd_write(self, write_data):
        # Write command.
        header = make_stc_header(HOST_STC_FLAG.HOST_SPI_WRITE_BIT, len(write_data))
        to_send = header + tuple(write_data)
        # print(f'tx write: {[hex(i) for i in to_send]}')
        return self._spi.write(to_send, True, True)

    def _cmd_preread(self):
        # Pre-read command.
        header = make_stc_header(HOST_STC_FLAG.HOST_SPI_PREREAD_BIT, 0)
        # print(f'tx preread: {[hex(i) for i in header]}')
        self._spi.write(header, True, True)

    def _cmd_read(self, rx_size):
        # Read command
        header = make_stc_header(HOST_STC_FLAG.HOST_SPI_READ_BIT, rx_size)
        # print(f'tx read: {[hex(i) for i in header]}')
        self._spi.write(header, True, False)

    def write_read(self, write_data, rx_size) -> list:
        # self._spi._logger.log_str('+++hsspi write_read+++')
        # self._spi._logger.log_str('hsspi write:')
        self.write(write_data)
        # self._spi._logger.log_str('hsspi read:')
        rx = self.read(rx_size)
        # self._spi._logger.log_str('---hsspi write_read---')
        return rx

    def get_status_code(self) -> str:
        return self._spi.get_status_code()

    def delay_us(self, delay: int):
        self._spi.delay_us(delay)
