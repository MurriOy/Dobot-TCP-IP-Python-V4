# Copyright (c) 2026 Dobot
# Licensed under the MIT License

"""Plugin related module - force control, conveyor and other extended functions"""

from typing import Sequence
from ..core.connection import DobotConnection
from .motion import CoordinateType


class Plugins:
    """Plugin module - handling force control, conveyor and other extended functions"""

    def __init__(self, connection: DobotConnection):
        self.connection = connection

    def _send_cmd(self, command: str) -> str:
        """Send command and receive response"""
        return self.connection.send_receive_text(command)

    # ==================== Force Sensor Basic Commands ====================

    def EnableFTSensor(self, status: int) -> str:
        """
        EnableFTSensor enable/disable force sensor (immediate command)
        
        Args:
            status: 0-disable, 1-enable
        """
        if status not in [0, 1]:
            raise ValueError("status must be 0 or 1")
        return self._send_cmd(f"EnableFTSensor({status})")

    def SixForceHome(self) -> str:
        """SixForceHome force sensor homing (immediate command)"""
        return self._send_cmd("SixForceHome()")

    def GetForce(self, tool: int = -1) -> str:
        """
        GetForce get force sensor value (immediate command)
        
        Args:
            tool: Tool coordinate system number, range [0, 50], -1 means use current tool coordinate system
        """
        if tool == -1:
            return self._send_cmd("GetForce()")
        if not (0 <= tool <= 50):
            raise ValueError("tool parameter must be in [0, 50]")
        return self._send_cmd(f"GetForce({tool})")

    # ==================== Force Control Drag Mode ====================

    def ForceDriveMode(self, direction: Sequence[int], user: int = -1) -> str:
        """
        ForceDriveMode specify draggable directions and enter force control drag mode (immediate command)
        
        Args:
            direction: Drag switches for 6 directions [x,y,z,rx,ry,rz], 0 means not draggable in that direction, 1 means draggable
            user: User coordinate system number, range [0, 50], if not specified, user coordinate system is not referenced
        """
        if len(direction) != 6:
            raise ValueError("direction requires 6 parameters")
        for d in direction:
            if d not in [0, 1]:
                raise ValueError("direction parameter value must be 0 or 1")
        if user != -1 and not (0 <= user <= 50):
            raise ValueError("user parameter must be in [0, 50]")
        direction_str = "{" + ",".join([f"{v}" for v in direction]) + "}"
        if user == -1:
            return self._send_cmd(f"ForceDriveMode({direction_str})")
        return self._send_cmd(f"ForceDriveMode({direction_str},{user})")

    def ForceDriveSpeed(self, speed: int) -> str:
        """
        ForceDriveSpeed set force control drag speed (immediate command)
        
        Args:
            speed: Force control drag speed ratio, range [1, 100]
        """
        if not 1 <= speed <= 100:
            raise ValueError("speed ratio must be in 1-100")
        return self._send_cmd(f"ForceDriveSpeed({speed})")

    # ==================== Force Control Mode Parameter Settings ====================

    def FCForceMode(self, direction: Sequence[int], force: Sequence[float],
                      reference: int = 0, user: int = -1, tool: int = -1) -> str:
        """
        FCForceMode enable force control with user-specified parameters (queue command)
        
        Args:
            direction: Force control switches for 6 directions [x,y,z,rx,ry,rz], 1 means enabled, 0 means disabled
            force: Target forces for 6 directions [fx,fy,fz,frx,fry,frz], translation range [-200,200]N, attitude range [-12,12]N/m
            reference: Reference coordinate system type (0-tool coordinate system, 1-user coordinate system)
            user: User coordinate system number (0-50)
            tool: Tool coordinate system number (0-50)
        """
        if len(direction) != 6:
            raise ValueError("direction requires 6 parameters")
        if len(force) != 6:
            raise ValueError("force requires 6 parameters")
        for d in direction:
            if d not in [0, 1]:
                raise ValueError("direction parameter value must be 0 or 1")
        for i, f in enumerate(force):
            if i < 3:
                if not (-200 <= f <= 200):
                    raise ValueError("translation target force must be in [-200, 200]")
            else:
                if not (-12 <= f <= 12):
                    raise ValueError("attitude target force must be in [-12, 12]")
        if user != -1 and not (0 <= user <= 50):
            raise ValueError("user parameter must be in [0, 50]")
        if tool != -1 and not (0 <= tool <= 50):
            raise ValueError("tool parameter must be in [0, 50]")
        if reference not in [0, 1]:
            raise ValueError("reference parameter must be 0 or 1")
        direction_str = "{" + ",".join([f"{v}" for v in direction]) + "}"
        force_str = "{" + ",".join([f"{v}" for v in force]) + "}"
        params = [direction_str, force_str]
        if reference != 0:
            params.append(f"reference={reference}")
        if user != -1:
            params.append(f"user={user}")
        if tool != -1:
            params.append(f"tool={tool}")
        return self._send_cmd(f"FCForceMode({','.join(params)})")

    def FCSetDeviation(self, deviation: Sequence[float], control_type: int = -1) -> str:
        """
        FCSetDeviation set translation and attitude deviation in force control mode (immediate command)
        
        Args:
            deviation: Deviations for 6 directions [x,y,z,rx,ry,rz], translation unit mm, attitude unit degrees
                       Translation deviation range (0, 1000], default 100; attitude deviation range (0, 360], default 36
            control_type: Control type, 0-alarm when exceeding threshold, 1-stop searching and continue motion when exceeding threshold, -1 means default
        """
        if len(deviation) != 6:
            raise ValueError("deviation requires 6 parameters")
        for v in deviation[:3]:
            if not (0 < v <= 1000):
                raise ValueError("translation deviation must be in (0, 1000]")
        for v in deviation[3:]:
            if not (0 < v <= 360):
                raise ValueError("attitude deviation must be in (0, 360]")
        if control_type not in [-1, 0, 1]:
            raise ValueError("control_type must be -1, 0 or 1")
        dev_str = "{" + ",".join([f"{v}" for v in deviation]) + "}"
        if control_type == -1:
            return self._send_cmd(f"FCSetDeviation({dev_str})")
        return self._send_cmd(f"FCSetDeviation({dev_str},{control_type})")

    def FCSetForceLimit(self, x: float, y: float, z: float,
                           rx: float, ry: float, rz: float) -> str:
        """
        FCSetForceLimit set maximum force limit (immediate command)
        
        Args:
            x,y,z: Translation direction maximum force limit (N), range (0, 500], default 500
            rx,ry,rz: Attitude direction maximum force limit (N/m), range (0, 50], default 50
        """
        for v in [x, y, z]:
            if not (0 < v <= 500):
                raise ValueError("translation direction maximum force limit must be in (0, 500]")
        for v in [rx, ry, rz]:
            if not (0 < v <= 50):
                raise ValueError("attitude direction maximum force limit must be in (0, 50]")
        return self._send_cmd(f"FCSetForceLimit({x},{y},{z},{rx},{ry},{rz})")

    def FCSetMass(self, x: float, y: float, z: float,
                    rx: float, ry: float, rz: float) -> str:
        """
        FCSetMass set inertia coefficient for each direction in force control mode (immediate command)
        
        Args:
            x,y,z: Translation direction inertia coefficient (kg), range (0, 10000], default 20
            rx,ry,rz: Attitude direction inertia coefficient (kg·m²), range (0, 10000], default 20
        """
        for v in [x, y, z, rx, ry, rz]:
            if not (0 < v <= 10000):
                raise ValueError("inertia coefficient must be in (0, 10000]")
        return self._send_cmd(f"FCSetMass({x},{y},{z},{rx},{ry},{rz})")

    def FCSetStiffness(self, x: float, y: float, z: float,
                         rx: float, ry: float, rz: float) -> str:
        """
        FCSetStiffness set stiffness coefficient for each direction in force control mode (immediate command)
        
        Args:
            x,y,z: Translation direction stiffness coefficient (N/mm), range [0, 10000], default 30
            rx,ry,rz: Attitude direction stiffness coefficient (N/m·deg), range [0, 10000], default 30
        """
        for v in [x, y, z, rx, ry, rz]:
            if not (0 <= v <= 10000):
                raise ValueError("stiffness coefficient must be in [0, 10000]")
        return self._send_cmd(f"FCSetStiffness({x},{y},{z},{rx},{ry},{rz})")

    def FCSetDamping(self, x: float, y: float, z: float,
                       rx: float, ry: float, rz: float) -> str:
        """
        FCSetDamping set damping coefficient for each direction in force control mode (immediate command)
        
        Args:
            x,y,z: Translation direction damping coefficient (N·s/mm), range [0, 1000], default 50
            rx,ry,rz: Attitude direction damping coefficient (N·s/m·deg), range [0, 1000], default 50
        """
        for v in [x, y, z, rx, ry, rz]:
            if not (0 <= v <= 1000):
                raise ValueError("damping coefficient must be in [0, 1000]")
        return self._send_cmd(f"FCSetDamping({x},{y},{z},{rx},{ry},{rz})")

    def FCOff(self) -> str:
        """FCOff exit force control mode (queue command)"""
        return self._send_cmd("FCOff()")

    def FCSetForceSpeedLimit(self, x: float, y: float, z: float,
                                 rx: float, ry: float, rz: float) -> str:
        """
        FCSetForceSpeedLimit set force control adjustment speed for each direction (immediate command)
        
        Args:
            x,y,z: Translation direction force control adjustment speed (mm/s)
                   CRA/CRAF model range (0, safety limit TCP speed value]
                   Other models range (0, 300]
            rx,ry,rz: Attitude direction force control adjustment speed (deg/s)
                      CRA/CRAF model range (0, (4*safety limit TCP speed value*0.001)/(3.14*180)]
                      Other models range (0, 90]
        """
        for v in [x, y, z]:
            if not (0 < v <= 300):
                raise ValueError("translation direction force control adjustment speed must be in (0, 300]")
        for v in [rx, ry, rz]:
            if not (0 < v <= 90):
                raise ValueError("attitude direction force control adjustment speed must be in (0, 90]")
        return self._send_cmd(f"FCSetForceSpeedLimit({x},{y},{z},{rx},{ry},{rz})")

    def FCSetForce(self, x: float, y: float, z: float,
                     rx: float, ry: float, rz: float) -> str:
        """
        FCSetForce real-time adjust constant force settings for each direction (immediate command)
        
        Args:
            x,y,z: Translation direction constant force value (N), range [-200, 200]
            rx,ry,rz: Attitude direction constant force value (N/m), range [-12, 12]
        """
        for v in [x, y, z]:
            if not (-200 <= v <= 200):
                raise ValueError("translation direction constant force value must be in [-200, 200]")
        for v in [rx, ry, rz]:
            if not (-12 <= v <= 12):
                raise ValueError("attitude direction constant force value must be in [-12, 12]")
        return self._send_cmd(f"FCSetForce({x},{y},{z},{rx},{ry},{rz})")

    # ==================== Force Sensor Collision Detection (Only for CRAF models) ====================

    def SetFCCollision(self, force: float, torque: float) -> str:
        """
        SetFCCollision set threshold parameters for force sensor collision detection (only for CRAF models, immediate command)
        
        Args:
            force: Force threshold for triggering force sensor collision detection, unit N
                   CR5AF range: [5, 150]
                   CR10AF range: [5, 300]
                   CR20AF range: [5, 500]
            torque: Torque threshold for triggering force sensor collision detection, unit N/m
                    CR5AF range: [0.5, 15]
                    CR10AF range: [0.5, 30]
                    CR20AF range: [0.5, 50]
        """
        if not (5 <= force <= 500):
            raise ValueError("force threshold must be in [5, 500], specific range depends on model")
        if not (0.5 <= torque <= 50):
            raise ValueError("torque threshold must be in [0.5, 50], specific range depends on model")
        return self._send_cmd(f"SetFCCollision({force},{torque})")

    def FCCollisionSwitch(self, status: int) -> str:
        """
        FCCollisionSwitch enable/disable force sensor collision detection switch (only for CRAF models, immediate command)
        
        Args:
            status: 0-disable collision detection, 1-enable collision detection
        """
        if status not in [0, 1]:
            raise ValueError("status must be 0 or 1")
        return self._send_cmd(f"FCCollisionSwitch({status})")

    # ==================== Conveyor Tracking ====================

    def CnvInit(self, index: int) -> str:
        """
        CnvInit enable conveyor (immediate command)
        
        Args:
            index: Conveyor index (1-3)
        """
        if not 1 <= index <= 3:
            raise ValueError("conveyor index must be in 1-3")
        return self._send_cmd(f"CnvInit({index})")

    def GetCnvObject(self, obj_id: int) -> str:
        """
        GetCnvObject wait for specified workpiece to enter conveyor gripping area (immediate command)
        
        Args:
            obj_id: Workpiece type, range [0, 15]
                    0: Do not specify workpiece type, get the first workpiece entering the queue
        """
        if not 0 <= obj_id <= 15:
            raise ValueError("workpiece type must be in 0-15")
        return self._send_cmd(f"GetCnvObject({obj_id})")

    def StartSyncCnv(self) -> str:
        """StartSyncCnv enable conveyor tracking function (immediate command)"""
        return self._send_cmd("StartSyncCnv()")

    def CnvMovL(self, pose: Sequence[float],
                 coord_type: CoordinateType = CoordinateType.CARTESIAN,
                 user: int = -1, tool: int = -1,
                 a: int = -1, v: int = -1, speed: int = -1,
                 cp: int = -1, r: int = -1) -> str:
        """
        CnvMovL execute conveyor following, using linear trajectory interpolation (queue command)
        
        Args:
            pose: 6 coordinate values [x,y,z,rx,ry,rz] or [j1,j2,j3,j4,j5,j6]
            coord_type: Point coordinate system type (CoordinateType.JOINT or CoordinateType.CARTESIAN)
            user: User coordinate system number (0-50)
            tool: Tool coordinate system number (0-50)
            a: Acceleration ratio (1-100)
            v: Speed ratio (1-100), mutually exclusive with speed
            speed: Target speed (mm/s), mutually exclusive with v
            cp: Smooth transition ratio (0-100), mutually exclusive with r
            r: Smooth transition radius (mm), mutually exclusive with cp
        """
        if len(pose) != 6:
            raise ValueError("pose requires 6 parameters")

        if coord_type == CoordinateType.JOINT:
            prefix = "joint"
        else:
            prefix = "pose"

        pose_str = prefix + "={" + ",".join([f"{v:.6f}" for v in pose]) + "}"
        params = [pose_str]
        if user != -1:
            params.append(f"user={user}")
        if tool != -1:
            params.append(f"tool={tool}")
        if a != -1:
            params.append(f"a={a}")
        if v != -1:
            params.append(f"v={v}")
        if speed != -1:
            params.append(f"speed={speed}")
        if cp != -1:
            params.append(f"cp={cp}")
        if r != -1:
            params.append(f"r={r}")
        return self._send_cmd(f"CnvMovL({','.join(params)})")

    def CnvMovC(self, via_point: Sequence[float], target_point: Sequence[float],
                 user: int = -1, tool: int = -1,
                 a: int = -1, v: int = -1, speed: int = -1,
                 cp: int = -1, r: int = -1, mode: int = 0,
                 coord_type: CoordinateType = CoordinateType.CARTESIAN) -> str:
        """
        CnvMovC execute conveyor following arc trajectory interpolation (queue command)
        
        Document prototype: CnvMovC(P1,P2,user, tool, a, v, cp|r, mode)
        P1=via point, P2=target point
        
        Args:
            via_point: Arc via point P1 [x,y,z,rx,ry,rz] or [j1..j6]
            target_point: Arc endpoint P2 [x,y,z,rx,ry,rz] or [j1..j6]
            user: User coordinate system number (0-50). -1 means current
            tool: Tool coordinate system number (0-50). -1 means current
            a: Acceleration ratio (1-100). -1 means use default
            v: Speed ratio (1-100), mutually exclusive with speed. -1 means use default
            speed: Target speed (mm/s), mutually exclusive with v (speed has priority)
            cp: Smooth transition ratio (0-100), mutually exclusive with r. -1 means not set
            r: Smooth transition radius (mm), mutually exclusive with cp. -1 means not set
            mode: Interpolation mode. Default 0
            coord_type: Point coordinate system type (Cartesian or Joint)
        """
        if len(via_point) != 6:
            raise ValueError("via_point (via point P1) requires 6 parameters")
        if len(target_point) != 6:
            raise ValueError("target_point (target point P2) requires 6 parameters")

        if coord_type == CoordinateType.JOINT:
            prefix = "joint"
        else:
            prefix = "pose"

        via_str = prefix + "={" + ",".join([f"{val:.6f}" for val in via_point]) + "}"
        target_str = prefix + "={" + ",".join([f"{val:.6f}" for val in target_point]) + "}"

        params = [via_str, target_str]
        if user != -1:
            params.append(f"user={user}")
        if tool != -1:
            params.append(f"tool={tool}")
        if a != -1:
            params.append(f"a={a}")
        if speed != -1:
            params.append(f"speed={speed}")
        elif v != -1:
            params.append(f"v={v}")
        if cp != -1:
            params.append(f"cp={cp}")
        if r != -1:
            params.append(f"r={r}")
        if mode != 0:
            params.append(f"mode={mode}")
        return self._send_cmd(f"CnvMovC({','.join(params)})")

    def StopSyncCnv(self) -> str:
        """StopSyncCnv stop conveyor tracking function (immediate command)"""
        return self._send_cmd("StopSyncCnv()")

    def SetCnvPointOffset(self, x_offset: float, y_offset: float) -> str:
        """
        SetCnvPointOffset set X, Y direction offsets in conveyor user coordinate system (immediate command)
        
        Args:
            x_offset: X direction offset (mm)
            y_offset: Y direction offset (mm)
        """
        return self._send_cmd(f"SetCnvPointOffset({x_offset},{y_offset})")

    def SetCnvTimeCompensation(self, compensation: float) -> str:
        """
        SetCnvTimeCompensation set compensation time (immediate command)
        
        Args:
            compensation: Compensation time (ms)
        """
        return self._send_cmd(f"SetCnvTimeCompensation({compensation})")


