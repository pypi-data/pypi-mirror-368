from .exec import ExecError, ExecResponse_ByCommand_ToSingle, ExecResponse_ByDevice_ByCommand, ExecResponse_ByDevice_ToSingle, ExecStatus as ExecStatus, SingleExecResponse
from typing_extensions import TypeAlias

__all__ = ['ExecCommandsResult', 'ExecSingleCommandResult', 'DeviceToCommandToCommandOutputDict', 'DeviceToSingleCommandOutputDict', 'ExecStatus', 'ExecFailedError']

DeviceToCommandToCommandOutputDict: TypeAlias = ExecResponse_ByDevice_ByCommand
ExecCommandsResult: TypeAlias = ExecResponse_ByCommand_ToSingle
DeviceToSingleCommandOutputDict: TypeAlias = ExecResponse_ByDevice_ToSingle
ExecSingleCommandResult: TypeAlias = SingleExecResponse
ExecFailedError: TypeAlias = ExecError
MultipleExecResultsStatus: TypeAlias = ExecStatus
ExecResultStatus: TypeAlias = ExecStatus
