# Arm Secondary Development MD Documentation - Part Three

## 2.8 Path Recovery Commands

Functional Overview

When the pause state supports jog functionality enabled, during project pause, the user can send MoveJog, RunTo, and drag mode entry/exit commands to change the robot's posture. Before resuming the project, the user can use the path recovery command to restore the robot to the paused position, preventing abnormal robot motion after resuming the project.

Command List

| **Command**         | **Function**              | **Command Type** |
| ------------------ | ----------------------- | ------------ |
| SetResumeOffset    | Set path recovery return distance | Immediate Command |
| PathRecovery       | Start path recovery       | Immediate Command |
| PathRecoveryStop   | Stop robot during path recovery | Immediate Command |
| PathRecoveryStatus | Query path recovery status | Immediate Command |

SetResumeOffset

Prototype

SetResumeOffset(distance)

Description

This command is only used for welding processes. Sets the return distance of the path recovery target point relative to the paused position along the weld seam.

Note:

This command only takes effect during welding (i.e., when WeldArcSpeed is active).

This command requires setting the return distance before pausing in order to properly plan the return point.

Required Parameters

| **Parameter Name** | **Type** | **Description**                                          |
| -------------- | ------ | ------------------------------------------------------- |
| distance | double | Sets the return distance along the forward direction during path recovery after pausing, unit: mm. |

Return

ErrorID,\{},SetResumeOffset(distance);

PathRecovery

Prototype

PathRecovery()

Description

Start path recovery: After the project is paused, control the robot to return to the posture at the time of pausing.

Note:

This command only controls the robot to return to the posture at the time of pausing. To continue the project, the Continue command needs to be sent.

This command is an asynchronous interface that returns immediately after sending. Whether the robot has returned to the posture at the time of pausing needs to be determined through the PathRecoveryStatus command.

Return

ErrorID,\{},PathRecovery();

PathRecoveryStop

Prototype

PathRecoveryStop()

Description

Stop the robot during path recovery.

Return

ErrorID,\{},PathRecoveryStop();

PathRecoveryStatus

Prototype

PathRecoveryStatus()

Description

Query the path recovery status.

Return

ErrorID,\{status},PathRecoveryStatus();

Where status indicates the path recovery status:

0: Returned to the posture at the time of pausing.

1: Not returned to the posture at the time of pausing, with a small deviation from the posture at the time of pausing.

2: Not returned to the posture at the time of pausing, with a large deviation from the posture at the time of pausing.

Command Example

SetResumeOffset(10); // Set welding return distance to 10mm

MovL(P1);// Linear motion to point P1 at global speed

WeldArcSpeed(10);// Set welding speed to 10mm/s

WeldArcSpeedStart();// Turn on welding speed switch

MovL(P2);// Linear motion to point P2 at set welding speed

WeldArcSpeedEnd();// Turn off welding speed switch

// After obtaining the project pause status through real-time feedback or RobotMode polling

RunTo(P); // Move the paused robot to a safe point for manual handling

PathRecovery(); // Robot returns to the offset position (return 10mm along the weld seam) at the paused point

PathRecoveryStop(); // Stop the robot when an anomaly is detected during path recovery.

RunTo(P); // Move the robot to a safe point again for manual handling

PathRecovery(); // Robot returns to the offset paused point

if(PathRecoveryStatus()=0)

\{

// Robot has returned to the offset paused point

Continue(); // Continue running the project

}

## 2.9 Log Export Commands

Functional Overview

This group of commands is used to export robot logs and view export status.

Command List

| **Command**       | **Function**          | **Command Type** |
| --------------- | ------------------- | ------------ |
| LogExportUSB    | Export robot logs to USB drive | Immediate Command |
| GetExportStatus | Get log export status | Immediate Command |

LogExportUSB

Prototype

LogExportUSB(range)

Description

Export robot logs to the root directory of the USB drive inserted into the robot control cabinet's USB interface.

Note:

When exporting logs, it is recommended to insert only one USB drive to avoid export failure.

If the USB drive contains multiple partitions, the logs will be exported to the first partition. Some storage devices (e.g., USB drives used as boot drives) have a hidden first partition, which may cause the exported logs to not be directly visible in Windows.

Do not remove the USB drive during the export process, as this may cause file corruption, and the USB drive must be formatted before exporting again.

Required Parameters

| **Parameter Name** | **Type** | **Description**                                                           |
| ------------ | ------ | ----------------------------------------------------------------------- |
| range   | int    | Export range. 0: Export contents of logs/all and logs/user folders. 1: Export all contents of the logs folder. |

Return

ErrorID,\{},LogExportUSB(range);

This command returns immediately after sending. Please use GetExportStatus to get the log export status. If this command is sent during the export process, it will return -1, indicating command execution failure.

Example

LogExportUSB(0)

Export contents of logs/all and logs/user folders to the USB drive.

GetExportStatus

Prototype

GetExportStatus()

Description

Get the log export status.

Return

ErrorID,\{status},GetExportStatus();

