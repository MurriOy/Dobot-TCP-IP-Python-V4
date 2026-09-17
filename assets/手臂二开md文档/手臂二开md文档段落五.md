# Arm Secondary Development MD Document Paragraph 5

## 3 Real-time Feedback Information

The controller provides real-time robot status information through ports 30004, 30005, and 30006.

Port 30004 is the real-time feedback port, where the client receives robot real-time status information every 8ms.

Port 30005 is a configurable robot information feedback port (default is every 200ms; contact technical support if you need to modify it).

Port 30006 is a configurable robot information feedback port (default is every 1000ms; contact technical support if you need to modify it).

Each data packet received through the real-time feedback port contains 1440 bytes, arranged in a standard format as shown in the following table.

Real-time feedback data is stored in little-endian (low-byte first) format, meaning that when a value is stored using multiple bytes, the low bytes of the data are stored in the earlier bytes.

For example, if a data value is 1234, its binary representation is 0000 0100 1101 0010, transmitted via two bytes: the first byte is 1101 0010 (lower 8 bits of the binary value), and the second byte is 0000 0100 (higher 8 bits of the binary value).

| **Meaning**            | **Data Type**     | **Number of Values** | **Byte Size** | **Byte Position**  | **Description**                                                                                                                                                                  |
| -------------------- | -------------- | ------------------ | ---------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MessageSize          | unsigned short | 1                  | 2          | 0000\~0001       | Total message byte length                                                                                                                                                           |
| N/A                  | N/A            | N/A                | 6          | 0002\~0007       | Reserved                                                                                                                                                                   |
| DigitalInputs        | uint64         | 1                  | 8          | 0008\~0015       | Current digital input terminal status. See DI/DO description for details.                                                                                                                                                  |
| DigitalOutputs       | uint64         | 1                  | 8          | 0016\~0023       | Current digital output terminal status. See DI/DO description for details.                                                                                                                                                  |
| RobotMode            | uint64         | 1                  | 8          | 0024\~0031       | Robot mode. See RobotMode command description for details.                                                                                                                                                 |
| TimeStamp            | uint64         | 1                  | 8          | 0032\~0039       | Unix timestamp (unit: ms)                                                                                                                                                         |
| RunTime              | uint64         | 1                  | 8          | 0040\~0047       | Robot power-on running time (unit: ms)                                                                                                                                                       |
| TestValue            | uint64         | 1                  | 8          | 0048\~0055       | Memory structure test standard value 0x0123 4567 89AB CDEF                                                                                                                                       |
| N/A                  | N/A            | N/A                | 8          | 0056\~0063       | Reserved                                                                                                                                                                   |
| SpeedScaling         | double         | 1                  | 8          | 0064\~0071       | Speed scaling                                                                                                                                                                  |
| N/A                  | N/A            | N/A                | 16         | 0072\~0087       | Reserved                                                                                                                                                                   |
| VRobot               | double         | 1                  | 8          | 0088\~0095       | Robot voltage                                                                                                                                                                 |
| IRobot               | double         | 1                  | 8          | 0096\~0103       | Robot current                                                                                                                                                                 |
| ProgramState         | double         | 1                  | 8          | 0104\~0111       | Script running status                                                                                                                                                                |
| SafetyIOIn           | char           | 2                  | 2          | 0112\~0113       | Safety IO input status                                                                                                                                                              |
| SafetyIOOut          | char           | 2                  | 2          | 0114\~0115       | Safety IO output status                                                                                                                                                              |
| N/A                  | N/A            | N/A                | 76         | 0116\~0191       | Reserved                                                                                                                                                                   |
| QTarget              | double         | 6                  | 48         | 0192\~0239       | Target joint position                                                                                                                                                                |
| QDTarget             | double         | 6                  | 48         | 0240\~0287       | Target joint speed                                                                                                                                                                |
| QDDTarget            | double         | 6                  | 48         | 0288\~0335       | Target joint acceleration                                                                                                                                                               |
| ITarget              | double         | 6                  | 48         | 0336\~0383       | Target joint current                                                                                                                                                                |
| MTarget              | double         | 6                  | 48         | 0384\~0431       | Target joint torque                                                                                                                                                                |
| QActual              | double         | 6                  | 48         | 0432\~0479       | Actual joint position                                                                                                                                                                |
| QDActual             | double         | 6                  | 48         | 0480\~0527       | Actual joint speed                                                                                                                                                                |
| IActual              | double         | 6                  | 48         | 0528\~0575       | Actual joint current                                                                                                                                                                |
| ActualTCPForce       | double         | 6                  | 48         | 0576\~0623       | TCP force values for each axis (calculated from raw six-axis force data)                                                                                                                                               |
| ToolVectorActual     | double         | 6                  | 48         | 0624\~0671       | TCP Cartesian actual coordinate values                                                                                                                                                           |
| TCPSpeedActual       | double         | 6                  | 48         | 0672\~0719       | TCP Cartesian actual speed values                                                                                                                                                           |
| TCPForce             | double         | 6                  | 48         | 0720\~0767       | TCP force values (calculated from joint currents)                                                                                                                                                      |
| ToolVectorTarget     | double         | 6                  | 48         | 0768\~0815       | TCP Cartesian target coordinate values                                                                                                                                                           |
| TCPSpeedTarget       | double         | 6                  | 48         | 0816\~0863       | TCP Cartesian target speed values                                                                                                                                                           |
| MotorTemperatures    | double         | 6                  | 48         | 0864\~0911       | Joint temperature                                                                                                                                                                  |
| JointModes           | double         | 6                  | 48         | 0912\~0959       | Joint control mode. 8: Position mode, 10: Torque mode                                                                                                                                                |
| VActual              | double         | 6                  | 48         | 0960\~1007       | Joint voltage                                                                                                                                                                  |
| HandType             | char           | 4                  | 4          | 1008\~1011       | Hand type (reserved parameter)                                                                                                                                                              |
| User                 | char           | 1                  | 1          | 1012             | User coordinate system                                                                                                                                                                 |
| Tool                 | char           | 1                  | 1          | 1013             | Tool coordinate system                                                                                                                                                                 |
| RunQueuedCmd         | char           | 1                  | 1          | 1014             | Algorithm queue running flag                                                                                                                                                              |
| PauseCmdFlag         | char           | 1                  | 1          | 1015             | Algorithm queue pause flag                                                                                                                                                              |
| VelocityRatio        | char           | 1                  | 1          | 1016             | Joint speed ratio (0\~100)                                                                                                                                                        |
| AccelerationRatio    | char           | 1                  | 1          | 1017             | Joint acceleration ratio (0\~100)                                                                                                                                                       |
| N/A                  | N/A            | N/A                | 1          | 1018             | Reserved                                                                                                                                                                   |
| XYZVelocityRatio     | char           | 1                  | 1          | 1019             | Cartesian position speed ratio (0\~100)                                                                                                                                                     |
| RVelocityRatio       | char           | 1                  | 1          | 1020             | Cartesian orientation speed ratio (0\~100)                                                                                                                                                     |
| XYZAccelerationRatio | char           | 1                  | 1          | 1021             | Cartesian position acceleration ratio (0\~100)                                                                                                                                                    |
| RAccelerationRatio   | char           | 1                  | 1          | 1022             | Cartesian orientation acceleration ratio (0\~100)                                                                                                                                                    |
| N/A                  | N/A            | N/A                | 2          | 1023\~1024       | Reserved                                                                                                                                                                   |
| BrakeStatus          | char           | 1                  | 1          | 1025             | Robot brake status. See BrakeStatus description for details.                                                                                                                                               |
| EnableStatus         | char           | 1                  | 1          | 1026             | Robot enable status                                                                                                                                                               |
| DragStatus           | char           | 1                  | 1          | 1027             | Robot drag status. 0: Not in drag state, 1: Joint drag state, 2: Force control drag state                                                                                                                                   |
| RunningStatus        | char           | 1                  | 1          | 1028             | Robot motion status                                                                                                                                                               |
| ErrorStatus          | char           | 1                  | 1          | 1029             | Robot alarm status                                                                                                                                                               |
| JogStatusCR          | char           | 1                  | 1          | 1030             | Robot jog status                                                                                                                                                               |
| CRRobotType          | char           | 1                  | 1          | 1031             | Robot model. See RobotType description for details.                                                                                                                                                   |
| DragButtonSignal     | char           | 1                  | 1          | 1032             | End effector button drag signal                                                                                                                                                              |
| EnableButtonSignal   | char           | 1                  | 1          | 1033             | End effector button enable signal                                                                                                                                                              |
| RecordButtonSignal   | char           | 1                  | 1          | 1034             | End effector button record signal                                                                                                                                                              |
| ReappearButtonSignal | char           | 1                  | 1          | 1035             | End effector button replay signal                                                                                                                                                              |
| JawButtonSignal      | char           | 1                  | 1          | 1036             | End effector button gripper control signal                                                                                                                                                            |
| SixForceOnline       | char           | 1                  | 1          | 1037             | Six-axis force sensor online status. 0: Offline, 1: Online, 2: Abnormal                                                                                                                                            |
| CollisionState       | char           | 1                  | 1          | 1038             | Collision state                                                                                                                                                                  |
| ArmApproachState     | char           | 1                  | 1          | 1039             | Small arm safety skin approach pause                                                                                                                                                            |
| J4ApproachState      | char           | 1                  | 1          | 1040             | J4 safety skin approach pause                                                                                                                                                            |
| J5ApproachState      | char           | 1                  | 1          | 1041             | J5 safety skin approach pause                                                                                                                                                            |
| J6ApproachState      | char           | 1                  | 1          | 1042             | J6 safety skin approach pause                                                                                                                                                            |
| N/A                  | N/A            | N/A                | 61         | 1043\~1103       | Reserved                                                                                                                                                                   |
| VibrationDisZ        | double         | 1                  | 8          | 1104\~1111       | Accelerometer measured Z-axis vibration displacement                                                                                                                                                          |
| CurrentCommandId     | uint64         | 1                  | 8          | 1112\~1119       | Current motion queue id                                                                                                                                                              |
| MActual\[6]          | double         | 6                  | 48         | 1120\~1167       | Actual torque of six joints                                                                                                                                                             |
| Load                 | double         | 1                  | 8          | 1168\~1175       | End effector load weight (unit: kg)                                                                                                                                                          |
| CenterX              | double         | 1                  | 8          | 1176\~1183       | End effector load X-direction eccentric distance (unit: mm)                                                                                                                                                     |
| CenterY              | double         | 1                  | 8          | 1184\~1191       | End effector load Y-direction eccentric distance (unit: mm)                                                                                                                                                     |
| CenterZ              | double         | 1                  | 8          | 1192\~1199       | End effector load Z-direction eccentric distance (unit: mm)                                                                                                                                                     |
| User\[6]             | double         | 6                  | 48         | 1200\~1247       | User coordinate system coordinate values                                                                                                                                                              |
| Tool\[6]             | double         | 6                  | 48         | 1248\~1295       | Tool coordinate system coordinate values                                                                                                                                                              |
| N/A                  | N/A            | N/A                | 8          | 1296\~1303       | Reserved                                                                                                                                                                   |
| SixForceValue\[6]    | double         | 6                  | 48         | 1304\~1351       | Current raw six-axis force data values                                                                                                                                                            |
| TargetQuaternion\[4] | double         | 4                  | 32         | 1352\~1383       | \[qw,qx,qy,qz] Target quaternion                                                                                                                                                  |
| ActualQuaternion\[4] | double         | 4                  | 32         | 1384\~1415       | \[qw,qx,qy,qz] Actual quaternion                                                                                                                                                  |
| AutoManualMode       | char           | 1                  | 2          | 1416\~1417       | Manual/Automatic mode                                                                                                                                                               |
| ExportStatus         | unsigned short | 1                  | 2          | 1418\~1419       | USB drive export status                                                                                                                                                                |
| SafetyState          | char           | 1                  | 1          | 1420             | Safety state: 1420:0 Emergency stop state (active low), 1420:1 Protective stop state (active low), 1420:2 Reduced mode state (active low), 1420:3 Non-stop state (active low), 1420:4 In motion state (active low), 1420:5 System emergency stop state (active low), 1420:6 User emergency stop state (active low), 1420:7 Safety origin output state (active low, valid when not at safety origin) |
| SafeState            | char           | 1                  | 1          | 1421             | Safety state reserved                                                                                                                                                               |
| N/A                  | N/A            | N/A                | 18         | 1422\~1439       | Reserved                                                                                                                                                                   |
| TOTAL                | -              | -                  | 1440       | -                | 1440byte package                                                                                                                                                      |

