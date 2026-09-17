# Arm Secondary Development Documentation - Section 1

# Preface

# Purpose

This manual introduces the DOBOT industrial robot controller V4 TCP/IP secondary development interface and its usage, helping users understand and develop TCP/IP-based robot control software.

![](attachment/1.png)

# Target Audience

This manual is suitable for:

Customers

● Sales engineers

Installation and commissioning engineers

· Technical support engineers

# Revision History

| **Time** | **Version** | **Revision History** |
|----------|-------------|---------------------|
| 2026/04/10 | V4.6.6 | 1. Added SetSingleCoil and SetSingleHoldReg commands to Modbus-related instructions. 2. Updated port 30005 definition. 3. Added error code -9 description to general error codes. |
| 2025/10/15 | V4.6.5 | 1. Added GetScrName command to calculation and query instructions. 2. Added DOGroupDEC, DIGroupDEC, GetDOGroupDEC commands to IO instructions. 3. Added MovS, ArcIO, StartRTOffset, EndRTOffset, OffsetPara commands to motion instructions. 4. Added conveyor belt commands. 5. Optimized RunTo, Arc, Circle, GetStartPose motion commands. |
| 2025/05/08 | V4.6.2 | 1. Corresponds to 6-axis robot controller v4.6.2. 2. Added force control commands SetFCCollision, FCCollisionSwitch. |
| 2025/03/20 | V4.6.0 | Updated GetErrorID command return value. |

| **Time** | **Version** | **Revision History** |
|----------|-------------|---------------------|
| 2024/12/26 | V4.6.0 | 1. Corresponds to 6-axis robot controller v4.6.0. 2. Added RequestControl command, trajectory recovery commands, log export commands, force control commands, motion commands RelPointTool, RelPointUser, RelJoint. 3. Added general error code -8, added allowed TCP commands in various states. 4. Fixed StartPath command format. 5. Fixed index ranges for DO, DI, ToolDO, ToolDI, ToolAI. 6. Fixed ServoP, ServoJ command runtime ranges. 7. Optimized real-time feedback information. |
| 2024/08/15 | V4.5.1 | Fixed ServoJ command example, added ServoJ and ServoP return values. |
| 2024/03/25 | V4.5.1 | Corresponds to 6-axis robot controller v4.5.1. |
| 2023/10/19 | V4.5.0 | Corresponds to 6-axis robot controller v4.5.0, added CreateTray, GetTrayPoint, ServoJ, ServoP commands, optimized some descriptions. |
| 2023/07/26 | V4.4.0 | Corresponds to 6-axis robot controller v4.4.0. |
| 2023/05/12 | V4.3.0 | Corresponds to 6-axis robot controller v4.3.0. |
| 2023/02/17 | V4.2.0 | Corresponds to 6-axis robot controller v4.2.0. |

# 1 Overview

Due to the low cost, high reliability, strong practicality, and high performance of TCP/IP-based communication, many industrial automation projects have extensive needs for controlling robots based on TCP/IP protocol. Therefore, DOBOT robots provide rich interfaces for interaction with external devices based on TCP/IP protocol.

# Port Description

By design, DOBOT robots open server ports 29999, 30004, 30005, and 30006:

● Port 29999: The host computer can directly send control commands to the robot through port 29999, or actively obtain certain robot status. These functions are called Dashboard.

● Ports 30004, 30005, and 30006: Port 30004 is the real-time feedback port, where the client can receive real-time robot status information every 8ms. Ports 30005 and 30006 are configurable feedback ports (port 30005 defaults to 200ms feedback, port 30006 defaults to 1000ms feedback; contact technical support for modifications). Each data packet received through the real-time feedback port contains 1440 bytes, arranged in standard format.

# Message Format

Message commands and responses are in ASCII format (string format).

Host computer message format:

MessageName(Param1,Param2,Param3......ParamN)

Consists of message name and parameters, parameters are placed in parentheses, separated by English commas ",", and a complete message ends with a right parenthesis.

TCP/IP remote control commands are case-insensitive. The following three formats are all recognized as enable robot commands:

● ENABLEROBOT()

● enablerobot()

● eNabLErobOt()

After receiving the command, the robot returns a response message in the following format:

ErrorID, {value, ..., valueN}, MessageName(Param1,Param2,Param3......ParamN);

● ErrorID of 0 indicates successful command reception, non-zero indicates command error (see general error codes);

● {value, ..., valueN} represents return values; {} is returned if no return values;

● MessageName(Param1,Param2,Param3,ParamN) is the sent command message.

Example:

Sent:

```
MovL(-500,100,200,150,0,90)
```

Returned:

```
0, {}, MovL(-500, 100, 200, 150, 0, 90);
```

0 indicates successful reception, {} indicates no return values.

Sent:

```
Mov(-500,100,200,150,0,90)
```

Returned:

```
-10000, {}, Mov(-500, 100, 200, 150, 0, 90);
```

-10000 indicates command does not exist, {} indicates no return values.

# Queued Commands and Immediate Commands

● Queued commands: The system waits for the previous command queue to complete execution before executing this command. For example, if a DO command is preceded by a series of motion commands, the system waits for the robot to complete motion before setting DO.

· Immediate commands: The system ignores the command queue and executes immediately after reading this command. For example, if a DOInstant command is preceded by a series of motion commands, the system does not wait for the robot to complete motion, but sets DO immediately after reading this command.

Unless otherwise specified, input reading commands are all immediate commands.

The examples in this document are pseudocode and cannot be run directly; they are only used to illustrate how to use the interfaces.
