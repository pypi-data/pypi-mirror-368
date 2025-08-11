#! python

from collections import UserDict
from enum import IntEnum


class DWT_PLL_CH_TYPE(IntEnum):
    DWT_CH5 = 5,
    DWT_CH9 = 9


class DWT_PLEN(IntEnum):
    DWT_PLEN_4096 = 0x1ff,
    DWT_PLEN_2048 = 0xff,
    DWT_PLEN_1536 = 0xbf,
    DWT_PLEN_1024 = 0x7f,
    DWT_PLEN_512 = 0x3f,
    DWT_PLEN_256 = 0x1f,
    DWT_PLEN_128 = 0x0f,
    DWT_PLEN_72 = 0x08,
    DWT_PLEN_64 = 0x07,
    DWT_PLEN_32 = 0x03,


class DWT_PAC_SIZE(IntEnum):
    DWT_PAC8 = 0,
    DWT_PAC16 = 1,
    DWT_PAC32 = 2,
    DWT_PAC4 = 3,


class DWT_SFD_TYPE(IntEnum):
    DWT_SFD_IEEE_4A = 0,
    DWT_SFD_IEEE_4Z_4 = 1,
    DWT_SFD_IEEE_4Z_8 = 2,
    DWT_SFD_IEEE_4Z_16 = 3,
    DWT_SFD_IEEE_4Z_32 = 4,
    DWT_SFD_DW_8 = 6,
    DWT_SFD_DW_16 = 7,


class DWT_UWB_BIT_RATE(IntEnum):
    DWT_BR_850K = 0,
    DWT_BR_6M8 = 1,
    DWT_BR_NODATA = 2,
    DWT_BR_6M8_128 = 4,
    DWT_BR_27M_256 = 5,
    DWT_BR_27M_256_K7 = 0xd,
    DWT_BR_54M_256 = 0xe,
    DWT_BR_108M_256 = 0xf,


class DWT_PHR_MODE(IntEnum):
    DWT_PHRMODE_STD = 0x0,
    DWT_PHRMODE_EXT = 0x1,


class DWT_PHR_RATE(IntEnum):
    DWT_PHRRATE_STD = 0x0,
    DWT_PHRRATE_DTA = 0x1,


class DWT_STS_MODE(IntEnum):
    DWT_STS_MODE_OFF = 0x0,
    DWT_STS_MODE_1 = 0x1,
    DWT_STS_MODE_2 = 0x2,
    DWT_STS_MODE_ND = 0x3,
    DWT_STS_MODE_SDC = 0x4,


class DWT_STS_LENGTHS(IntEnum):
    DWT_STS_LEN_16 = 1,
    DWT_STS_LEN_32 = 3,
    DWT_STS_LEN_64 = 7,
    DWT_STS_LEN_128 = 15,
    DWT_STS_LEN_256 = 31,
    DWT_STS_LEN_512 = 63,
    DWT_STS_LEN_1024 = 127,
    DWT_STS_LEN_2048 = 255,


class DWT_PDOA_MODE(IntEnum):
    DWT_PDOA_M0 = 0x0,
    DWT_PDOA_M3 = 0x3,


class Radio_config(UserDict):
    def __setitem__(self, item, value):
        if(type(value) == str):
            v = int(value, 0)
        else:
            v = value
        if item == "chan":
            val = DWT_PLL_CH_TYPE(v).value
        elif item == "txPreambLength":
            val = DWT_PLEN(v).value
        elif item == "rxPAC":
            val = DWT_PAC_SIZE(v).value
        elif item == "txCode":
            val = v
        elif item == "rxCode":
            val = v
        elif item == "sfdType":
            val = DWT_SFD_TYPE(v).value
        elif item == "dataRate":
            val = DWT_UWB_BIT_RATE(v).value
        elif item == "phrMode":
            val = DWT_PHR_MODE(v).value
        elif item == "phrRate":
            val = DWT_PHR_RATE(v).value
        elif item == "sfdTO":
            val = v
        elif item == "stsMode":
            val = DWT_STS_MODE(v).value
        elif item == "stsLength":
            val = DWT_STS_LENGTHS(v).value
        elif item == "pdoaMode":
            val = DWT_PDOA_MODE(v).value
        elif item == "PGdly":
            val = v
        elif item == "power":
            val = v
        elif item == "PGcount":
            val = v
        else:
            raise KeyError(f"Item: '{item}' is not a valid field for Radio Config")
        super().__setitem__(item, val)
