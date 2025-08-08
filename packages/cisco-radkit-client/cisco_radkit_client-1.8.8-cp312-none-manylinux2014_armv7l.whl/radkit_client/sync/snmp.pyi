from .from_async import SyncDictWrapper, SyncWrapper
from _typeshed import Incomplete
from radkit_client.async_.snmp import AsyncSNMPQuery, AsyncSNMPQuerySet, AsyncSNMPResult, AsyncSNMP_API, AsyncSingleDeviceSNMPResult, AsyncSingleDeviceSNMP_API, SNMPNetworkErrorCode as SNMPNetworkErrorCode, SNMPQueryStatistics as SNMPQueryStatistics, SNMPResponseErrorCode as SNMPResponseErrorCode, SNMPResultStatus as SNMPResultStatus, SNMPRow as SNMPRow, SNMPTable as SNMPTable, SNMPTableDeviceView as SNMPTableDeviceView, SNMPVarBindErrorCode as SNMPVarBindErrorCode, SNMP_APIError as SNMP_APIError, SingleDeviceSNMPTable as SingleDeviceSNMPTable
from typing_extensions import Self

__all__ = ['SingleDeviceSNMP_API', 'SNMP_API', 'SNMPTable', 'SingleDeviceSNMPTable', 'SNMPRow', 'SNMPQuerySet', 'SNMPQuery', 'SNMPQueryStatistics', 'SingleDeviceSNMPResult', 'SNMPResult', 'SNMPTableDeviceView', 'SNMP_APIError', 'SNMPResultStatus', 'SNMPNetworkErrorCode', 'SNMPResponseErrorCode', 'SNMPVarBindErrorCode']

class SNMPQuery(SyncWrapper[AsyncSNMPQuery]):
    device_name: Incomplete
    device: Incomplete
    description: Incomplete
    result_count: Incomplete
    done: Incomplete
    request_count: Incomplete
    response_count: Incomplete
    response_time: Incomplete
    dropped_packets: Incomplete
    ping_time: Incomplete
    failed_count: Incomplete
    status: Incomplete
    total_row_count: Incomplete
    error_messages: Incomplete
    short_error_message: Incomplete
    raw_response: Incomplete

class SNMPQuerySet(SyncDictWrapper[AsyncSNMPQuerySet, int, AsyncSNMPQuery, SNMPQuery]):
    stats: Incomplete

class SNMPResult(SyncWrapper[AsyncSNMPResult]):
    aggregate: Incomplete
    result: Incomplete
    queries: Incomplete
    resume_fetch: Incomplete
    pause_fetch: Incomplete
    def wait(self, timeout: float | None = None) -> Self: ...

class SingleDeviceSNMPResult(SyncWrapper[AsyncSingleDeviceSNMPResult]):
    result: Incomplete
    queries: Incomplete
    resume_fetch: Incomplete
    pause_fetch: Incomplete
    def wait(self, timeout: float | None = None) -> Self: ...
    device_name: Incomplete
    device: Incomplete

class SNMP_API(SyncWrapper[AsyncSNMP_API]):
    get: Incomplete
    walk: Incomplete
    get_next: Incomplete
    get_bulk: Incomplete

class SingleDeviceSNMP_API(SyncWrapper[AsyncSingleDeviceSNMP_API]):
    get: Incomplete
    walk: Incomplete
    get_next: Incomplete
    get_bulk: Incomplete
    device_name: Incomplete
    device: Incomplete