Where status indicates the log export status.

0: Export not started

1: Exporting

2: Export complete

3: Export failed, USB drive not found

4: Export failed, insufficient USB drive space

5: Export failed, USB drive removed during export

The export complete and export failure status will be maintained until the user uses the export function again.

## 2.10 Force Control Commands

Functional Overview

Dobot supports optional six-axis force sensors and implements force control function on/off and settings through the force control plugin. Force-controlled drag refers to drag-and-drop teaching functionality based on end-effector force analysis. When the user applies a force on the six-axis force sensor at the end-effector, the robot moves in the direction of the force, and the movement speed is proportional to the force magnitude within a certain range. In practical applications, the user can also constrain the robot's movement direction to move only along one or several directions.

Command List

| **Command**            | **Function**                             | **Command Type** |
| -------------------- | -------------------------------------- | ------------ |
| EnableFTSensor       | Enable/disable force sensor                  | Immediate Command |
| SixForceHome         | Force sensor homing                     | Immediate Command |
| GetForce             | Get force sensor values                   | Immediate Command |
| ForceDriveMode       | Enter force-controlled drag mode                   | Immediate Command |
| ForceDriveSpeed      | Set force-controlled drag speed                   | Immediate Command |
| FCForceMode          | Enable force control with user-specified parameters               | Queue Command     |
| FCSetDeviation       | Set displacement and attitude deviation in force control mode            | Immediate Command |
| FCSetForceLimit      | Set maximum force limit                    | Immediate Command |
| FCSetMass            | Set inertia coefficients in each direction in force control mode            | Immediate Command |
| FCSetStiffness       | Set elasticity coefficients in each direction in force control mode            | Immediate Command |
| FCSetDamping         | Set damping coefficients in each direction in force control mode            | Immediate Command |
| FCOff                | Exit force control mode                     | Queue Command     |
| FCSetForceSpeedLimit | Set force control adjustment speed in each direction               | Immediate Command |
| FCSetForce           | Real-time adjustment of constant force settings                   | Immediate Command |
| SetFCCollision       | Set force sensor collision detection threshold parameters (CRAF models only) | Immediate Command |
| FCCollisionSwitch    | Enable/disable force sensor collision detection switch (CRAF models only) | Immediate Command |

EnableFTSensor

Prototype

EnableFTSensor(status)

Description

Enable/disable the force sensor.

Required Parameters

| **Parameter Name** | **Type** | **Description**             |
| ------- | ------ | ---------------------- |
| status  | int    | Force sensor switch, 1 for enable, 0 for disable. |

Return

ErrorID,\{},EnableFTSensor(status);

Example

EnableFTSensor(1)

Turn on the force sensor.

SixForceHome

Prototype

SixForceHome()

Description

Set the current force sensor value to 0, using the current sensor force state as the zero point.

Return

ErrorID,\{},SixForceHome();

Example

SixForceHome()

Set the current force sensor value to 0.

GetForce

Prototype

GetForce(tool)

Description

Get the current force sensor values.

Optional Parameters

| **Parameter Name** | **Type** | **Description**                                        |
| ------- | ------ | ------------------------------------------------- |
| tool    | int    | Used to specify the tool coordinate system reference for obtaining values, range: \[0,50]. When not specified, the global tool coordinate system is used. |

Return

ErrorID,\{Fx,Fy,Fz,Mx,My,Mz},GetForce(tool);

Fx, Fy, Fz are the force values in each direction of the reference coordinate system, Mx, My, Mz are the torque values.

Example

GetForce(1)

Get the current force sensor values under tool coordinate system 1.

ForceDriveMode

Prototype

ForceDriveMode(\{x,y,z,rx,ry,rz},user)

Description

Specify the draggable directions and enter force-controlled drag mode.

Required Parameters

| **Parameter Name**  | **Type** | **Description**                                                                                                                                    |
| ----------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| \{x,y,z,rx,ry,rz} | string | Used to specify the draggable directions. 0 means that direction cannot be dragged, 1 means that direction can be dragged. Example: \{1,1,1,1,1,1} means the robot arm can be freely dragged in all axis directions. \{1,1,1,0,0,0} means the robot arm can only be dragged in XYZ axis directions. \{0,0,0,1,1,1} means the robot arm can only rotate in RxRyRz axis directions. |

Optional Parameters

| **Parameter Name** | **Type** | **Description**                                                 |
| ------- | ------ | ---------------------------------------------------------- |
| user    | int    | Used to specify the user coordinate system reference during dragging, range: \[0,50]. When not specified, it means not referencing the user coordinate system, referencing the global tool coordinate system. |

Return

ErrorID,\{},ForceDriveMode(\{x,y,z,rx,ry,rz},user);

Example 1

ForceDriveMode(\{1,1,1,1,1,1},1)

Enter force-controlled drag mode, can be freely dragged in all axis directions of user coordinate system 1.

Example 2

ForceDriveMode(\{1,1,1,0,0,0})

