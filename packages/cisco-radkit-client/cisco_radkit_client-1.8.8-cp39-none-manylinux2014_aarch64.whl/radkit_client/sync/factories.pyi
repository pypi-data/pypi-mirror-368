from .client import Client
from .device import Device, DeviceDict
from .from_async import Portal
from .service import Service
from radkit_client.async_.client import AsyncClient
from radkit_client.async_.device import AsyncDevice, AsyncDeviceDict
from radkit_client.async_.service import AsyncService

__all__ = ['create_device', 'create_device_dict', 'create_service', 'create_client']

def create_device(async_device: AsyncDevice, portal: Portal) -> Device: ...
def create_device_dict(async_device_dict: AsyncDeviceDict, portal: Portal) -> DeviceDict: ...
def create_service(async_service: AsyncService, portal: Portal) -> Service: ...
def create_client(async_device: AsyncClient, portal: Portal) -> Client: ...
