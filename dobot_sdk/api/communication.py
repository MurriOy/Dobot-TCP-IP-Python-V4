# Copyright (c) 2026 Dobot
# Licensed under the MIT License

"""Communication module - Modbus and bus register control"""

from typing import List, Union
from ..core.connection import DobotConnection


class Communication:
    """Communication module - Handle Modbus and bus register communication"""

    def __init__(self, connection: DobotConnection):
        self.connection = connection

    def _send_cmd(self, command: str) -> str:
        """Send command and receive response"""
        return self.connection.send_receive_text(command)

    # ==================== Modbus Master Creation ====================

    def ModbusCreate(self, ip: str, port: int, slave_id: int, is_rtu: int = 0) -> str:
        """
        Create Modbus master

        Args:
            ip: Slave IP address
            port: Slave port
            slave_id: Slave ID
            is_rtu: Whether to use RTU mode (0-TCP, 1-RTU), default 0

        Returns:
            str: ErrorID,{index},ModbusCreate(ip,port,slave_id,isRTU);
                 index is the returned master index, used for subsequent Modbus commands
        """
        cmd = f'ModbusCreate("{ip}",{port},{slave_id},{is_rtu})'
        return self._send_cmd(cmd)

    def ModbusRTUCreate(self, slave_id: int, baud: int, 
                          parity: str = "E", data_bit: int = 8, 
                          stop_bit: int = 1) -> str:
        """
        Create Modbus master based on RS485 interface

        Args:
            slave_id: Slave ID
            baud: RS485 interface baud rate
            parity: Parity bit ("O"-odd, "E"-even, "N"-none, default "E")
            data_bit: Data bit length, default 8
            stop_bit: Stop bit length, default 1

        Returns:
            str: ErrorID,{index},ModbusRTUCreate(slave_id,baud,parity,data_bit,stop_bit);
        """
        if parity not in ["O", "E", "N"]:
            raise ValueError("parity must be 'O', 'E', or 'N'")
        
        cmd = f'ModbusRTUCreate({slave_id},{baud},"{parity}",{data_bit},{stop_bit})'
        return self._send_cmd(cmd)

    def ModbusClose(self, index: int) -> str:
        """
        Disconnect from Modbus slave and release master

        Args:
            index: Master index returned when creating the master
        """
        return self._send_cmd(f"ModbusClose({index})")

    # ==================== Contact Registers ====================

    def GetInBits(self, index: int, addr: int, count: int) -> str:
        """
        Read values from Modbus slave contact registers (discrete inputs)

        Args:
            index: Master index returned when creating the master
            addr: Contact register starting address
            count: Number of consecutive contact register values to read, range: [1, 16]

        Returns:
            str: ErrorID,{value1,value2,...,valuen},GetInBits(index,addr,count);
        """
        if not 1 <= count <= 16:
            raise ValueError("count must be in range [1, 16]")
        
        cmd = f"GetInBits({index},{addr},{count})"
        return self._send_cmd(cmd)

    # ==================== Input Registers ====================

    def GetInRegs(self, index: int, addr: int, count: int, val_type: str = "U16") -> str:
        """
        Read values from Modbus slave input registers with specified data type

        Args:
            index: Master index returned when creating the master
            addr: Input register starting address
            count: Number of consecutive input register values to read, range: [1, 4]
            val_type: Data format for reading
                      U16 - 16-bit unsigned integer (2 bytes, occupies 1 register);
                      U32 - 32-bit unsigned integer (4 bytes, occupies 2 registers);
                      F32 - 32-bit single-precision float (4 bytes, occupies 2 registers);
                      F64 - 64-bit double-precision float (8 bytes, occupies 4 registers);
                      Default is U16

        Returns:
            str: ErrorID,{value1,value2,...,valuen},GetInRegs(index,addr,count,valType);
        """
        if not 1 <= count <= 4:
            raise ValueError("count must be in range [1, 4]")
        if val_type not in ["U16", "U32", "F32", "F64"]:
            raise ValueError("val_type must be 'U16', 'U32', 'F32', or 'F64'")
        
        cmd = f'GetInRegs({index},{addr},{count},"{val_type}")'
        return self._send_cmd(cmd)

    # ==================== Coil Registers ====================

    def GetCoils(self, index: int, addr: int, count: int) -> str:
        """
        Read values from Modbus slave coil registers

        Args:
            index: Master index returned when creating the master
            addr: Coil register starting address
            count: Number of consecutive coil register values to read, range: [1, 16]

        Returns:
            str: ErrorID,{value1,value2,...,valuen},GetCoils(index,addr,count);
        """
        if not 1 <= count <= 16:
            raise ValueError("count must be in range [1, 16]")
        
        cmd = f"GetCoils({index},{addr},{count})"
        return self._send_cmd(cmd)

    def SetCoils(self, index: int, addr: int, count: int, val_tab: Union[List[int], str]) -> str:
        """
        Write specified values to coil register addresses

        Args:
            index: Master index returned when creating the master
            addr: Coil register starting address
            count: Number of consecutive coil register values to write, range: [1, 16]
            val_tab: Values to write, count must match the count parameter

        Returns:
            str: ErrorID,{},SetCoils(index,addr,count,valTab);
        """
        if not 1 <= count <= 16:
            raise ValueError("count must be in range [1, 16]")
        
        if isinstance(val_tab, list):
            val_str = "{" + ",".join(str(v) for v in val_tab) + "}"
        else:
            val_str = val_tab
        
        cmd = f"SetCoils({index},{addr},{count},{val_str})"
        return self._send_cmd(cmd)

    def SetSingleCoil(self, index: int, addr: int, value: int) -> str:
        """
        Write to a single coil register (new command in V4.6.6)

        Args:
            index: Master index returned when creating the master
            addr: Coil register address
            value: Value to write, 0 or 1

        Returns:
            str: ErrorID,{},SetSingleCoil(index,addr,value);
        """
        if value not in [0, 1]:
            raise ValueError("value must be 0 or 1")
        
        cmd = f"SetSingleCoil({index},{addr},{value})"
        return self._send_cmd(cmd)

    # ==================== Holding Registers ====================

    def GetHoldRegs(self, index: int, addr: int, count: int, val_type: str = "U16") -> str:
        """
        Read values from Modbus slave holding registers with specified data type

        Args:
            index: Master index returned when creating the master, supports up to 5 devices, range: [0, 4]
            addr: Holding register starting address
            count: Number of consecutive holding register values to read
            val_type: Data type for reading
                      U16 - 16-bit unsigned integer (2 bytes, occupies 1 register);
                      U32 - 32-bit unsigned integer (4 bytes, occupies 2 registers);
                      F32 - 32-bit single-precision float (4 bytes, occupies 2 registers);
                      F64 - 64-bit double-precision float (8 bytes, occupies 4 registers);
                      Default is U16

        Returns:
            str: ErrorID,{value1,value2,...,valuen},GetHoldRegs(index,addr,count,valType);
        """
        if not 0 <= index <= 4:
            raise ValueError("index must be in range [0, 4]")
        if val_type not in ["U16", "U32", "F32", "F64"]:
            raise ValueError("val_type must be 'U16', 'U32', 'F32', or 'F64'")
        
        cmd = f'GetHoldRegs({index},{addr},{count},"{val_type}")'
        return self._send_cmd(cmd)

    def SetHoldRegs(self, index: int, addr: int, count: int, 
                      val_tab: Union[List[int], str], val_type: str = "U16") -> str:
        """
        Write specified values to Modbus slave holding register addresses with specified data type

        Args:
            index: Master index returned when creating the master, supports up to 5 devices, range: [0, 4]
            addr: Holding register starting address
            count: Number of consecutive holding register values to write, range: [1, 4]
            val_tab: Values to write, count must match the count parameter
            val_type: Data type for writing
                      U16 - 16-bit unsigned integer (2 bytes, occupies 1 register);
                      U32 - 32-bit unsigned integer (4 bytes, occupies 2 registers);
                      F32 - 32-bit single-precision float (4 bytes, occupies 2 registers);
                      F64 - 64-bit double-precision float (8 bytes, occupies 4 registers);
                      Default is U16

        Returns:
            str: ErrorID,{},SetHoldRegs(index,addr,count,valTab,valType);
        """
        if not 0 <= index <= 4:
            raise ValueError("index must be in range [0, 4]")
        if not 1 <= count <= 4:
            raise ValueError("count must be in range [1, 4]")
        if val_type not in ["U16", "U32", "F32", "F64"]:
            raise ValueError("val_type must be 'U16', 'U32', 'F32', or 'F64'")
        
        if isinstance(val_tab, list):
            val_str = "{" + ",".join(str(v) for v in val_tab) + "}"
        else:
            val_str = val_tab
        
        cmd = f'SetHoldRegs({index},{addr},{count},{val_str},"{val_type}")'
        return self._send_cmd(cmd)

    def SetSingleHoldReg(self, index: int, addr: int, value: int) -> str:
        """
        Write to a single holding register (new command in V4.6.6)

        Args:
            index: Master index returned when creating the master, range: [0, 4]
            addr: Holding register address
            value: Value to write

        Returns:
            str: ErrorID,{},SetSingleHoldReg(index,addr,value);
        """
        if not 0 <= index <= 4:
            raise ValueError("index must be in range [0, 4]")
        
        cmd = f"SetSingleHoldReg({index},{addr},{value})"
        return self._send_cmd(cmd)

    # ==================== Bus Registers - Input Registers ====================

    def GetInputBool(self, address: int) -> str:
        """
        Get bool type data from input register at specified address

        Args:
            address: Register address, range: [0, 63]

        Returns:
            str: ErrorID,{value},GetInputBool(address);
                 value represents the value at the specified register address, 0 or 1
        """
        if not 0 <= address <= 63:
            raise ValueError("address must be in range [0, 63]")
        
        return self._send_cmd(f"GetInputBool({address})")

    def GetInputInt(self, address: int) -> str:
        """
        Get int type data from input register at specified address

        Args:
            address: Register address, range: [0, 23]

        Returns:
            str: ErrorID,{value},GetInputInt(address);
                 value represents the value at the specified register address, integer (int32)
        """
        if not 0 <= address <= 23:
            raise ValueError("address must be in range [0, 23]")
        
        return self._send_cmd(f"GetInputInt({address})")

    def GetInputFloat(self, address: int) -> str:
        """
        Get float type data from input register at specified address

        Args:
            address: Register address, range: [0, 23]

        Returns:
            str: ErrorID,{value},GetInputFloat(address);
                 value represents the value at the specified register address, single-precision float
        """
        if not 0 <= address <= 23:
            raise ValueError("address must be in range [0, 23]")
        
        return self._send_cmd(f"GetInputFloat({address})")

    # ==================== Bus Registers - Output Registers ====================

    def GetOutputBool(self, address: int) -> str:
        """
        Get bool type data from output register at specified address

        Args:
            address: Register address, range: [0, 63]

        Returns:
            str: ErrorID,{value},GetOutputBool(address);
                 value represents the value at the specified register address, 0 or 1
        """
        if not 0 <= address <= 63:
            raise ValueError("address must be in range [0, 63]")
        
        return self._send_cmd(f"GetOutputBool({address})")

    def GetOutputInt(self, address: int) -> str:
        """
        Get int type data from output register at specified address

        Args:
            address: Register address, range: [0, 23]

        Returns:
            str: ErrorID,{value},GetOutputInt(address);
                 value represents the value at the specified register address, integer (int32)
        """
        if not 0 <= address <= 23:
            raise ValueError("address must be in range [0, 23]")
        
        return self._send_cmd(f"GetOutputInt({address})")

    def GetOutputFloat(self, address: int) -> str:
        """
        Get float type data from output register at specified address

        Args:
            address: Register address, range: [0, 23]

        Returns:
            str: ErrorID,{value},GetOutputFloat(address);
                 value represents the value at the specified register address, single-precision float
        """
        if not 0 <= address <= 23:
            raise ValueError("address must be in range [0, 23]")
        
        return self._send_cmd(f"GetOutputFloat({address})")

    def SetOutputBool(self, address: int, value: int) -> str:
        """
        Set bool value at output register specified address

        Args:
            address: Register address, range: [0, 63]
            value: Value to set, 0 or 1

        Returns:
            str: ErrorID,{},SetOutputBool(address,value);
        """
        if not 0 <= address <= 63:
            raise ValueError("address must be in range [0, 63]")
        if value not in [0, 1]:
            raise ValueError("value must be 0 or 1")
        
        return self._send_cmd(f"SetOutputBool({address},{value})")

    def SetOutputInt(self, address: int, value: int) -> str:
        """
        Set int value at output register specified address

        Args:
            address: Register address, range: [0, 23]
            value: int32 value to set

        Returns:
            str: ErrorID,{},SetOutputInt(address,value);
        """
        if not 0 <= address <= 23:
            raise ValueError("address must be in range [0, 23]")
        
        return self._send_cmd(f"SetOutputInt({address},{value})")

    def SetOutputFloat(self, address: int, value: float) -> str:
        """
        Set float value at output register specified address

        Args:
            address: Register address, range: [0, 23]
            value: float value to set

        Returns:
            str: ErrorID,{},SetOutputFloat(address,value);
        """
        if not 0 <= address <= 23:
            raise ValueError("address must be in range [0, 23]")
        
        return self._send_cmd(f"SetOutputFloat({address},{value})")