**Motion Parameter Feedback Description**

If motion parameters (speed, acceleration, etc.) are individually set in the project, the related feedback values will not update immediately, but will update when the robot executes the next motion command.

**DI/DO Description**

DI and DO each occupy 8 bytes, with each byte containing 8 bits (binary), supporting up to 64 DI/DO port states. Each bit from low to high represents the state of a terminal: 1 indicates the corresponding terminal is ON, 0 indicates the corresponding terminal is OFF or does not exist.

For example:

* The first byte of DI is 0x01, binary representation 00000001, representing the status of DI\_1 \~ DI\_8 from low to high, meaning DI\_1 is ON and the other 7 DIs are OFF.
* The second byte is 0x02, binary representation 00000010, representing the status of DI\_9 \~ DI\_16 from low to high, meaning DI\_10 is ON and the other 7 DIs are OFF.
* Subsequent bytes follow the same pattern. Depending on the control cabinet, the number of IO terminals varies, and binary bits exceeding the IO terminal count are all filled with 0.

**BrakeStatus Description**

This byte expresses the brake status of each joint in bits. A corresponding bit of 1 indicates that the joint brake is released. The correspondence between bit positions and joints is shown in the following table:

| **Bit** | **7** | **6** | **5** | **4** | **3** | **2** | **1** | **0** |
| ------ | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| Meaning     | Reserved   | Reserved   | Joint 1   | Joint 2   | Joint 3   | Joint 4   | Joint 5   | Joint 6   |

