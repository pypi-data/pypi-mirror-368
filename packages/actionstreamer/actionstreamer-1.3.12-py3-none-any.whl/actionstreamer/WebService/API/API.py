import datetime
import json
from json import JSONEncoder

import actionstreamer.CommonFunctions
from actionstreamer.Config import WebServiceConfig

class PatchOperation:

    def __init__(self, field_name: str, value):
        self.fieldName = field_name
        self.value = value
        
class WebServiceResult:

    def __init__(self, code: int, description: str, http_response_code: int, http_response_string: str, json_data: str):
        self.code = code
        self.description = description
        self.http_response_code = http_response_code
        self.http_response_string = http_response_string
        self.json_data = json_data

class DateTimeEncoder(JSONEncoder):

    # Override the default method
    def default(self, obj) -> str | None:
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def register_agent(ws_config: WebServiceConfig, device_serial: str, agent_type: str, agent_version: str, agent_index: int, process_id: int) -> tuple[int, str]:

    try:        
        jsonPostData = {"deviceName":device_serial, "agentType":agent_type, "agentVersion":agent_version, "agentIndex":agent_index, "processID":process_id}

        method = "POST"
        path = 'v1/agent'
        url = ws_config.base_url + path
        headers = {"Content-Type": "application/json"}
        parameters = ''
        body = json.dumps(jsonPostData)
        
        response_code, response_string = actionstreamer.CommonFunctions.send_signed_request(ws_config, method, url, path, headers, parameters, body)

    except Exception as ex:
        
        filename, line_number = actionstreamer.CommonFunctions.get_exception_info()
        if filename is not None and line_number is not None:
            print(f"Exception occurred at line {line_number} in {filename}")
        print(ex)

        response_code = -1
        response_string = "Exception in RegisterAgent"

    return response_code, response_string


def device_ready(ws_config: WebServiceConfig, device_serial: str, agent_type: str, agent_version: str, agent_index: int, process_id: int) -> tuple[int, str]:

    try:        
        jsonPostData = {"deviceName":device_serial, "agentType":agent_type, "agentVersion":agent_version, "agentIndex":agent_index, "processID":process_id, "deviceSerial":device_serial}

        method = "POST"
        path = 'v1/device/ready'
        url = ws_config.base_url + path
        headers = {"Content-Type": "application/json"}
        parameters = ''
        body = json.dumps(jsonPostData)
        
        response_code, response_string = actionstreamer.CommonFunctions.send_signed_request(ws_config, method, url, path, headers, parameters, body)

    except Exception as ex:
        
        filename, line_number = actionstreamer.CommonFunctions.get_exception_info()
        if filename is not None and line_number is not None:
            print(f"Exception occurred at line {line_number} in {filename}")
        print(ex)

        response_code = -1
        response_string = "Exception in RegisterAgent"

    return response_code, response_string


def get_device(ws_config: actionstreamer.Config.WebServiceConfig, device_name: str) -> WebServiceResult:

    ws_result = WebServiceResult(0, '', '', '', None)

    try:
        json_post_data = {"deviceName":device_name}

        method = "POST"
        path = 'v1/device/name'
        url = ws_config.base_url + path
        headers = {"Content-Type": "application/json"}
        parameters = ''
        
        json_post_data = {
            "deviceName": device_name
        }

        body = json.dumps(json_post_data)

        response_code, response_string = actionstreamer.CommonFunctions.send_signed_request(ws_config, method, url, path, headers, parameters, body)

        ws_result.http_response_code = response_code
        ws_result.http_response_string = response_string
        ws_result.json_data = json.loads(response_string)

    except Exception as ex:
        
        ws_result.code = -1
        filename, line_number = actionstreamer.CommonFunctions.get_exception_info()
        if filename is not None and line_number is not None:
            print(f"Exception occurred in get_device at line {line_number} in {filename}")
        print(ex)
        ws_result.description = str(ex)

    return ws_result


def get_device_by_id(ws_config: actionstreamer.Config.WebServiceConfig, device_id: int) -> WebServiceResult:

    ws_result = WebServiceResult(0, '', '', '', None)

    try:
        json_post_data = {}

        method = "GET"
        path = 'v1/device/' + str(device_id)
        url = ws_config.base_url + path
        headers = {"Content-Type": "application/json"}
        parameters = ''

        response_code, response_string = actionstreamer.CommonFunctions.send_signed_request(ws_config, method, url, path, headers, parameters, '')

        ws_result.http_response_code = response_code
        ws_result.http_response_string = response_string
        ws_result.json_data = json.loads(response_string)

    except Exception as ex:
        
        ws_result.code = -1
        filename, line_number = actionstreamer.CommonFunctions.get_exception_info()
        if filename is not None and line_number is not None:
            print(f"Exception occurred in get_device at line {line_number} in {filename}")
        print(ex)
        ws_result.description = str(ex)

    return ws_result