#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""spi_Cheetah.py: A python wrapper for the FTDI-provided libMPSSE DLL (SPI only)

"""

import sys
from array import array

from . import cheetah_py, spi_config


class SpiCheetah():
    def __init__(self, logger=None):
        self._status_code = cheetah_py.CH_OK
        self._device = None
        self._handle = 0
        self._logger = logger

    def get_channel_info(self) -> dict:
        # Find all the attached devices
        (numchannels, ports, unique_ids) = cheetah_py.ch_find_devices_ext(16, 16)

        devices = {}

        # Print the information on each device
        for idx in range(numchannels):
            port = ports[idx]
            unique_id = unique_ids[idx]

            # Determine if the device is in-use
            inuse = "(avail)"
            if port & cheetah_py.CH_PORT_NOT_FREE:
                inuse = "(in-use)"
                port = port & ~cheetah_py.CH_PORT_NOT_FREE

            # Display device port number, in-use status, and serial number
            print(f"port = {port}   {inuse}  ({unique_id // 1000000}-{unique_id % 1000000})")
            devinfolist = {
                        'index': idx,
                        'Type': 'Cheetah',
                        'ID': unique_ids,
                        'port': port,
                        'inuse': inuse
                        }
            devices[f'Dev{idx}'] = devinfolist

        return devices

    def open_channel(self, device: dict):

        self._handle = cheetah_py.ch_open(device["port"])
        if self._handle <= 0:
            raise IOError(f'Error openning channel {device["index"]}:'
                          f'{cheetah_py.ch_status_string(cheetah_py.CH_UNABLE_TO_OPEN)}')

        self._device = device
        print(f'Successfully opened device channel {self._device["index"]}\
            with handle {self._handle}')

    def init_channel(self,
                     clock_rate: int = 100000,
                     latency_timer: int = 255,
                     mode: spi_config.SpiMode = spi_config.SpiMode.MODE_0,
                     cs_polarity: spi_config.SpiCSPol = spi_config.SpiCSPol.ACTIVE_LOW):

        cpol, cpha = spi_config.spi_mode_2_cpol_cpha(mode)
        cheetah_py.ch_spi_configure(self._handle, (cpol.value >> 1),
                                    cpha.value & 1, 0, not cs_polarity.value)
        print("SPI configuration set to mode %d," % mode, end=' ')
        # Set the bitrate.
        bitrate = cheetah_py.ch_spi_bitrate(self._handle, clock_rate // 1000)
        print("Bitrate set to %d kHz" % bitrate)

        sys.stdout.flush()

        # Power the target using the Cheetah adapter's power supply.
        cheetah_py.ch_target_power(self._handle, cheetah_py.CH_TARGET_POWER_ON)
        cheetah_py.ch_spi_queue_clear(self._handle)
        cheetah_py.ch_spi_queue_oe(self._handle, 1)
        cheetah_py.ch_spi_batch_shift(self._handle, 1)
        if self._logger:
            self._logger.log_str('SPI initialized')

    def close_channel(self):
        cheetah_py.ch_spi_queue_clear(self._handle)
        cheetah_py.ch_spi_queue_oe(self._handle, 0)
        cheetah_py.ch_spi_batch_shift(self._handle, 1)
        cheetah_py.ch_close(self._handle)
        if self._logger:
            self._logger.log_str('Closing SPI')

    def write(self, write_data, cs_enable=True, cs_disable=True) -> int:

        cheetah_py.ch_spi_queue_clear(self._handle)

        cheetah_py.ch_spi_queue_ss(self._handle, cs_enable)
        cheetah_py.ch_spi_queue_array(self._handle, array('B', write_data))
        cheetah_py.ch_spi_queue_ss(self._handle, not cs_disable)

        batch = cheetah_py.ch_spi_batch_length(self._handle)
        self._status_code, read_data = cheetah_py.ch_spi_batch_shift(self._handle, batch)

        if self._logger:
            wr = ''.join([format(a, '02x') for a in array('B', write_data)])
            rd = ''.join([format(a, '02x') for a in read_data])
            self._logger.log(len(write_data), wr, rd)

        return batch

    def read(self, size: int, cs_enable=True, cs_disable=True) -> list:

        cheetah_py.ch_spi_queue_clear(self._handle)

        cheetah_py.ch_spi_queue_ss(self._handle, cs_enable)
        dummy = array('B', [0 for i in range(size)])
        cheetah_py.ch_spi_queue_array(self._handle, dummy)
        cheetah_py.ch_spi_queue_ss(self._handle, not cs_disable)

        batch = cheetah_py.ch_spi_batch_length(self._handle)
        _, in_buffer = cheetah_py.ch_spi_batch_shift(self._handle, batch)

        if self._logger:
            wr = '00'*size
            rd = ''.join([format(a, '02x') for a in in_buffer])
            self._logger.log(size, wr, rd)

        return in_buffer.tolist()

    def get_status_code(self) -> str:
        return cheetah_py.ch_status_string(self._status_code)

    def delay_us(self, delay: int):
        cheetah_py.ch_spi_queue_clear(self._handle)
        cheetah_py.ch_spi_queue_delay_ns(self._handle, delay * 1000)
        batch = cheetah_py.ch_spi_batch_length(self._handle)
        cheetah_py.ch_spi_batch_shift(self._handle, batch)