Examples:

* 0x01 (00000001): Joint 6 brake released
* 0x02 (00000010): Joint 5 brake released
* 0x03 (00000011): Joint 5 and Joint 6 brakes released
* 0x04 (00000100): Joint 4 brake released

**RobotType Description**

| **Value** | **Represented Model**    |
| ------ | ----------- |
| 3      | CR3         |
| 5      | CR5         |
| 7      | CR7         |
| 10     | CR10        |
| 12     | CR12        |
| 16     | CR16        |
| 101    | Nova 2      |
| 103    | Nova 5      |
| 113    | CR3A        |
| 115    | CR5A        |
| 116    | CR5AF       |
| 117    | CR7A        |
| 120    | CR10A       |
| 121    | CR10AF      |
| 122    | CR12A       |
| 126    | CR16A       |
| 127    | CR20AF      |
| 130    | CR20A       |
| 150    | Magician E6 |
| 160    | New Nova 2    |
| 161    | New Nova 5    |
| 162    | New Nova 2S   |
| 203    | CR3V        |
| 205    | CR5V        |
| 207    | CR7V        |
| 210    | CR10V       |
| 212    | CR12V       |
| 216    | CR16V       |
| 220    | CR20V       |

## 4 General Error Codes

| **Error Code** | **Description**                                                       | **Notes**                                                                                                      |
| ------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| 0       | No error                                                          | Command sent successfully                                                                                                      |
| -1      | Command execution failure                                                       | Command received but execution failed                                                                                                |
| -2      | Robot is in alarm state                                                    | Commands cannot be executed in robot alarm state. Clear the alarm and resend the command.                                                                               |
| -3      | Robot is in emergency stop state                                                    | Commands cannot be executed in robot emergency stop state. Release the emergency stop and clear the alarm, then resend the command.                                                                          |
| -4      | Robot is in power-off state                                                    | Commands cannot be executed in robot power-off state. Power on the robot first.                                                                                   |
| -5      | Robot is in script running state                                                  | Some commands are rejected when the robot is in script running state. Pause/stop the script first.                                                                            |
| -6      | MoveJog command axis does not match motion type                                         | Modify the coordtype parameter value. See MoveJog command description for details.                                                                               |
| -7      | Robot is in script paused state                                                  | Some commands are rejected when the robot is in script paused state. Stop the script first.                                                                               |
| -8      | Robot authentication expired                                                      | Robot is in unusable state. Contact FAE for handling.                                                                                        |
| -9      | Corresponding command is in disabled state                                                   | Safety commands SetSafeWallEnable, SetFCCollision, FCCollisionSwitch, SetCollisionLevel, SetBackDistance are in disabled state.           |
| ...     | ...                                                          | ...                                                                                                         |
| -10000  | Command error                                                         | The sent command does not exist                                                                                                    |
| -20000  | Parameter count error                                                       | The number of parameters in the sent command is incorrect                                                                                                |
| -30001  | When named parameters are present among required parameters, it indicates that the data type of any named required parameter is incorrect. Otherwise, it indicates the data type of the first unnamed parameter is incorrect.   | -3000X indicates required parameter data type error. When named required parameters exist, it indicates the named required parameter type is incorrect, e.g., joint="a". Otherwise, the last digit 1 indicates the first required parameter's data type is incorrect.                          |
| -30002  | Parameter type of the second unnamed required parameter is incorrect                                          | -3000X indicates required parameter type error. The last digit 2 indicates the second required parameter's parameter type is incorrect.                                                                    |
| ...     | ...                                                          | ...                                                                                                         |
| -40001  | When named parameters are present among required parameters, it indicates that the range of any named required parameter is incorrect. The range of the first parameter is incorrect.                | -4000X indicates required parameter range error. When named required parameters exist, it indicates the named required parameter range is incorrect, e.g., joint={999,999,999,999,999,999,999}. Otherwise, the last digit 1 indicates the first required parameter's range is incorrect. |
| -40002  | Range of the second unnamed required parameter is incorrect                                          | -4000X indicates required parameter range error. The last digit 2 indicates the second required parameter's range is incorrect.                                                                    |
| ...     | ...                                                          | ...                                                                                                         |
| -50001  | When named parameters are present among optional parameters, it indicates that the data type of any named optional parameter is incorrect. Otherwise, it indicates the data type of the first unnamed optional parameter is incorrect. | -5000X indicates optional parameter data type error. When named optional parameters exist, it indicates the named optional parameter data type is incorrect, e.g., user="ss". Otherwise, the last digit 1 indicates the first optional parameter's data type is incorrect.                     |
| -50002  | Parameter data type of the second unnamed optional parameter is incorrect                                        | -5000X indicates optional parameter data type error. The last digit 2 indicates the second parameter's data type is incorrect.                                                                  |
| ...     | ...                                                          | ...                                                                                                         |
| -60001  | When named parameters are present among optional parameters, it indicates that the range of any named optional parameter is incorrect. Otherwise, it indicates the range of the first unnamed optional parameter is incorrect.     | -6000X indicates optional parameter range error. When named optional parameters exist, it indicates the named optional parameter is incorrect, e.g., a=200. The last digit 1 indicates the first optional parameter's range is incorrect.                                   |
| -60002  | Range of the second unnamed optional parameter is incorrect                                          | -60000 indicates optional parameter range error. The last digit 2 indicates the second optional parameter's range is incorrect.                                                                    |
| ...     | ...                                                          | ...                                                                                                         |

