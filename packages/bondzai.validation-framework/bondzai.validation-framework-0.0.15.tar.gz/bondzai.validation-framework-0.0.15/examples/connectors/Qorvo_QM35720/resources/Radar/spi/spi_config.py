#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""spi_config.py: A python SPI configuration data

"""

from enum import IntEnum, Enum

# polarity, phase, bitorder, ss_polarity


class SpiCPOL(IntEnum):
    LOW = 0
    HIGH = 2


class SpiCPHA(IntEnum):
    RISING_FALLING = 0
    FALLING_RISING = 1


class SpiMode(IntEnum):
    MODE_0 = 0
    MODE_1 = 1
    MODE_2 = 2
    MODE_3 = 3


def spi_mode_2_cpol_cpha(mode: SpiMode) -> tuple:
    if mode == SpiMode.MODE_0:
        return (SpiCPOL.LOW, SpiCPHA.RISING_FALLING)
    if mode == SpiMode.MODE_1:
        return (SpiCPOL.LOW, SpiCPHA.FALLING_RISING)
    if mode == SpiMode.MODE_2:
        return (SpiCPOL.HIGH, SpiCPHA.RISING_FALLING)
    if mode == SpiMode.MODE_3:
        return (SpiCPOL.HIGH, SpiCPHA.FALLING_RISING)
    return (SpiCPOL.LOW, SpiCPHA.RISING_FALLING)


def spi_cpol_cpha_2_mode(polarity: SpiCPOL, phase: SpiCPHA) -> SpiMode:
    return SpiMode(polarity + phase)


class SpiCSPol(Enum):
    ACTIVE_HIGH = 0
    ACTIVE_LOW = 1
