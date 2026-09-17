# Copyright (c) 2026 Dobot
# Licensed under the MIT License

"""IO related module - Digital IO, Analog IO, End-effector IO control"""

from typing import List, Union
from ..core.connection import DobotConnection


class IO:
    """IO module - Handles all IO-related commands"""

    def __init__(self, connection: DobotConnection):
        self.connection = connection

    def _send_cmd(self, command: str) -> str:
        """Send command and receive response"""
        return self.connection.send_receive_text(command)

    # ==================== Digital Output Ports ====================

    def DO(self, index: int, status: int, time: float = None) -> str:
        """
        Set digital output port status (queued command)
        Args:
            index: DO port index (1-based)
            status: Status (0=Off, 1=On)
            time: Output duration in seconds. Valid when status=1, automatically changes to 0 after the time elapses.

        Returns:
            str: ErrorID,{ResultID},DO(index,status,time);
        """
        if status not in [0, 1]:
            raise ValueError("DO status must be 0 or 1")
        if time is not None:
            return self._send_cmd(f"DO({index},{status},{time:.3f})")
        return self._send_cmd(f"DO({index},{status})")

    def DOInstant(self, index: int, status: int) -> str:
        """
        Set digital output port status (immediate command)
        Args:
            index: DO port index (1-based)
            status: Status (0=Off, 1=On)

        Returns:
            str: ErrorID,{},DOInstant(index,status);
        """
        if status not in [0, 1]:
            raise ValueError("DO status must be 0 or 1")
        return self._send_cmd(f"DOInstant({index},{status})")

    def GetDO(self, index: int) -> str:
        """
        Get digital output port status (immediate command)
        Args:
            index: DO port index (1-based)

        Returns:
            str: ErrorID,{status},GetDO(index);
        """
        return self._send_cmd(f"GetDO({index})")

    def DOGroup(self, *index_value_pairs) -> str:
        """
        Set multiple digital output port status (queued command)
        Args:
            *index_value_pairs: Paired parameters of port index and status, e.g. DOGroup(4,1,6,0,2,1,7,0)

        Returns:
            str: ErrorID,{ResultID},DOGroup(index1,value1,index2,value2,...);
        """
        if len(index_value_pairs) % 2 != 0:
            raise ValueError("DOGroup parameters must be even in number (index and value paired)")
        params = []
        for i in range(0, len(index_value_pairs), 2):
            index = index_value_pairs[i]
            value = index_value_pairs[i + 1]
            if not isinstance(index, int):
                raise ValueError("DOGroup index must be of int type")
            if value not in [0, 1]:
                raise ValueError("DOGroup value must be 0 or 1")
            params.append(str(index))
            params.append(str(value))
        return self._send_cmd(f"DOGroup({','.join(params)})")

    def DOGroupDEC(self, indices: Union[List[int], str], value: int) -> str:
        """
        Set multiple digital output port status by decimal value (queued command)
        Args:
            indices: Port index list, e.g. [1,2,3,4,5] or string "{1,2,3,4,5}"
            value: Decimal value
        Returns:
            str: ErrorID,{ResultID},DOGroupDEC({index1,index2,...,indexN},value);
        """
        if isinstance(indices, list):
            indices_str = "{" + ",".join(str(i) for i in indices) + "}"
        else:
            indices_str = indices
        return self._send_cmd(f"DOGroupDEC({indices_str},{value})")

    def GetDOGroup(self, *indices) -> str:
        """
        Get multiple digital output port status (immediate command)
        Args:
            *indices: DO port numbers to read, e.g. GetDOGroup(1,2)

        Returns:
            str: ErrorID,{status1,status2,...},GetDOGroup(index1,index2,...);
        """
        params = ",".join(str(i) for i in indices)
        return self._send_cmd(f"GetDOGroup({params})")

    def GetDOGroupDEC(self, indices: Union[List[int], str]) -> str:
        """
        Get current status of multiple digital output ports, returns decimal value (immediate command)

        Args:
            indices: Port index list, e.g. [1,2,3] or string "{1,2,3}"

        Returns:
            str: ErrorID,{value},GetDOGroupDEC({index1,...,indexN});
        """
        if isinstance(indices, list):
            indices_str = "{" + ",".join(str(i) for i in indices) + "}"
        else:
            indices_str = indices
        return self._send_cmd(f"GetDOGroupDEC({indices_str})")

    # ==================== Digital Input Ports ====================

    def DI(self, index: int) -> str:
        """
        Get DI port status (immediate command)
        Args:
            index: DI port index (1-based)

        Returns:
            str: ErrorID,{status},DI(index);
        """
        return self._send_cmd(f"DI({index})")

    def DIGroup(self, *indices) -> str:
        """
        Get status of multiple DI ports (immediate command)
        Args:
            *indices: DI port numbers to read, e.g. DIGroup(4,6,2,7)

        Returns:
            str: ErrorID,{status1,status2,...},DIGroup(index1,index2,...);
        """
        params = ",".join(str(i) for i in indices)
        return self._send_cmd(f"DIGroup({params})")

    def DIGroupDEC(self, indices: Union[List[int], str]) -> str:
        """
        Get status of multiple DI ports, returns decimal value (queued command)

        Args:
            indices: Port index list, e.g. [1,2] or string "{1,2}"

        Returns:
            str: ErrorID,{value},DIGroupDEC({index1,index2,...,indexN});
        """
        if isinstance(indices, list):
            indices_str = "{" + ",".join(str(i) for i in indices) + "}"
        else:
            indices_str = indices
        return self._send_cmd(f"DIGroupDEC({indices_str})")

    # ==================== Analog Output Ports ====================

    def AO(self, index: int, value: float) -> str:
        """
        Set analog output port value (queued command)
        Args:
            index: AO port index (1-based)
            value: Analog value (0.0-10.0V)

        Returns:
            str: ErrorID,{ResultID},AO(index,value);
        """
        return self._send_cmd(f"AO({index},{value:.2f})")

    def AOInstant(self, index: int, value: float) -> str:
        """
        Set analog output port value (immediate command)
        Args:
            index: AO port index (1-based)
            value: Analog value (0.0-10.0V)

        Returns:
            str: ErrorID,{},AOInstant(index,value);
        """
        return self._send_cmd(f"AOInstant({index},{value:.2f})")

    def GetAO(self, index: int) -> str:
        """
        Get analog output port value (immediate command)
        Args:
            index: AO port index (1-based)

        Returns:
            str: ErrorID,{value},GetAO(index);
        """
        return self._send_cmd(f"GetAO({index})")

    # ==================== Analog Input Ports ====================

    def AI(self, index: int) -> str:
        """
        Get AI port value (immediate command)
        Args:
            index: AI port index (1-based)

        Returns:
            str: ErrorID,{value},AI(index);
        """
        return self._send_cmd(f"AI({index})")

    # ==================== End-effector Digital Output Ports ====================

    def ToolDO(self, index: int, status: int) -> str:
        """
        Set end-effector digital output port status (queued command)
        Args:
            index: End-effector DO port index (0-1)
            status: Status (0=Off, 1=On)

        Returns:
            str: ErrorID,{ResultID},ToolDO(index,status);
        """
        if status not in [0, 1]:
            raise ValueError("DO status must be 0 or 1")
        return self._send_cmd(f"ToolDO({index},{status})")

    def ToolDOInstant(self, index: int, status: int) -> str:
        """
        Set end-effector digital output port status (immediate command)
        Args:
            index: End-effector DO port index (0-1)
            status: Status (0=Off, 1=On)

        Returns:
            str: ErrorID,{},ToolDOInstant(index,status);
        """
        if status not in [0, 1]:
            raise ValueError("DO status must be 0 or 1")
        return self._send_cmd(f"ToolDOInstant({index},{status})")

    def GetToolDO(self, index: int) -> str:
        """
        Get end-effector digital output port status (immediate command)
        Args:
            index: End-effector DO port index (0-1)

        Returns:
            str: ErrorID,{status},GetToolDO(index);
        """
        return self._send_cmd(f"GetToolDO({index})")

    # ==================== End-effector Digital Input Ports ====================

    def ToolDI(self, index: int) -> str:
        """
        Get end-effector DI port status (immediate command)
        Args:
            index: End-effector DI port index
        Returns:
            str: ErrorID,{status},ToolDI(index);
        """
        return self._send_cmd(f"ToolDI({index})")

    # ==================== End-effector Analog Input Ports ====================

    def ToolAI(self, index: int) -> str:
        """
        Get end-effector AI port value (immediate command)
        Args:
            index: End-effector AI port index
        Returns:
            str: ErrorID,{value},ToolAI(index);
        """
        return self._send_cmd(f"ToolAI({index})")

    # ==================== End-effector Tool Settings ====================

    def SetTool485(self, baud: int, parity: str = "N", stopbit: int = 1, identify: int = None) -> str:
        """
        Set end-effector 485 communication format (immediate command)

        Args:
            baud: Baud rate
            parity: Parity bit ("O"=Odd, "E"=Even, "N"=None) default "N"
            stopbit: Stop bit default 1
            identify: Identification parameter (optional)
        Returns:
            str: ErrorID,{},SetTool485(baud,parity,stopbit[,identify]);
        """
        if identify is not None:
            return self._send_cmd(f'SetTool485({baud},"{parity}",{stopbit},{identify})')
        return self._send_cmd(f'SetTool485({baud},"{parity}",{stopbit})')

    def SetToolPower(self, status: int) -> str:
        """
        Set end-effector tool power status (immediate command)
        Args:
            status: Power status (0-Off, 1-On)

        Returns:
            str: ErrorID,{},SetToolPower(status);
        """
        if status not in [0, 1]:
            raise ValueError("Status must be 0 or 1")
        return self._send_cmd(f"SetToolPower({status})")

    def SetToolMode(self, mode: int, type: int = None, identify: int = None) -> str:
        """
        Set end-effector multiplexing terminal mode (immediate command)
        Args:
            mode: Mode value
            type: Type value (optional)
            identify: Identification parameter (optional)
        Returns:
            str: ErrorID,{},SetToolMode(mode[,type[,identify]]);
        """
        params = [str(mode)]
        if type is not None:
            params.append(str(type))
            if identify is not None:
                params.append(str(identify))
        return self._send_cmd(f"SetToolMode({','.join(params)})")