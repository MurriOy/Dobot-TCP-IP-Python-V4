# Copyright (c) 2026 Dobot
# Licensed under the MIT License

"""Robot Control module - Status query, kinematics calculation, reachability check, robot control"""

from typing import Tuple, Sequence
from ..core.connection import DobotConnection


class RobotControl:
    """Robot control module - Status query, kinematics calculation, reachability check, logging, script control"""

    def __init__(self, connection: DobotConnection):
        self.connection = connection

    def _send_cmd(self, command: str) -> str:
        """Send command and receive response"""
        return self.connection.send_receive_text(command)

    # ==================== Control Mode and Power ====================

    def RequestControl(self) -> str:
        """
        RequestControl switches the device control mode to TCP mode (immediate command)
        
        Notes:
        - Other TCP commands can only be executed in TCP mode
        - TCP mode can only be switched when the robot is unpowered or disabled (and not paused or brake released)
        - After calling this interface, EnableRobot, motion commands, etc. can be executed
        
        Returns:
            str: ErrorID,{},RequestControl();
        """
        return self._send_cmd("RequestControl()")

    def PowerOn(self) -> str:
        """PowerOn powers on the robot (immediate command)"""
        return self._send_cmd("PowerOn()")

    def EnableRobot(self, load: float = 0.0, **kwargs) -> str:
        """
        EnableRobot enables the robot (immediate command)

        Prototype: EnableRobot(load,centerX,centerY,centerZ,isCheck)

        Args:
            load: Payload weight (kg)
            centerX: Payload center of gravity X coordinate (mm)
            centerY: Payload center of gravity Y coordinate (mm)
            centerZ: Payload center of gravity Z coordinate (mm)
            isCheck: Whether to check payload (0=don't check, 1=check)
        """
        if load == 0.0:
            cmd = "EnableRobot()"
        elif 'centerX' not in kwargs:
            cmd = f"EnableRobot({load:.6f})"
        else:
            cx = kwargs.get('centerX', 0.0)
            cy = kwargs.get('centerY', 0.0)
            cz = kwargs.get('centerZ', 0.0)
            check = kwargs.get('isCheck', 0)
            cmd = f"EnableRobot({load:.6f},{cx:.6f},{cy:.6f},{cz:.6f},{check})"
        return self._send_cmd(cmd)

    def DisableRobot(self) -> str:
        """DisableRobot disables the robot (immediate command)"""
        return self._send_cmd("DisableRobot()")

    def ClearError(self) -> str:
        """ClearError clears robot alarms (immediate command)"""
        return self._send_cmd("ClearError()")

    # ==================== Motion Control ====================

    def RunScript(self, script_name: str) -> str:
        """
        RunScript runs the specified project (immediate command)
        
        Args:
            script_name: Script file name        """
        return self._send_cmd(f"RunScript(\"{script_name}\")")

    def Stop(self) -> str:
        """Stop stops motion (or running project) (immediate command)"""
        return self._send_cmd("Stop()")

    def Pause(self) -> str:
        """Pause pauses motion (or running project) (immediate command)"""
        return self._send_cmd("Pause()")

    def Continue(self) -> str:
        """Continue continues motion (or paused project) (immediate command)"""
        return self._send_cmd("Continue()")

    def EmergencyStop(self, mode: int) -> str:
        """
        EmergencyStop emergency stops the robot (immediate command)
        
        Args:
            mode: Emergency stop operation mode. 1 means press emergency stop, 0 means release emergency stop.
        """
        if mode not in [0, 1]:
            raise ValueError("mode must be 0 or 1")
        return self._send_cmd(f"EmergencyStop({mode})")

    # ==================== Brake and Drag ====================

    def BrakeControl(self, axis_id: int, value: int) -> str:
        """
        BrakeControl controls the brake of specified joint (immediate command)        
        Args:
            axis_id: Joint number (1-6)
            value: 0-brake on, 1-brake off
        """
        if not 1 <= axis_id <= 6:
            raise ValueError("Joint number must be between 1-6")
        if value not in [0, 1]:
            raise ValueError("value must be 0 or 1")
        return self._send_cmd(f"BrakeControl({axis_id},{value})")

    def StartDrag(self) -> str:
        """StartDrag robot enters joint drag mode (immediate command)"""
        return self._send_cmd("StartDrag()")

    def StopDrag(self) -> str:
        """StopDrag robot exits drag mode (immediate command)"""
        return self._send_cmd("StopDrag()")

    def DragSensitivity(self, index: int, value: int) -> str:
        """
        DragSensitivity sets drag sensitivity (immediate command)
        
        Args:
            index: Axis number, range: [0,6]. 0 means all axes set to the same sensitivity. 1~6 respectively set J1~J6 axis sensitivity.
            value: Drag sensitivity, smaller value means greater resistance during drag. Range: [1, 90].
        """
        if not 0 <= index <= 6:
            raise ValueError("Axis number must be between 0-6")
        if not 1 <= value <= 90:
            raise ValueError("Drag sensitivity must be between 1-90")
        return self._send_cmd(f"DragSensitivity({index},{value})")

    # ==================== Speed and Acceleration Settings ====================

    def SpeedFactor(self, factor: int) -> str:
        """
        SpeedFactor sets global speed ratio (immediate command)
        
        Args:
            factor: Speed ratio (1-100)
        """
        if not 1 <= factor <= 100:
            raise ValueError("Speed ratio must be between 1-100")
        return self._send_cmd(f"SpeedFactor({factor})")

    def AccJ(self, acc: int) -> str:
        """
        AccJ sets joint motion acceleration ratio (immediate command)
        
        Args:
            acc: Acceleration ratio (1-100)
        """
        if not 1 <= acc <= 100:
            raise ValueError("Acceleration ratio must be between 1-100")
        return self._send_cmd(f"AccJ({acc})")

    def AccL(self, acc: int) -> str:
        """
        AccL sets linear and arc motion acceleration ratio (immediate command)
        
        Args:
            acc: Acceleration ratio (1-100)
        """
        if not 1 <= acc <= 100:
            raise ValueError("Acceleration ratio must be between 0-100")
        return self._send_cmd(f"AccL({acc})")

    def VelJ(self, vel: int) -> str:
        """
        VelJ sets joint motion speed ratio (immediate command)
        
        Args:
            vel: Speed ratio (1-100)
        """
        if not 1 <= vel <= 100:
            raise ValueError("Speed ratio must be between 0-100")
        return self._send_cmd(f"VelJ({vel})")

    def VelL(self, vel: int) -> str:
        """
        VelL sets linear and arc motion speed ratio (immediate command)
        
        Args:
            vel: Speed ratio (1-100)
        """
        if not 1 <= vel <= 100:
            raise ValueError("Speed ratio must be between 0-100")
        return self._send_cmd(f"VelL({vel})")

    def CP(self, value: int) -> str:
        """
        CP sets smooth transition ratio (immediate command)
        
        Args:
            value: Smooth transition ratio (0-100)
        """
        if not 0 <= value <= 100:
            raise ValueError("Smooth transition ratio must be between 0-100")
        return self._send_cmd(f"CP({value})")

    # ==================== Coordinate System Settings ====================

    def User(self, index: int) -> str:
        """
        User sets global user coordinate system (queue command)        
        Args:
            index: User coordinate system number (0-50)
        """
        if not 0 <= index <= 50:
            raise ValueError("User coordinate system number must be between 0-50")
        return self._send_cmd(f"User({index})")

    def SetUser(self, index: int, pose: Sequence[float], type: int = None) -> str:
        """
        SetUser modifies the specified user coordinate system (immediate command)
        
        Args:
            index: User coordinate system number (1-50)
            pose: 6 coordinate parameters [x,y,z,rx,ry,rz]
            type: Whether to make coordinate system changes take effect globally. 0: The coordinate system modified by this command only takes effect during the current project run. 1: The coordinate system modified by this command will be saved by the controller.
        """
        if not 1 <= index <= 50:
            raise ValueError("User coordinate system number must be between 1-50")
        if len(pose) != 6:
            raise ValueError("pose requires 6 parameters")
        pose_str = "{" + ",".join([f"{v:.6f}" for v in pose]) + "}"
        if type is not None:
            if type not in [0, 1]:
                raise ValueError("type must be 0 or 1")
            return self._send_cmd(f"SetUser({index},{pose_str},{type})")
        return self._send_cmd(f"SetUser({index},{pose_str})")

    def CalcUser(self, index: int, matrix_direction: int, offset: Sequence[float]) -> str:
        """
        CalcUser calculates user coordinate system (immediate command)
        Args:
            index: User coordinate system number (0-50)
            matrix_direction: Calculation direction (1-left multiply, coordinate system rotates along base coordinate system; 0-right multiply, coordinate system rotates along itself)
            offset: Offset values [x,y,z,rx,ry,rz]
        """
        if not 0 <= index <= 50:
            raise ValueError("User coordinate system number must be between 0-50")
        if matrix_direction not in [0, 1]:
            raise ValueError("matrix_direction must be 0 or 1")
        if len(offset) != 6:
            raise ValueError("offset requires 6 parameters")
        offset_str = "{" + ",".join([f"{v:.6f}" for v in offset]) + "}"
        return self._send_cmd(f"CalcUser({index},{matrix_direction},{offset_str})")

    def Tool(self, index: int) -> str:
        """
        Tool sets global tool coordinate system (queue command)        
        Args:
            index: Tool coordinate system number (0-50)
        """
        if not 0 <= index <= 50:
            raise ValueError("Tool coordinate system number must be between 0-50")
        return self._send_cmd(f"Tool({index})")

    def SetTool(self, index: int, pose: Sequence[float], type: int = None) -> str:
        """
        SetTool modifies the specified tool coordinate system (immediate command)
        
        Args:
            index: Tool coordinate system number (1-50)
            pose: 6 coordinate parameters [x,y,z,rx,ry,rz]
            type: Whether to make coordinate system changes take effect globally. 0: The coordinate system modified by this command only takes effect during the current project run. 1: The coordinate system modified by this command will be saved by the controller.
        """
        if not 1 <= index <= 50:
            raise ValueError("Tool coordinate system number must be between 1-50")
        if len(pose) != 6:
            raise ValueError("pose requires 6 parameters")
        pose_str = "{" + ",".join([f"{v:.6f}" for v in pose]) + "}"
        if type is not None:
            if type not in [0, 1]:
                raise ValueError("type must be 0 or 1")
            return self._send_cmd(f"SetTool({index},{pose_str},{type})")
        return self._send_cmd(f"SetTool({index},{pose_str})")

    def CalcTool(self, index: int, matrix_direction: int, offset: Sequence[float]) -> str:
        """
        CalcTool calculates tool coordinate system (immediate command)
        Args:
            index: Tool coordinate system number (0-50)
            matrix_direction: Calculation direction (1-left multiply, coordinate system rotates along flange coordinate system; 0-right multiply, coordinate system rotates along itself)
            offset: Offset values [x,y,z,rx,ry,rz]
        """
        if not 0 <= index <= 50:
            raise ValueError("Tool coordinate system number must be between 0-50")
        if matrix_direction not in [0, 1]:
            raise ValueError("matrix_direction must be 0 or 1")
        if len(offset) != 6:
            raise ValueError("offset requires 6 parameters")
        offset_str = "{" + ",".join([f"{v:.6f}" for v in offset]) + "}"
        return self._send_cmd(f"CalcTool({index},{matrix_direction},{offset_str})")

    # ==================== Payload Settings ====================

    def SetPayload(self, load_or_name, *args, **kwargs) -> str:
        """
        SetPayload sets the robot end-effector payload (queue command)

        Supports two calling methods (exactly as documented):
        Method 1: SetPayload(load, x, y, z)
        Method 2: SetPayload(name)

        Also maintains backward compatibility: SetPayload(load, center=[x,y,z])

        Args:
            load_or_name:
                - float: Payload weight (kg) -> Method 1
                - str: Preset payload parameter group name -> Method 2
            x (optional, float): End-effector payload X-axis eccentric coordinate (mm)
            y (optional, float): End-effector payload Y-axis eccentric coordinate (mm)
            z (optional, float): End-effector payload Z-axis eccentric coordinate (mm)
            center (optional, Sequence[float]): Backward compatible, payload center of gravity [x,y,z]
            preset_name (optional, str): Backward compatible, if provided, the previous two are ignored, equivalent to Method 2
        """
        center = kwargs.get('center', None)
        preset_name = kwargs.get('preset_name', None)

        if isinstance(load_or_name, str):
            return self._send_cmd(f'SetPayload("{load_or_name}")')

        if preset_name is not None:
            return self._send_cmd(f'SetPayload("{preset_name}")')

        load = float(load_or_name)

        x = y = z = None
        if len(args) == 3:
            x, y, z = args
        elif len(args) == 1 and isinstance(args[0], (list, tuple)):
            if len(args[0]) != 3:
                raise ValueError("center list requires 3 parameters [x,y,z]")
            x, y, z = args[0]
        elif center is not None:
            if len(center) != 3:
                raise ValueError("center requires 3 parameters [x,y,z]")
            x, y, z = center
        elif len(args) != 0:
            raise ValueError("Positional arguments only support SetPayload(load, x, y, z) three-parameter form or SetPayload(load, [x,y,z]) list form")

        if x is not None and y is not None and z is not None:
            return self._send_cmd(f"SetPayload({load:.6f},{float(x):.6f},{float(y):.6f},{float(z):.6f})")
        return self._send_cmd(f"SetPayload({load:.6f})")

    # ==================== Collision Detection Settings ====================

    def SetCollisionLevel(self, level: int) -> str:
        """
        SetCollisionLevel sets collision detection level (queue command)        
        Args:
            level: Collision detection level (0-5), 0 disables collision detection, 1~5 higher numbers mean higher sensitivity
        """
        if not 0 <= level <= 5:
            raise ValueError("Collision detection level must be between 0-5")
        return self._send_cmd(f"SetCollisionLevel({level})")

    def SetBackDistance(self, distance: float) -> str:
        """
        SetBackDistance sets collision retreat distance (queue command)
        
        Args:
            distance: Collision retreat distance (mm), range [0, 50]
        """
        if not 0 <= distance <= 50:
            raise ValueError("distance must be between 0 and 50 (unit: mm)")
        return self._send_cmd(f"SetBackDistance({distance:.6f})")

    def SetPostCollisionMode(self, mode: int) -> str:
        """
        SetPostCollisionMode sets post-collision handling mode (queue command)
        Args:
            mode: Post-collision handling mode
                  0: Disable and stop motion (V4.6.6 official documentation definition)
                  1: Pause motion (V4.6.6 official documentation definition)
                  2: Ignore collision and continue motion (Extended mode, partial firmware support, not defined in V4.6.6 official documentation)
        """
        if mode not in [0, 1, 2]:
            raise ValueError("Post-collision handling mode must be 0, 1, or 2")
        return self._send_cmd(f"SetPostCollisionMode({mode})")

    # ==================== Safety Skin and Safety Zone ====================

    def EnableSafeSkin(self, status: int) -> str:
        """
        EnableSafeSkin enables or disables the safety skin function (queue command)
        
        Args:
            status: 0-disable, 1-enable        """
        if status not in [0, 1]:
            raise ValueError("Status must be 0 or 1")
        return self._send_cmd(f"EnableSafeSkin({status})")

    def SetSafeSkin(self, part: int, sensitivity: int) -> str:
        """
        SetSafeSkin sets the sensitivity of each part of the safety skin (queue command)
        
        Args:
            part: Safety skin part number. 3=forearm, 4~6=J4~J6
            sensitivity: Sensitivity level [0, 3]. 0=off, 1=low, 2=medium, 3=high
        """
        if not (part == 3 or 4 <= part <= 6):
            raise ValueError("part can only be 3(forearm) or 4~6 (J4~J6)")
        if not 0 <= sensitivity <= 3:
            raise ValueError("sensitivity must be between 0 and 3")
        return self._send_cmd(f"SetSafeSkin({part},{sensitivity})")

    def SetSafeWallEnable(self, index: int, status: int) -> str:
        """
        SetSafeWallEnable enables or disables the specified safe wall (queue command)
        
        Args:
            index: Safe wall number            status: 0-disable, 1-enable        """
        if status not in [0, 1]:
            raise ValueError("Status must be 0 or 1")
        return self._send_cmd(f"SetSafeWallEnable({index},{status})")

    def SetWorkZoneEnable(self, index: int, status: int) -> str:
        """
        SetWorkZoneEnable enables or disables the specified safety zone (queue command)        
        Args:
            index: Safety zone number
            status: 0-disable, 1-enable        """
        if status not in [0, 1]:
            raise ValueError("Status must be 0 or 1")
        return self._send_cmd(f"SetWorkZoneEnable({index},{status})")

    # ==================== Status Query ====================

    def RobotMode(self) -> str:
        """RobotMode gets the robot current status (immediate command)"""
        return self._send_cmd("RobotMode()")

    def GetPose(self, user: int = None, tool: int = None) -> str:
        """
        GetPose gets the robot current pose in Cartesian coordinates under the specified coordinate system (immediate command)
        
        Args:
            user: User coordinate system index (0-50)
            tool: Tool coordinate system index (0-50)
        """
        has_coord = user is not None or tool is not None
        if has_coord and (user is None or tool is None):
            raise ValueError("user and tool parameters must be set together or not set at all")

        if has_coord:
            if not (0 <= user <= 50):
                raise ValueError("user must be between 0-50")
            if not (0 <= tool <= 50):
                raise ValueError("tool must be between 0-50")
            return self._send_cmd(f"GetPose(user={user},tool={tool})")
        else:
            return self._send_cmd("GetPose()")

    def GetAngle(self) -> str:
        """GetAngle gets the robot current joint coordinates (immediate command)"""
        return self._send_cmd("GetAngle()")

    def GetErrorID(self) -> str:
        """GetErrorID gets the robot current error code (immediate command)"""
        return self._send_cmd("GetErrorID()")

    def GetScrName(self) -> str:
        """GetScrName gets the name of the script currently running on the robot (immediate command)"""
        return self._send_cmd("GetScrName()")

    # ==================== Kinematics Calculation ====================

    def PositiveKin(self, joints: Sequence[float], user: int = -1, tool: int = -1) -> str:
        """
        PositiveKin performs forward kinematics calculation (immediate command)
        
        Args:
            joints: 6 joint angles [j1,j2,j3,j4,j5,j6] (degrees)
            user: User coordinate system number. Default is -1, meaning current user coordinate system.
            tool: Tool coordinate system number. Default is -1, meaning current tool coordinate system.
        """
        if len(joints) != 6:
            raise ValueError("Requires 6 joint angles")
        joint_str = ",".join([f"{j:.6f}" for j in joints])
        if user != -1 and tool != -1:
            return self._send_cmd(f"PositiveKin({joint_str},user={user},tool={tool})")
        return self._send_cmd(f"PositiveKin({joint_str})")

    def InverseKin(self, pose: Sequence[float], use_joint_near: int = 0, joint_near: Sequence[float] = None, user: int = -1, tool: int = -1) -> str:
        """
        InverseKin performs inverse kinematics calculation (immediate command)
        
        Args:
            pose: 6 Cartesian coordinates [x,y,z,rx,ry,rz]
            use_joint_near: Whether to use joint proximity constraint. 0: Don't use. 1: Use.
            joint_near: Joint proximity reference values [j1,j2,j3,j4,j5,j6]. Takes effect when useJointNear is 1.
            user: User coordinate system number. Default is -1, meaning current user coordinate system.
            tool: Tool coordinate system number. Default is -1, meaning current tool coordinate system.
        """
        if len(pose) != 6:
            raise ValueError("Requires 6 pose parameters")
        pose_str = ",".join([f"{p:.6f}" for p in pose])
        params = [pose_str]
        if use_joint_near != 0:
            params.append(f"useJointNear={use_joint_near}")
            if joint_near is not None:
                if len(joint_near) != 6:
                    raise ValueError("joint_near requires 6 joint angles")
                joint_near_str = "jointNear={" + ",".join([f"{j:.6f}" for j in joint_near]) + "}"
                params.append(joint_near_str)
        if user != -1:
            params.append(f"user={user}")
        if tool != -1:
            params.append(f"tool={tool}")
        return self._send_cmd(f"InverseKin({','.join(params)})")

    # ==================== Reachability Check ====================

    def CheckOddMovL(self, p1: Sequence[float], p2: Sequence[float],
                     point_type: str = "joint",
                     user: int = -1, tool: int = -1,
                     a: float = -1, v: float = -1,
                     cp: float = None, r: float = None) -> str:
        """
        CheckOddMovL checks point reachability for linear motion (immediate command)
        
        Args:
            p1: Start point [j1,j2,j3,j4,j5,j6] or [x,y,z,rx,ry,rz]
            p2: End point [j1,j2,j3,j4,j5,j6] or [x,y,z,rx,ry,rz]
            point_type: Point type "joint" or "pose" (Cartesian)
            user: User coordinate system number. -1 means not specified
            tool: Tool coordinate system number. -1 means not specified
            a: Acceleration. -1 means use default value
            v: Speed. -1 means use default value
            cp: Continuity (mutually exclusive with r)
            r: Blending radius (mutually exclusive with cp, unit: mm)
        """
        if len(p1) != 6:
            raise ValueError("p1 requires 6 values")
        if len(p2) != 6:
            raise ValueError("p2 requires 6 values")
        if point_type not in ("joint", "pose"):
            raise ValueError("point_type can only be 'joint' or 'pose'")
        p_values1 = ",".join([f"{j:.6f}" for j in p1])
        p_values2 = ",".join([f"{j:.6f}" for j in p2])
        params = [f"{point_type}={{{p_values1}}}", f"{point_type}={{{p_values2}}}"]
        if user != -1:
            params.append(f"user={user}")
        if tool != -1:
            params.append(f"tool={tool}")
        if a != -1:
            params.append(f"a={a:.6f}")
        if v != -1:
            params.append(f"v={v:.6f}")
        if cp is not None:
            params.append(f"cp={cp:.6f}")
        elif r is not None:
            params.append(f"r={r:.6f}")
        return self._send_cmd(f"CheckOddMovL({','.join(params)})")

    def CheckOddMovJ(self, p1: Sequence[float], p2: Sequence[float],
                     point_type: str = "joint",
                     a: float = -1, v: float = -1,
                     cp: float = None) -> str:
        """
        CheckOddMovJ checks point reachability for joint motion (immediate command)
        
        Args:
            p1: Start point [j1,j2,j3,j4,j5,j6] or [x,y,z,rx,ry,rz]
            p2: End point [j1,j2,j3,j4,j5,j6] or [x,y,z,rx,ry,rz]
            point_type: Point type "joint" or "pose" (Cartesian)
            a: Acceleration. -1 means use default value
            v: Speed. -1 means use default value
            cp: Continuity
        """
        if len(p1) != 6:
            raise ValueError("p1 requires 6 values")
        if len(p2) != 6:
            raise ValueError("p2 requires 6 values")
        if point_type not in ("joint", "pose"):
            raise ValueError("point_type can only be 'joint' or 'pose'")
        p_values1 = ",".join([f"{j:.6f}" for j in p1])
        p_values2 = ",".join([f"{j:.6f}" for j in p2])
        params = [f"{point_type}={{{p_values1}}}", f"{point_type}={{{p_values2}}}"]
        if a != -1:
            params.append(f"a={a:.6f}")
        if v != -1:
            params.append(f"v={v:.6f}")
        if cp is not None:
            params.append(f"cp={cp:.6f}")
        return self._send_cmd(f"CheckOddMovJ({','.join(params)})")

    def CheckOddMovC(self, p1: Sequence[float], p2: Sequence[float], p3: Sequence[float],
                     point_type: str = "joint",
                     user: int = -1, tool: int = -1,
                     a: float = -1, v: float = -1,
                     cp: float = None, r: float = None) -> str:
        """
        CheckOddMovC checks point reachability for arc motion (immediate command)
        
        Args:
            p1: Start point [j1,j2,j3,j4,j5,j6] or [x,y,z,rx,ry,rz]
            p2: Middle point [j1,j2,j3,j4,j5,j6] or [x,y,z,rx,ry,rz]
            p3: End point [j1,j2,j3,j4,j5,j6] or [x,y,z,rx,ry,rz]
            point_type: Point type "joint" or "pose" (Cartesian)
            user: User coordinate system number. -1 means not specified
            tool: Tool coordinate system number. -1 means not specified
            a: Acceleration. -1 means use default value
            v: Speed. -1 means use default value
            cp: Continuity (mutually exclusive with r)
            r: Blending radius (mutually exclusive with cp, unit: mm)
        """
        if len(p1) != 6:
            raise ValueError("p1 requires 6 values")
        if len(p2) != 6:
            raise ValueError("p2 requires 6 values")
        if len(p3) != 6:
            raise ValueError("p3 requires 6 values")
        if point_type not in ("joint", "pose"):
            raise ValueError("point_type can only be 'joint' or 'pose'")
        p_values1 = ",".join([f"{j:.6f}" for j in p1])
        p_values2 = ",".join([f"{j:.6f}" for j in p2])
        p_values3 = ",".join([f"{j:.6f}" for j in p3])
        params = [f"{point_type}={{{p_values1}}}",
                  f"{point_type}={{{p_values2}}}",
                  f"{point_type}={{{p_values3}}}"]
        if user != -1:
            params.append(f"user={user}")
        if tool != -1:
            params.append(f"tool={tool}")
        if a != -1:
            params.append(f"a={a:.6f}")
        if v != -1:
            params.append(f"v={v:.6f}")
        if cp is not None:
            params.append(f"cp={cp:.6f}")
        elif r is not None:
            params.append(f"r={r:.6f}")
        return self._send_cmd(f"CheckOddMovC({','.join(params)})")

    # ==================== Tray Related ====================

    def CreateTray(self, name: str, dimensions: Sequence[int],
                    points: list) -> str:
        """
        CreateTray creates a tray (immediate command)
        Supports 1D, 2D, and 3D trays.

        Prototype (exactly as documented):
        CreateTray(Trayname, {Count}, {P1},{P2}) -- 1D tray
        CreateTray(Trayname, {row,col}, {P1},{P2},{P3},{P4}) -- 2D tray
        CreateTray(Trayname, {row,col,layer}, {P1},{P2},{P3},{P4},{P5},{P6},{P7},{P8}) -- 3D tray

        Args:
            name: Tray name (max 32 bytes string, no pure numbers or pure spaces)
            dimensions: Dimension parameters
                - 1D: [count] Number of points [2,50]
                - 2D: [row, col] Number of rows and columns
                - 3D: [row, col, layer] Number of rows, columns, and layers
            points: Endpoint list, each endpoint is [x,y,z,rx,ry,rz] format, each point as independent parameter
                - 1D: 2 endpoints [p1, p2]
                - 2D: 4 endpoints [p1, p2, p3, p4]
                - 3D: 8 endpoints [p1, p2, p3, p4, p5, p6, p7, p8]
        """
        dims = ",".join([str(d) for d in dimensions])
        point_strs = []
        for p in points:
            if len(p) != 6:
                raise ValueError(f"Each point requires 6 values [x,y,z,rx,ry,rz], currently passed {len(p)}")
            point_strs.append("{pose = {" + ",".join([f"{v:.6f}" for v in p]) + "}}")
        cmd = f"CreateTray({name},{{{dims}}}," + ",".join(point_strs) + ")"
        return self._send_cmd(cmd)

    def GetTrayPoint(self, trayname: str, index: int) -> str:
        """
        GetTrayPoint gets tray point (immediate command)
        
        Args:
            trayname: Tray name (string, corresponds to the name used when creating with CreateTray)
            index: Tray point index (starting from which point, 1-based)
        """
        if not trayname or not trayname.strip():
            raise ValueError("trayname cannot be empty")
        if index < 1:
            raise ValueError("index must be greater than or equal to 1")
        return self._send_cmd(f"GetTrayPoint({trayname},{index})")

    # ==================== Log Export ====================

    def LogExportUSB(self, log_range: int = None) -> str:
        """
        LogExportUSB exports robot logs to USB drive (immediate command)

        Args:
            log_range: Log export range.
                0: Export logs/all and logs/user
                1: Export all contents of logs folder
        """
        if log_range is not None:
            if log_range not in [0, 1]:
                raise ValueError("log_range must be 0 or 1")
            return self._send_cmd(f"LogExportUSB({log_range})")
        return self._send_cmd("LogExportUSB()")

    def GetExportStatus(self) -> str:
        """GetExportStatus gets log export status (immediate command)"""
        return self._send_cmd("GetExportStatus()")