**Description:** Named parameters refer to parameters in the format "key=value". The system checks parameters from front to back; if multiple parameters have errors, it will report the error code of the first error detected.

**Error Example 1**

```
// Prototype: MovJ(P,user,tool,a,v,cp)
MovJ(joint="a",user=1, tool=0, a=20, v=50, cp=100)
```

In the above example, the named required parameter "joint" has an incorrect data type, resulting in error -30001.

**Error Example 2**

```
// Prototype: DO(index,status,time)
DO(1,"2")
```

In the above example, the second unnamed required parameter has an incorrect data type, resulting in error -30002.

**Error Example 3**

```
// Prototype: MovJ(P,user,tool,a,v,cp)
MovJ(pose={-500,100,200,150,0,90},user="ss", tool=0, a=20, v=50, cp=100)
```

In the above example, the named optional parameter "user" has an incorrect data type, resulting in error -50001.

**Error Example 4**

```
// Prototype: EnableRobot(load,centerX,centerY,centerZ)
EnableRobot(1.5,"a",0,30.5)
```

In the above example, the second unnamed optional parameter has an incorrect data type, resulting in error -50002.

**Error Example 5**

```
// Prototype: SetUser(index,table,type)
SetUser(1,{0,0,100,0,0,0}123,1)
```

The system checks parameter quantity before checking parameter types. If there are other characters between `}` and the next `,` in the command parameters, it will cause the parameters to be incorrectly parsed. For example, `{0,0,100,0,0,0}123` will be parsed as two parameters: `{0,0,100,0,0,0}` and `123`, causing this command to report -20000 (parameter count error) instead of -30002 (required parameter 2 type error).

