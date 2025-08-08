from _typeshed import Incomplete
from datetime import datetime
from pydantic import BaseModel
from radkit_common.support_package import BasicSupportPackage

__all__ = ['create_support_package', 'ClientSupportPackage']

class ClientSupportPackage(BaseModel):
    __pt_repr__: Incomplete
    model_config: Incomplete
    basic_support_package: BasicSupportPackage
    client_started_at: datetime
    def write_to_file(self, path: str, indent: int = 2, by_alias: bool = False) -> None: ...
    def to_json(self, indent: int = 2, by_alias: bool = False) -> str: ...

async def create_support_package() -> ClientSupportPackage: ...