Enter force-controlled drag mode, can be dragged in XYZ axis directions of the global tool coordinate system.

ForceDriveSpeed

Prototype

ForceDriveSpeed(speed)

Description

Set the force-controlled drag speed ratio.

Required Parameters

| **Parameter Name** | **Type** | **Description**                 |
| ------- | ------ | -------------------------- |
| speed   | int    | Force-controlled drag speed ratio, range: \[1,100]. |

Return

ErrorID,\{},ForceDriveSpeed(speed);

Example

ForceDriveSpeed(10)

Set the force-controlled drag speed ratio to 10.

FCForceMode

Prototype

FCForceMode(\{x,y,z,rx,ry,rz},\{fx,fy,fz,frx,fry,frz},reference,user,tool)

Description

Enable force control with user-specified configuration parameters.

Required Parameters

| **Parameter Name**        | **Type** | **Description**                                                                                                                                                                                   |
| ----------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| \{x,y,z,rx,ry,rz}       | string | Enable/disable force control adjustment in a specific Cartesian space direction. 0 means force control is disabled for that direction. 1 means force control is enabled for that direction.                                                                           |
| \{fx,fy,fz,frx,fry,frz} | string | Target force: The target value of the contact force between the tool end-effector and the workpiece, which is an analog force that can be set by the user. The target force directions correspond to the \{x,y,z,rx,ry,rz} directions in Cartesian space. Displacement direction target force range \[-200,200], unit N; attitude direction target force range \[-12,12], unit N/m. When target force is 0, it is in compliant mode, which is similar to force-controlled dragging. If force control adjustment is not enabled for a certain direction, the target force for that direction will also not take effect. |

Optional Parameters

| **Parameter Name** | **Type** | **Description**                                                                                                               |
| --------- | ------ | -------------------------------------------------------------------------------------------------------------------- |
| reference | string | Format is "reference=value". Value indicates the reference coordinate system, default is tool coordinate system. reference=0 means referencing the tool coordinate system, i.e., force control adjustment along the tool coordinate system. reference=1 means referencing the user coordinate system, i.e., force control adjustment along the user coordinate system. |
| user      | string | Format is "user=index", index is the calibrated user coordinate system index. Range: \[0,50].                                                                      |
| tool      | string | Format is "tool=index", index is the calibrated tool coordinate system index. Range: \[0,50].                                                                      |

Return

ErrorID,\{ResultID},FCForceMode(\{x,y,z,rx,ry,rz},\{fx,fy,fz,frx,fry,frz},reference,user,tool);

Example

FCForceMode(\{1,1,1,1,1,1},\{100,100,100,10,10,10},reference=1,user=1)

Perform force control adjustment in all directions referencing calibrated user coordinate system 1, with displacement direction target force of 100N and attitude direction target force of 10N/m.

FCSetDeviation

Prototype

FCSetDeviation(\{x,y,z,rx,ry,rz}，controltype)

Description

Set the displacement and attitude deviation in force control mode. If the constant force deviates a large distance during force control, the robot will perform corresponding processing.

Required Parameters

| **Parameter Name**  | **Type** | **Description**                                                                                         |
| ----------------- | ------ | ---------------------------------------------------------------------------------------------- |
| \{x,y,z,rx,ry,rz} | string | x, y, z represent the displacement deviation in force control mode, unit: mm. Range: (0,1000], default 100mm. rx, ry, rz represent the attitude deviation in force control mode, unit: degrees. Range: (0,360], default 36 degrees. |

Optional Parameters

| **Parameter Name** | **Type** | **Description**                                                                   |
| ----------- | ------ | ------------------------------------------------------------------------ |
| controltype | int    | Indicates how the robot arm handles the situation when the threshold is exceeded during force control. 0: When threshold is exceeded, the robot arm alarms (default). 1: When threshold is exceeded, the robot arm stops searching and continues motion on the original trajectory. |

Return

ErrorID,\{},FCSetDeviation(\{x,y,z,rx,ry,rz}，controltype);

Example

FCSetDeviation(\{200,200,200,36,36,36})

Set the displacement deviation in x, y, z directions to 200mm and the attitude deviation in rx, ry, rz directions to 36° in force control mode.

After exiting TCP mode, the parameters are restored to default values.

FCSetForceLimit

Prototype

FCSetForceLimit(x,y,z,rx,ry,rz)

Description

Set the maximum force limit for each direction (this setting takes effect for all directions, including directions where force control is not enabled).

Required Parameters

| **Parameter Name** | **Type** | **Description**                      |
| ------- | ------ | ---------------------------- |
| x       | double | Force limit in x direction, range: (0,500], default 500. |
| y       | double | Force limit in y direction, range: (0,500], default 500. |
| z       | double | Force limit in z direction, range: (0,500], default 500. |
| rx      | double | Force limit in rx direction, range: (0,50], default 50.  |
| ry      | double | Force limit in ry direction, range: (0,50], default 50.  |
| rz      | double | Force limit in rz direction, range: (0,50], default 50.  |

Return

