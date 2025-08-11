
from dtiot_d2c.dmo.api_client import ApiClient, ApiClients, ApiToken
from dtiot_d2c.dmo.consts import *
from dtiot_d2c.dmo.dmo import (add_resource, delete_resource, get_resources,
                               update_resource, update_resource_labels)
from dtiot_d2c.dmo.dmoCLI import _CFG as CLICFG
from dtiot_d2c.dmo.onem2m_utils import (convert_dict_to_onem2m_labels,
                                        convert_onem2m_labels_to_dict,
                                        convert_onem2m_timestamp_to_datetime,
                                        select_from_response_body)


class TimeoutError(Exception):
    def __init__(self, message):
        super().__init__(message)
        