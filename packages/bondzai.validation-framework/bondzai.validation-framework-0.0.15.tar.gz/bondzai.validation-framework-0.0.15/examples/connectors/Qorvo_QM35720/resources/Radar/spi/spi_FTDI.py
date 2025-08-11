#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""spi_MPSSE.py: A python wrapper for the FTDI-provided libMPSSE DLL (SPI only)

Widely inspired from the https://github.com/jmbattle/pyMPSSE project from
Jason M. Battle with a MIT License.
"""

import ctypes
import os
import sys
from array import array

from . import spi_config

# Status Codes
STATUS_CODES = {0: 'FT_OK',
                1: 'FT_INVALID_HANDLE',
                2: 'FT_DEVICE_NOT_FOUND',
                3: 'FT_DEVICE_NOT_OPENED',
                4: 'FT_IO_ERROR',
                5: 'FT_INSUFFICIENT_RESOURCES',
                6: 'FT_INVALID_PARAMETER',
                7: 'FT_INVALID_BAUD_RATE',
                8: 'FT_DEVICE_NOT_OPENED_FOR_ERASE',
                9: 'FT_DEVICE_NOT_OPENED_FOR_WRITE',
                10: 'FT_FAILED_TO_WRITE_DEVICE',
                11: 'FT_EEPROM_READ_FAILED',
                12: 'FT_EEPROM_WRITE_FAILED',
                13: 'FT_EEPROM_ERASE_FAILED',
                14: 'FT_EEPROM_NOT_PRESENT',
                15: 'FT_EEPROM_NOT_PROGRAMMED',
                16: 'FT_INVALID_ARGS',
                17: 'FT_NOT_SUPPORTED',
                18: 'FT_OTHER_ERROR',
                19: 'FT_DEVICE_LIST_NOT_READY'}

# Device Types
DEVICE_TYPES = {0: 'FT_DEVICE_BM',
                1: 'FT_DEVICE_BM',
                2: 'FT_DEVICE_100AX',
                3: 'FT_DEVICE_UNKNOWN',
                4: 'FT_DEVICE_2232C',
                5: 'FT_DEVICE_232R',
                6: 'FT_DEVICE_2232H',
                7: 'FT_DEVICE_4232H',
                8: 'FT_DEVICE_232H',
                9: 'FT_DEVICE_X_SERIES'}


class FT_DEVICE_LIST_INFO_NODE(ctypes.Structure):
    _fields_ = [
        ('Flags', ctypes.c_ulong),
        ('Type', ctypes.c_ulong),
        ('ID', ctypes.c_ulong),
        ('LocID', ctypes.c_ulong),
        ('SerialNumber', ctypes.c_ubyte*16),
        ('Description', ctypes.c_ubyte*64),
        ('ftHandle', ctypes.c_ulonglong)]


class CHANNEL_CONFIG(ctypes.Structure):
    _fields_ = [
        ('ClockRate', ctypes.c_ulong),
        ('LatencyTimer', ctypes.c_ubyte),
        ('configOptions', ctypes.c_ulong),
        ('Pin', ctypes.c_ulong),
        ('reserved', ctypes.c_ushort)]


class SpiFTDI():
    def __init__(self, logger=None):
        self._status_code = None
        self._device = None
        self._logger = logger

        dll = "libMPSSE"
        extra_dll_dir = os.path.abspath(os.path.dirname(__file__))

        if sys.version_info >= (3, 8):
            os.add_dll_directory(extra_dll_dir)
        else:
            os.environ.setdefault("PATH", "")
            os.environ["PATH"] += os.pathsep + extra_dll_dir

        try:
            self._lib_mpsse = ctypes.WinDLL(dll)
        except OSError:
            print(f'Unable to load {dll}')
            raise
        self._handle = 0

# FTDI_API FT_STATUS SPI_GetNumChannels(uint32 *numChannels);

    def _get_num_channels(self) -> int:
        self._lib_mpsse.SPI_GetNumChannels.argtypes = [ctypes.POINTER(ctypes.c_ulong)]
        self._lib_mpsse.SPI_GetNumChannels.restype = ctypes.c_ulong
        numchannels = ctypes.c_ulong()
        self._status_code = self._lib_mpsse.SPI_GetNumChannels(ctypes.byref(numchannels))
        if self._status_code != 0:
            print(f'Error getting Number of channels: {STATUS_CODES[self._status_code]}')
            return 0

        print(f'Number of Channels: {numchannels.value}')
        return numchannels.value

# FT_STATUS SPI_GetChannelInfo(uint32 index, FT_DEVICE_LIST_INFO_NODE *chanInfo);

    def get_channel_info(self) -> dict:
        numchannels = self._get_num_channels()
        self._lib_mpsse.SPI_GetChannelInfo.argtypes = \
            [ctypes.c_ulong, ctypes.POINTER(FT_DEVICE_LIST_INFO_NODE)]
        self._lib_mpsse.SPI_GetChannelInfo.restype = ctypes.c_ulong

        channel_info = FT_DEVICE_LIST_INFO_NODE()
        devices = {}
        for idx in range(numchannels):
            self._status_code = \
                self._lib_mpsse.SPI_GetChannelInfo(ctypes.c_ulong(idx), ctypes.byref(channel_info))
            if self._status_code != 0:
                print(f'Error getting Channel Info: {STATUS_CODES[self._status_code]}')
            else:
                device_type = DEVICE_TYPES[channel_info.Type]
                # Remove non-ASCII characters
                serial_number = \
                    ''.join(map(chr, channel_info.SerialNumber)).split('\x00', maxsplit=1)[0]
                description = \
                    ''.join(map(chr, channel_info.Description)).split('\x00', maxsplit=1)[0]
                print(f'Flags: {channel_info.Flags}')
                print(f'Type: {device_type}')
                print(f'ID: {channel_info.ID}')
                print(f'LocID: {channel_info.LocID}')
                print(f'SerialNumber: {serial_number}')
                print(f'Description: {description}')
                print(f'Handle: {channel_info.ftHandle}')
                if device_type in ('FT_DEVICE_232H', 'FT_DEVICE_2232H'):
                    devinfolist = {
                        'index': idx,
                        'Flags': channel_info.Flags,
                        'Type': device_type,
                        'ID': channel_info.ID,
                        'LocID': channel_info.LocID,
                        'SerialNumber': serial_number,
                        'Description': description
                        }
                    devices[f'Dev{idx}'] = devinfolist
        return devices

# FT_STATUS SPI_OpenChannel(uint32 index, FT_HANDLE *handle);

    def open_channel(self, device: dict):
        self._lib_mpsse.SPI_OpenChannel.argtypes = \
            [ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulonglong)]
        self._lib_mpsse.SPI_OpenChannel.restype = ctypes.c_ulong
        assert (device['Type'] == 'FT_DEVICE_232H' or device['Type'] == 'FT_DEVICE_2232H')
        if self._handle != 0:
            raise IOError(f'A device is already open with handle {self._handle}')
        self._device = device
        tmp_handle = ctypes.c_ulonglong()
        self._status_code = \
            self._lib_mpsse.SPI_OpenChannel(
                ctypes.c_ulong(device['index']),
                ctypes.byref(tmp_handle))
        self._handle = tmp_handle.value

        if self._status_code != 0:
            raise IOError(f'Error openning channel: {STATUS_CODES[self._status_code]}')

        print(f'Successfully opened device channel {self._device["index"]}\
            with handle {self._handle}')

# FT_STATUS SPI_InitChannel(FT_HANDLE handle, ChannelConfig *config);

    def init_channel(self,
                     clock_rate: int = 100000,
                     latency_timer: int = 255,
                     mode: spi_config.SpiMode = spi_config.SpiMode.MODE_0,
                     cs_polarity: spi_config.SpiCSPol = spi_config.SpiCSPol.ACTIVE_LOW):

        config_options = mode.value + (cs_polarity.value << 5)
        self._lib_mpsse.SPI_InitChannel.argtypes = \
            [ctypes.c_ulonglong, ctypes.POINTER(CHANNEL_CONFIG)]
        self._lib_mpsse.SPI_InitChannel.restype = ctypes.c_ulong
        channel_config = CHANNEL_CONFIG(clock_rate, latency_timer, config_options, 0, 0)
        self._status_code = \
            self._lib_mpsse.SPI_InitChannel(
                ctypes.c_ulonglong(self._handle),
                ctypes.byref(channel_config))
        if self._status_code != 0:
            print(f'error init channel: {STATUS_CODES[self._status_code]}')
        else:
            print(f'Successfully initialized device channel \
                {self._device["index"]} with handle {self._handle}')
            print(f' Clock Rate: {channel_config.ClockRate}')
            print(f'Latency Timer: {channel_config.LatencyTimer}')
            print(f'Options: {channel_config.configOptions}')

# FT_STATUS SPI_CloseChannel(FT_HANDLE handle);

    def close_channel(self):
        self._lib_mpsse.SPI_CloseChannel.argtypes = [ctypes.c_ulonglong]
        self._lib_mpsse.SPI_CloseChannel.restype = ctypes.c_ulong
        self._status_code = self._lib_mpsse.SPI_CloseChannel(ctypes.c_ulonglong(self._handle))
        if self._status_code != 0:
            print(f'error closing channel: {STATUS_CODES[self._status_code]}')
        else:
            print(f'Successfully closed device channel {self._device["index"]} \
                with handle {self._handle}')

# FTDI_API FT_STATUS SPI_Write(FT_HANDLE handle, uint8 *buffer,	uint32 sizeToTransfer,
#                              uint32 *sizeTransferred, uint32 transferOptions)

    def write(self, write_data, cs_enable=True, cs_disable=True) -> int:

        self._lib_mpsse.SPI_Write.argtypes = \
            [ctypes.c_ulonglong, ctypes.POINTER(ctypes.c_ubyte),
             ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong), ctypes.c_ulong]
        self._lib_mpsse.SPI_Write.restype = ctypes.c_ulong
        options = 0
        options = options + (2 if cs_enable else 0)
        options = options + (4 if cs_disable else 0)

        out_buffer = (ctypes.c_ubyte*(len(write_data)))(*write_data)
        size_to_transfer = ctypes.c_ulong(len(write_data))
        size_transferred = ctypes.c_ulong()
        transfer_options = ctypes.c_ulong(options)

        self._status_code = self._lib_mpsse.SPI_Write(
            ctypes.c_ulonglong(self._handle),
            out_buffer, size_to_transfer,
            ctypes.byref(size_transferred),
            transfer_options)

        if self._logger:
            wr = ''.join([format(a, '02x') for a in array('B', write_data)])
            # TODO: to get the read data, use SPI_ReadWrite function instead of SPI_Write
            rd = '00'*size_transferred.value
            self._logger.log(size_transferred.value, wr, rd)

        if self._status_code != 0:
            # print(f'{STATUS_CODES[self._status_code]}')
            return 0

        return size_transferred.value

# FTDI_API FT_STATUS SPI_Read(FT_HANDLE handle, uint8 *buffer, uint32 sizeToTransfer,
#                             uint32 *sizeTransferred, uint32 transferOptions)

    def read(self, size: int, cs_enable=True, cs_disable=True) -> list:
        self._lib_mpsse.SPI_Read.argtypes = \
            [ctypes.c_ulonglong, ctypes.POINTER(ctypes.c_ubyte),
             ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong), ctypes.c_ulong]
        self._lib_mpsse.SPI_Read.restype = ctypes.c_ulong
        options = 0
        options = options + (2 if cs_enable else 0)
        options = options + (4 if cs_disable else 0)

        in_buffer = (ctypes.c_ubyte*(size))()
        size_to_transfer = ctypes.c_ulong(size)
        size_transferred = ctypes.c_ulong()
        transfer_options = ctypes.c_ulong(options)

        self._status_code = self._lib_mpsse.SPI_Read(
            ctypes.c_ulonglong(self._handle),
            in_buffer, size_to_transfer,
            ctypes.byref(size_transferred),
            transfer_options)

        if self._logger:
            wr = '00'*size_transferred.value
            rd = ''.join([format(a, '02x') for a in array('B', in_buffer[:])])
            self._logger.log(size_transferred.value, wr, rd)

        if self._status_code != 0:
            # print(f'{STATUS_CODES[self._status_code]}')
            return []

        # print(f'SPI transaction complete size rx {size_transferred.value}')
        return in_buffer[:]

    def get_status_code(self) -> str:
        return STATUS_CODES[self._status_code]

    def delay_us(self, delay: int):
        # No way to delay for us with FTDI.This is not an issue because FTDIs have
        # a huge delay at transaction.
        pass