ErrorID,\{},FCSetForceLimit(x,y,z,rx,ry,rz);

Example

FCSetForceLimit(500,500,500,50,50,50)

When FCSetForceLimit is not called, the maximum force limit in x, y, z directions defaults to 500; the maximum force limit in rx, ry, rz directions defaults to 50.

After exiting TCP mode, the parameters are restored to default values.

FCSetMass

Prototype

FCSetMass(x,y,z,rx,ry,rz)

Description

Set the inertia coefficients in each direction in force control mode.

Required Parameters

| **Parameter Name** | **Type** | **Description**                         |
| ------- | ------ | ------------------------------- |
| x       | double | Inertia coefficient in x direction, range: (0,10000], default 20.  |
| y       | double | Inertia coefficient in y direction, range: (0,10000], default 20.  |
| z       | double | Inertia coefficient in z direction, range: (0,10000], default 20.  |
| rx      | double | Inertia coefficient in rx direction, range: (0,10000], default 20. |
| ry      | double | Inertia coefficient in ry direction, range: (0,10000], default 20. |
| rz      | double | Inertia coefficient in rz direction, range: (0,10000], default 20. |

Return

ErrorID,\{},FCSetMass(x,y,z,rx,ry,rz);

Example

FCSetMass(20,20,20,20,20,20)

When FCSetMass is not called, the inertia coefficient in each direction defaults to 20.

After exiting TCP mode, the parameters are restored to default values.

FCSetStiffness

Prototype

FCSetStiffness(x,y,z,rx,ry,rz)

Description

Set the elasticity coefficients in each direction in force control mode.

Required Parameters

| **Parameter Name** | **Type** | **Description**                          |
| ------- | ------ | -------------------------------- |
| x       | double | Elasticity coefficient in x direction, range: \[0,10000], default 30.  |
| y       | double | Elasticity coefficient in y direction, range: \[0,10000], default 30.  |
| z       | double | Elasticity coefficient in z direction, range: \[0,10000], default 30.  |
| rx      | double | Elasticity coefficient in rx direction, range: \[0,10000], default 30. |
| ry      | double | Elasticity coefficient in ry direction, range: \[0,10000], default 30. |
| rz      | double | Elasticity coefficient in rz direction, range: \[0,10000], default 30. |

Return

ErrorID,\{},FCSetStiffness(x,y,z,rx,ry,rz);

Example

FCSetStiffness(30,30,30,30,30,30)

When FCSetStiffness is not called, the default elasticity coefficient in each direction is 30.

After exiting TCP mode, the parameters are restored to default values.

FCSetDamping

Prototype

FCSetDamping(x,y,z,rx,ry,rz)

Description

Set the damping coefficients in each direction in force control mode.

Required Parameters

| **Parameter Name** | **Type** | **Description**                         |
| ------- | ------ | ------------------------------- |
| x       | double | Damping coefficient in x direction, range: \[0,1000], default 50.  |
| y       | double | Damping coefficient in y direction, range: \[0,1000], default 50.  |
| z       | double | Damping coefficient in z direction, range: \[0,1000], default 50.  |
| rx      | double | Damping coefficient in rx direction, range: \[0,1000], default 50. |
| ry      | double | Damping coefficient in ry direction, range: \[0,1000], default 50. |
| rz      | double | Damping coefficient in rz direction, range: \[0,1000], default 50. |

Return

ErrorID,\{},FCSetDamping(x,y,z,rx,ry,rz);

Example

FCSetDamping(50,50,50,50,50,50)

When FCSetDamping is not called, the default damping coefficient in each direction is 50.

After exiting TCP mode, the parameters are restored to default values.

FCOff

Prototype

FCOff()

Description

Exit force control mode, used in conjunction with FCForceMode. The motion commands between them will perform force compliance control.

Return

ErrorID,\{ResultID},FCOff();

Example

FCOff()

Turn off force control.

FCSetForceSpeedLimit

Prototype

FCSetForceSpeedLimit(x,y,z,rx,ry,rz)

Description

Set the force control adjustment speed for each direction. When the force control speed limit is small, the force control adjustment speed is slower, suitable for low-speed gentle contact surfaces.

When the force control speed limit is large, the force control adjustment speed is fast, suitable for high-speed force control applications. Adjustment is needed according to the specific application scenario.

Required Parameters

| **Parameter Name** | **Type** | **Description**                                                                               |
| ------- | ------ | ------------------------------------------------------------------------------------ |
| x       | double | Force control adjustment speed in x direction, default 20mm/s. CRA model range: (0, safety limit TCP speed value]. Other models range: (0,300].                    |
| y       | double | Force control adjustment speed in y direction, default 20mm/s. CRA model range: (0, safety limit TCP speed value]. Other models range: (0,300].                    |
| z       | double | Force control adjustment speed in z direction, default 20mm/s. CRA model range: (0, safety limit TCP speed value]. Other models range: (0,300].                    |
| rx      | double | Force control adjustment speed in rx direction, default 20°/s. CRA model range: (0, (4×safety limit TCP speed value ×0.001/ 3.14 ×180)]. Other models range: (0,90]. |
| ry      | double | Force control adjustment speed in ry direction, default 20°/s. CRA model range: (0, (4×safety limit TCP speed value ×0.001/ 3.14 ×180)]. Other models range: (0,90]. |
| rz      | double | Force control adjustment speed in rz direction, default 20°/s. CRA model range: (0, (4×safety limit TCP speed value ×0.001/ 3.14 ×180)]. Other models range: (0,90]. |

