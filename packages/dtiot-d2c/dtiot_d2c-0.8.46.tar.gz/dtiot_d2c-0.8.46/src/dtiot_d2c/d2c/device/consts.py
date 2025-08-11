from enum import Enum

from pydantic import BaseModel

import dtiot_d2c.d2c.consts as d2c_consts


class DEVICE_PROFILES:
    SCS_LWM2M:str = "SCS-LwM2M"
    
class MessageStore(BaseModel):
    rn:str       # OneM2M name
    label:str    # Label to be used in logging

VALID_NAME_CHARS = r'^[0-9A-Za-z_-]+$'
    
INBOUND_DOWNLINK_MESSAGE_STORE  = MessageStore(rn="outgoing-msg", label="Downlink Inbound")
OUTBOUND_DOWNLINK_MESSAGE_STORE = MessageStore(rn="sent-msg", label="Downlink Outbound")
INBOUND_UPLINK_MESSAGE_STORE    = MessageStore(rn="received-msg", label="Uplink Inbound")
OUTBOUND_UPLINK_MESSAGE_STORE   = MessageStore(rn="sent-received-msg", label="Uplink Outbound")

UPLINK_PROPERTY_PREFIX = "UplinkProperty_"
DEVICE_PROPERTY_PREFIX = "DeviceProperty_"
DEVICE_SYSTEM_LABELS = ["profile", "ICCID", d2c_consts.D2C_SYSTEM_VERSION_LABEL]
DEVICE_INFO_RN = "device-info"
DEVICE_INFO_MGD = 1007

# Sleep seconds it is waited after the device credentials have been deleted to create new ones
DELETE_CREDENTIALS_SLEEP_SECS = 1