## 5 TCP Commands Allowed in Each State

**The operating state of RequestControl() is not described here; please refer to the RequestControl() command for details.**

**Error State**

TCP commands allowed when the robot is in error state (including emergency stop):

```
ClearError()
GetErrorID()
EmergencyStop()
Stop()
RobotMode()
LogExportUSB()
GetExportStatus()
```

**Power-off State**

The control cabinet is powered on, but the robot is not powered on.

In addition to the commands allowed in error state, the following commands are also supported:

```
PowerOn()
```

**Script Running State**

The script project is running. The following commands are allowed:

```
SpeedFactor()
RobotMode()
DoInstant()
ToolDoInstant()
AOInstant()
Stop()
Pause()
Continue()
GetStartPose()
PositiveKin()
InverseSolution()
GetAngle()
GetPose()
EmergencyStop()
ModbusCreate()
ModbusClose()
GetInBits()
GetInRegs()
GetCoils()
SetCoils()
GetHoldRegs()
SetHoldRegs()
GetErrorID()
DI()
ToolDI()
AI()
ToolAI()
DIGroup()
GetDO()
GetAO()
GetDOGroup()
SetTool485()
SetToolPower()
SetToolMode()
CalcUser()
CalcTool()
GetInputBool()
GetInputInt()
GetInputFloat()
GetOutputBool()
GetOutputInt()
GetOutputFloat()
SetOutputBool()
SetOutputInt()
SetOutputFloat()
GetCurrentCommandId()
LogExportUSB()
GetExportStatus()
ClearError()
GetForce()
```

**Script Paused State**

The script project is paused.

In addition to the commands allowed in script running state, the following commands are also supported:

```
EnableRobot()
DisableRobot()
RunTo()
PathRecovery()
StartDrag()
StopDrag()
SixForceHome()
EnableFTSensor()
ForceDriveMode()
ForceDriveSpeed()
```

**Other States**

No restrictions; all commands can be sent.