Return

ErrorID,\{},FCSetForceSpeedLimit(x,y,z,rx,ry,rz);

Example

FCSetForceSpeedLimit(20,20,20,20,20,20)

When FCSetForceSpeedLimit is not called, the force control adjustment speed in each direction defaults to 20mm/s.

After exiting TCP mode, the parameters are restored to default values.

FCSetForce

Prototype

FCSetForce(x,y,z,rx,ry,rz)

Description

Real-time adjustment of constant force settings for each direction.

Required Parameters

| **Parameter Name** | **Type** | **Description**                        |
| ------- | ------ | ------------------------------ |
| x       | double | Constant force value in x direction. Range: \[-200,200], unit N.  |
| y       | double | Constant force value in y direction. Range: \[-200,200], unit N.  |
| z       | double | Constant force value in z direction. Range: \[-200,200], unit N.  |
| rx      | double | Constant force value in rx direction. Range: \[-12,12], unit N/m. |
| ry      | double | Constant force value in ry direction. Range: \[-12,12], unit N/m. |
| rz      | double | Constant force value in rz direction. Range: \[-12,12], unit N/m. |

Return

ErrorID,\{},FCSetForce(x,y,z,rx,ry,rz);

Example

FCSetForce(50,50,50,10,10,10)

Constant force setting in x, y, z directions is 50N. Constant force setting in rx, ry, rz directions is 10N/m.

SetFCCollision

Prototype

SetFCCollision(force,torque)

Description

Set the force sensor collision detection threshold parameters. When the collision force or collision torque at the robot end exceeds the set threshold, the robot will pause or stop motion based on the settings. This command is only applicable to CRAF models. Other models will report an error when calling this command.

Required Parameters

| **Parameter Name** | **Type** | **Description**                                                                                                               |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------- |
| force   | double | Force threshold for triggering collision detection, shared by normal mode and reduced mode. Unit N, different models have different ranges as follows: CR5AF range: \[5, 150] CR10AF range: \[5, 300] CR20AF range: \[5, 500]      |
| torque  | double | Torque threshold for triggering collision detection, shared by normal mode and reduced mode. Unit N/m, different models have different ranges as follows: CR5AF range: \[0.5, 15] CR10AF range: \[0.5, 30] CR20AF range: \[0.5, 50] |

Return

ErrorID,\{},SetFCCollision(force,torque);

Example

SetFCCollision(50, 10)

When the collision force at the robot end exceeds 50N or the collision torque exceeds 10N/m, the robot will pause or stop motion based on the settings.

FCCollisionSwitch

Prototype

FCCollisionSwitch(switch)

Description

Enable/disable the force sensor collision detection switch. This command is only applicable to CRAF models. Other models will report an error when calling this command.

Required Parameters

| **Parameter Name** | **Type** | **Description**                                                |
| ------- | ------ | ------------------------------------------------------ |
| switch  | int    | Force sensor collision detection switch. Range: 0 or 1. 0 means disable force sensor collision detection function; 1 means enable force sensor collision detection function. |

Return

ErrorID,\{},FCCollisionSwitch(switch);

Example

FCCollisionSwitch(1)

Enable the force sensor collision detection function.

## 2.11 Conveyor Belt Commands

Functional Overview

The DOBOT conveyor belt tracking solution precisely captures the initial position of workpieces on the conveyor belt through photoelectric sensors/industrial cameras, and uses high-precision encoders to track the displacement changes of workpieces in real time. Combined with the conveyor belt tracking plugin, the robot control system can dynamically calculate the trajectory of the workpiece and control the robot to perform stable grasping, precision assembly, or continuous dispensing operations on workpieces on the conveyor belt.

Command List

| **Command**            | **Function**                   | **Command Type** |
| ---------------------- | -------------------------- | ------------ |
| CnvInit                | Enable conveyor belt                | Immediate Command |
| GetCnvObject           | Wait for specified workpiece to enter the conveyor belt pickup area     | Immediate Command |
| StartSyncCnv           | Enable conveyor belt tracking function            | Immediate Command |
| CnvMovL                | Execute conveyor belt tracking with linear trajectory interpolation     | Queue Command     |
| CnvMovC                | Execute conveyor belt tracking with circular trajectory interpolation     | Queue Command     |
| StopSyncCnv            | Stop conveyor belt tracking function            | Immediate Command |
| SetCnvPointOffset      | Set X, Y direction offsets in conveyor belt user coordinate system | Immediate Command |
| SetCnvTimeCompensation | Set compensation time               | Immediate Command |

