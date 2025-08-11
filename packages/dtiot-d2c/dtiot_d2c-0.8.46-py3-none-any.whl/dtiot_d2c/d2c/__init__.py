

import dtiot_d2c.d2c.version_info as version_info
from dtiot_d2c.d2c.application import Application
from dtiot_d2c.d2c.consts import *
from dtiot_d2c.d2c.device import Device, Message
from dtiot_d2c.d2c.device_group import DeviceGroup
from dtiot_d2c.d2c.onem2m_base import OneM2MBase


def get_version_info()->dict:
    """Returns version if of d2c cli

    Returns:
        dict: {"build_version":"<build version>", "build_date":"<build date>"}
    """

    return {
        "build_version":version_info.build_version,
        "build_date":version_info.build_date
    }