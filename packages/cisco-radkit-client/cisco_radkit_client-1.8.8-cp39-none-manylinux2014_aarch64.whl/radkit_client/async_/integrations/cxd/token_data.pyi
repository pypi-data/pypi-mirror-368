from pydantic import BaseModel

__all__ = ['CXDTokenData', 'CXDProtocolData']

class CXDProtocolData(BaseModel):
    path: str
    port: int
    hostname: str | None

class CXDTokenData(BaseModel):
    token: str
    expires: int
    hostname: str | None
    ftp: CXDProtocolData
    ftps: CXDProtocolData
    https: CXDProtocolData
    scp: CXDProtocolData
    sftp: CXDProtocolData
    @property
    def expired(self) -> bool: ...