CnvInit

Prototype

CnvInit(index)

Description

Enable the conveyor belt and send conveyor belt configuration information. Delete all queue information, start detecting and storing new queue information.

Required Parameters

| **Parameter Name** | **Type** | **Description**                              |
| ------- | ------ | ------------------------------------ |
| index   | int    | Conveyor belt number 1/2/3, the robot supports up to three conveyor belts. Setting to other values will report an error. |

Return

ErrorID,\{},CnvInit(index);

Example

CnvInit(1)

Enable conveyor belt 1 and send conveyor belt configuration information.

GetCnvObject

Prototype

GetCnvObject(objId)

Description

Wait for the specified workpiece to enter the conveyor belt pickup area (the area formed by the upper pickup boundary and lower pickup boundary).

Required Parameters

| **Parameter Name** | **Type** | **Description**                                                                                  |
| ------- | ------ | --------------------------------------------------------------------------------------- |
| objId   | int    | Workpiece type, range \[0, 15]. 0: Do not specify workpiece type, get the workpiece information that first entered the queue. For sensor triggering, objId defaults to 0. 1~15: Get the specified workpiece information that first entered the queue. |

Return

ErrorID,\{flag, objId, objframe},GetCnvObject(objId);

flag: The meaning of the value is as follows

0: No workpiece

1: Workpiece present

-1: Execution error, re-execute

-2: Unhandled error

-3: Not in tracking initialization state, need to execute CnvInit or StopSyncCnv command

objId: Workpiece type number, only meaningful when the required parameter objId is 0.

objframe: The result returns the current workpiece coordinate system (referenced to the robot base coordinate system). Even if the workpiece is not within the pickup boundary range, the workpiece coordinate system is still returned (mainly for real-time monitoring).

Example

GetCnvObject(0)

StartSyncCnv

Prototype

StartSyncCnv()

Description

Enable the conveyor belt tracking function.

Return

ErrorID,\{},StartSyncCnv();

CnvMovL

Prototype

CnvMovL(P,user, tool, a, v, cp|r)

Description

Based on the workpiece coordinate system, the robot moves linearly to the target position to perform conveyor belt tracking.

Required Parameters

| **Parameter Name** | **Type** | **Description**                                                                                  |
| ------- | ------ | --------------------------------------------------------------------------------------- |
| P       | string | Target position, supports joint variables or pose variables. Format is "joint = \{j1, j2, j3, j4, j5, j6}" or "pose = \{x, y, z, rx, ry, rz}". |

Optional Parameters

| **Parameter Name** | **Type** | **Description**                                                |
| ------- | ------ | ----------------------------------------------------- |
| user    | string | Format is "user=index", index is the calibrated user coordinate system index. Range: \[0,50].       |
| tool    | string | Format is "tool=index", index is the calibrated tool coordinate system index. Range: \[0,50].       |
| a       | string | Format is "a=value". Value represents the robot motion acceleration ratio when executing this command. Range: \[1,100]. |
| v       | string | Format is "v=value". Value represents the robot motion speed ratio when executing this command, range: \[1,100].  |
| cp      | string | Format is "cp=value". Value represents the smoothing transition ratio, mutually exclusive with r. Range: \[0,100].       |
| r       | string | Format is "r=value". Value represents the smoothing transition radius, mutually exclusive with cp, if both exist, r takes precedence. Unit: mm.     |

Return

ErrorID,\{flag},CnvMovL(P,user, tool, a, v, cp|r);

flag: Tracking result, the values are explained as follows

0: Execution successful

1: Tracking failed, workpiece type not detected

2: Tracking failed, workpiece type detected but not within pickup boundary range

3: Tracking failed, workpiece exceeded exit boundary

Example

CnvMovL(pose= \{x,y,z,rx,ry,rz},user = 1, tool = 0, a = 20, v = 50, cp = 100)

CnvMovC

Prototype

CnvMovC(P1,P2,user, tool, a, v, cp|r, mode)

Description

Based on the workpiece coordinate system, the robot moves from the current position through the intermediate point P1 to the target point P2 via circular motion, then performs conveyor belt tracking.

Required Parameters

| **Parameter Name** | **Type** | **Description**                                                                                     |
| ------- | ------ | ------------------------------------------------------------------------------------------ |
| P1      | string | Arc intermediate point, supports joint variables or pose variables. Format is "joint = \{j1, j2, j3, j4, j5, j6}" or "pose = \{x, y, z, rx, ry, rz}".  |
| P2      | string | Motion target point, supports joint variables or pose variables. Format is "joint = \{j1, j2, j3, j4, j5, j6}" or "pose = \{x, y, z, rx, ry, rz}". |

Optional Parameters

