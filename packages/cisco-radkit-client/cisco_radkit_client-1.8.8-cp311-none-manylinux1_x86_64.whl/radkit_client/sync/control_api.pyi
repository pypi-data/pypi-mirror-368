from radkit_client.sync.device import Device
from radkit_service.control_api import ControlAPI

__all__ = ['create_control_api']

def create_control_api(device: Device) -> ControlAPI: ...