| **Parameter Name** | **Type** | **Description**                                                                                                                                                                                                                                                                                                   |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| user    | string | Format is "user=index", index is the calibrated user coordinate system index. Range: \[0,50].                                                                                                                                                                                                                                                          |
| tool    | string | Format is "tool=index", index is the calibrated tool coordinate system index. Range: \[0,50].                                                                                                                                                                                                                                                          |
| a       | string | Format is "a=value". Value represents the robot motion acceleration ratio when executing this command. Range: \[1,100].                                                                                                                                                                                                                                                    |
| v       | string | Format is "v=value". Value represents the robot motion speed ratio when executing this command. Range: \[1,100].                                                                                                                                                                                                                                                     |
| cp      | string | Format is "cp=value". Value represents the smoothing transition ratio, mutually exclusive with r. Range: \[0,100].                                                                                                                                                                                                                                                          |
| r       | string | Format is "r=value". Value represents the smoothing transition radius, mutually exclusive with cp, if both exist, r takes precedence. Unit: mm. Smoothing transition will change the robot motion trajectory and affect the timing of DO output, use with caution.                                                                                                                                                                                                                      |
| mode    | int    | Format is "mode=value". By setting attitude control parameters, the robot's attitude relative to the arc during interpolation is adaptively controlled to meet the usage requirements of different scenarios. Range: \[0, 2]. mode=0: Linear mode. Interpolate from current attitude to P2 target pose, ignoring P1 attitude. In this mode, only attitude changes less than 180° can be achieved. Suitable for occasions with no requirements on robot attitude. mode=1: Pass through intermediate point mode. Starting from current attitude, pass through intermediate point pose, interpolate to P2 target pose. Mainly used in welding applications. mode=2: Fixed mode. Starting from current attitude, TCP maintains a constant direction relative to the arc tangent, ignoring P1 and P2 attitudes. In this mode, the attitude rotation angle is consistent with the arc angle, and attitude changes greater than 180° can be achieved. Mainly used in applications such as dispensing and polishing. |

Note:

When set to mode=1 (pass through intermediate point mode), to ensure the uniformity of arc motion speed, when teaching the arc trajectory, try to ensure the intermediate point position is at the middle of the actual arc.

When set to mode=1 (pass through intermediate point mode), it is necessary to appropriately adjust the attitude of each point to ensure the attitude change from the starting point to the intermediate point is close to the attitude change from the intermediate point to the target point. Otherwise, the constructed attitude curve may exceed the robot's reachable range, and an error will be reported during operation.

Return

ErrorID,\{flag},CnvMovC(P1,P2,user, tool, a, v, cp|r, mode);

flag: Tracking result, the values are explained as follows

0: Execution successful

1: Tracking failed, workpiece type not detected

2: Tracking failed, workpiece type detected but not within pickup boundary range

3: Tracking failed, workpiece exceeded exit boundary

Example

CnvMovC(joint = \{1, 2, 3, 4, 5, 6},joint = \{7, 8, 9, 10, 11, 12},user = 1, tool = 0, a = 20, v = 50, cp = 100)

StopSyncCnv

Prototype

StopSyncCnv()

Description

Stop the conveyor belt tracking function. Other commands after this command will only continue executing after this command has finished running.

Must be used in conjunction with the StartSyncCnv() command. Other motion commands except CnvMovL and CnvMovC must not be called between StartSyncCnv() and StopSyncCnv(), otherwise an error will be reported.

Return

ErrorID,\{},StopSyncCnv();

SetCnvPointOffset

Prototype

SetCnvPointOffset(xOffset, yOffset)

Description

Set the X, Y direction offsets in the conveyor belt user coordinate system.

Required Parameters

| **Parameter Name** | **Type** | **Description**       |
| ------- | ------ | ------------- |
| xOffset | double | X-axis direction offset, unit mm. |
| yOffset | double | Y-axis direction offset, unit mm  |

Return

ErrorID,\{},SetCnvPointOffset(xOffset, yOffset);

Example

SetCnvPointOffset(10, 10)

SetCnvTimeCompensation

Prototype

SetCnvTimeCompensation(time)

Description

Set compensation time to compensate for workpiece grasping position offset caused by time delay from visual triggering.

Required Parameters

| **Parameter Name** | **Type** | **Description**    |
| ------- | ------ | ---------- |
| time    | int    | Compensation time, unit ms. |

Return

ErrorID,\{},SetCnvTimeCompensation(time);

Example

SetCnvTimeCompensation(100)

## 2.12 Point Reachability Check Commands

Functional Overview

This group of commands is used to check whether each point in the specified motion trajectory is reachable.

Command List

| **Command**     | **Function**            | **Command Type** |
| ------------ | --------------- | ------------ |
| CheckOddMovL | Check linear motion point reachability | Immediate Command |
| CheckOddMovJ | Check joint motion point reachability | Immediate Command |
| CheckOddMovC | Check arc motion point reachability | Immediate Command |

CheckOddMovL

Prototype

CheckOddMovL(P1,P2,user,tool,a,v,cp|r)

Description

Check the point reachability of linear motion. Point parameters only support joint variables (joint = \{j1, j2, j3, j4, j5, j6}).

This command can only be called when the robot arm is stationary.

Required Parameters

| **Parameter Name** | **Type** | **Description** |
| ------- | ------ | ------- |
| P1      | string | Linear motion start point. |
| P2      | string | Linear motion end point. |

Optional Parameters

| **Parameter Name** | **Type** | **Description**                         |
| ------- | ------ | ------------------------------- |
| user    | int    | User coordinate system, effective for all points in the command.              |
| tool    | int    | Tool coordinate system, effective for all points in the command               |
| a       | int    | Robot motion acceleration ratio when executing this command. Range: (0,100] |
| v       | int    | Robot motion speed ratio when executing this command. Range: (0,100]  |
| cp      | int    | Smoothing transition ratio. Range: \[0,100]            |
| r       | int    | Smoothing transition radius, mutually exclusive with cp, if both exist, r takes precedence. Unit: mm    |

Return

ErrorID,\{result},CheckOddMovL(P1,P2,user,tool,a,v,cp|r);

result is the check result.

0: All trajectory points are reachable.

-1: Unable to perform check. Usually because the robot arm is in motion when this command is called.

For other return values, see the point reachability detection general error codes.

Example

CheckOddMovL(joint = \{0, 0, 90, 0, 0, 0},joint = \{90, 30, 0, 0, 0, 0})

Check the point reachability of linear motion from \{0, 0, 90, 0, 0, 0} to \{90, 30, 0, 0, 0, 0}.

CheckOddMovJ

Prototype

CheckOddMovJ(P1,P2,a,v,cp)

Description

Check the point reachability of joint motion. Point parameters only support joint variables (joint = \{j1, j2, j3, j4, j5, j6}).

This command can only be called when the robot arm is stationary.

Required Parameters

| **Parameter Name** | **Type** | **Description** |
| ------- | ------ | ------- |
| P1      | string | Joint motion start point. |
| P2      | string | Joint motion end point. |

Optional Parameters

| **Parameter Name** | **Type** | **Description**                         |
| ------- | ------ | ------------------------------- |
| a       | int    | Robot motion acceleration ratio when executing this command. Range: (0,100] |
| v       | int    | Robot motion speed ratio when executing this command. Range: (0,100]  |
| cp      | int    | Smoothing transition ratio. Range: \[0,100]            |

Return

ErrorID,\{result},CheckOddMovJ(P1,P2,a,v,cp);

result is the check result.

0: All trajectory points are reachable.

-1: Unable to perform check. Usually because the robot arm is in motion when this command is called.

For other return values, see the point reachability detection general error codes.

Example

CheckOddMovJ(joint = \{0, 0, 90, 0, 0, 0},joint = \{90, 30, 0, 0, 0, 0})

Check the point reachability of joint motion from \{0, 0, 90, 0, 0, 0} to \{90, 30, 0, 0, 0, 0}.

CheckOddMovC

Prototype

CheckOddMovC(P1,P2,P3,user,tool,a,v,cp|r)

Description

Check the point reachability of arc motion. Point parameters only support joint variables (joint = \{j1, j2, j3, j4, j5, j6}).

This command can only be called when the robot arm is stationary.

Required Parameters

| **Parameter Name** | **Type** | **Description**  |
| ------- | ------ | -------- |
| P1      | string | Arc motion start point.  |
| P2      | string | Arc motion intermediate point. |
| P3      | string | Arc motion end point.  |

Optional Parameters

| **Parameter Name** | **Type** | **Description**                         |
| ------- | ------ | ------------------------------- |
| user    | int    | User coordinate system, effective for all points in the command.              |
| tool    | int    | Tool coordinate system, effective for all points in the command               |
| a       | int    | Robot motion acceleration ratio when executing this command. Range: (0,100] |
| v       | int    | Robot motion speed ratio when executing this command. Range: (0,100]  |
| cp      | int    | Smoothing transition ratio. Range: \[0,100]            |
| r       | int    | Smoothing transition radius, mutually exclusive with cp, if both exist, r takes precedence. Unit: mm    |

Return

ErrorID,\{result},CheckOddMovC(P1,P2,P3,user,tool,a,v,cp|r);

result is the check result.

0: All trajectory points are reachable.

-1: Unable to perform check. Usually because the robot arm is in motion when this command is called.

For other return values, see the point reachability detection general error codes.

Example

CheckOddMovC(joint = \{0, 0, 90, 0, 0, 0},joint = \{60, 30, 0, 0, 0, 0},joint = \{90, 30, 0, 0, 0, 0})

Check the point reachability of arc motion from \{0, 0, 90, 0, 0, 0} => \{60, 30, 0, 0, 0, 0} => \{90, 30, 0, 0, 0, 0}.

Point Reachability Detection General Error Codes

16: Trajectory contains points near shoulder singularity

17: Trajectory contains unreachable points

18: Trajectory contains points that will trigger joint limits

19: Arc motion has duplicate points.

26: Trajectory contains points near wrist singularity

27: Trajectory contains points near elbow singularity

29: Velocity parameter error