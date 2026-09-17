# Copyright (c) 2026 Dobot
# Licensed under the MIT License

"""Motion-related module - All motion commands and trajectory control"""

from typing import Sequence
from enum import IntEnum
from ..core.connection import DobotConnection


class CoordinateType(IntEnum):
    """Coordinate system type enum (matches doc coordtype values exactly)

    Value mapping:
    0 = Joint coordinates (joint)
    1 = User coordinates (user / Cartesian)
    2 = Tool coordinates (tool / Cartesian)
    """
    JOINT = 0     # Joint angles — doc coordtype=0
    CARTESIAN = 1 # Cartesian pose in user coordinate system — doc coordtype=1
    USER = 1      # User coordinate alias, equivalent to CARTESIAN
    TOOL = 2      # Cartesian pose in tool coordinate system — doc coordtype=2


class Motion:
    """Motion module - Handles all motion-related commands"""
    
    def __init__(self, connection: DobotConnection):
        self.connection = connection
    
    def _fmt_pose(self, pose: Sequence[float], coord_type: CoordinateType) -> str:
        """Format pose as joint={...} or pose={...}

        Note: USER(1) and TOOL(2) both use pose= prefix in the point format.
        The actual user/tool coordinate system is specified separately via user= and tool= parameters.
        """
        if len(pose) != 6:
            raise ValueError(f"Pose requires6 parameters, got{len(pose)}")
        
        values = ",".join([f"{v:.6f}" for v in pose])
        if coord_type == CoordinateType.JOINT:
            return f"joint={{{values}}}"
        else:
            return f"pose={{{values}}}"
    
    def _send_cmd(self, command: str) -> str:
        """Send command and receive response"""
        return self.connection.send_receive_text(command)
    
    # ==================== Basic Motion ====================
    
    def MovJ(self, pose: Sequence[float], 
             coord_type: CoordinateType,
             user: int = -1, tool: int = -1,
             a: int = -1, v: int = -1, cp: int = -1) -> str:
        """
        MovJ Joint Motion (Queued Command)
        
        Args:
            pose:6 coordinate values [x,y,z,rx,ry,rz] or [j1,j2,j3,j4,j5,j6]
            coord_type: Coordinate system type (CoordinateType.CARTESIAN or CoordinateType.JOINT)
            user: User coordinate system index (0-50, -1 for current)
            tool: Tool coordinate system index (0-50, -1 for current)
            a: Acceleration ratio (1-100, -1 for global)
            v: Velocity ratio (1-100, -1 for global)
            cp: Smoothing ratio (0-100, -1 for disabled)

        Returns:
            str: ErrorID,{ResultID},MovJ(...);
        """
        pose_str = self._fmt_pose(pose, coord_type)
        
        params = [pose_str]
        if user != -1:
            params.append(f"user={user}")
        if tool != -1:
            params.append(f"tool={tool}")
        if a != -1:
            params.append(f"a={a}")
        if v != -1:
            params.append(f"v={v}")
        if cp != -1:
            params.append(f"cp={cp}")
        
        cmd = f"MovJ({','.join(params)})"
        return self._send_cmd(cmd)
    
    def MovL(self, pose: Sequence[float],
             coord_type: CoordinateType,
             user: int = -1, tool: int = -1,
             a: int = -1, v: int = -1, speed: int = -1,
             cp: int = -1, r: int = -1) -> str:
        """
        MovL Linear Motion (Queued Command)
        
        Args:
            pose:6 Cartesian coordinates [x,y,z,rx,ry,rz]
            coord_type: Coordinate system type (required)
            user: User coordinate system index (0-50)
            tool: Tool coordinate system index (0-50)
            a: Acceleration ratio (1-100)
            v: Velocity ratio (1-100), mutually exclusive with speed
            speed: Target speed (mm/s), mutually exclusive with v
            cp: Smoothing ratio (0-100), mutually exclusive with r
            r: Smoothing radius (mm), mutually exclusive with cp

        Returns:
            str: ErrorID,{ResultID},MovL(...);
        """
        pose_str = self._fmt_pose(pose, coord_type)
        
        params = [pose_str]
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
        if r != -1:
            params.append(f"r={r}")
        elif cp != -1:
            params.append(f"cp={cp}")
        
        cmd = f"MovL({','.join(params)})"
        return self._send_cmd(cmd)
    
    def MovLIO(self, pose: Sequence[float], do_list: list,
                coord_type: CoordinateType,
                user: int = -1, tool: int = -1,
                a: int = -1, v: int = -1, speed: int = -1,
                cp: int = -1, r: int = -1) -> str:
        """
        MovLIO Linear Motion with DO Output (Queued Command)
        
        Args:
            pose:6 Cartesian coordinates [x,y,z,rx,ry,rz]
            do_list: DO output list, each element is [Mode, Distance, Index, Status]
                     Mode=0/1, Distance=mm, Index=DO index, Status=0/1
            coord_type: Coordinate system type
            user: User coordinate system index (0-50)
            tool: Tool coordinate system index (0-50)
            a: Acceleration ratio (1-100)
            v: Velocity ratio (1-100), mutually exclusive with speed
            speed: Target speed (mm/s), mutually exclusive with v
            cp: Smoothing ratio (0-100), mutually exclusive with r
            r: Smoothing radius (mm), mutually exclusive with cp

        Returns:
            str: ErrorID,{ResultID},MovLIO(...);
        """
        pose_str = self._fmt_pose(pose, coord_type)
        
        params = [pose_str]
        for do_item in do_list:
            if len(do_item) != 4:
                raise ValueError("Each DO parameter requires4 values[Mode, Distance, Index, Status]")
            mode, distance, index, status = do_item
            params.append(f"{{{mode},{distance},{index},{status}}}")
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
        if r != -1:
            params.append(f"r={r}")
        elif cp != -1:
            params.append(f"cp={cp}")
        
        cmd = f"MovLIO({','.join(params)})"
        return self._send_cmd(cmd)
    
    def MovJIO(self, pose: Sequence[float], do_list: list,
                coord_type: CoordinateType,
                user: int = -1, tool: int = -1,
                a: int = -1, v: int = -1, cp: int = -1) -> str:
        """
        MovJIO Joint Motion with DO Output (Queued Command)
        
        Args:
            pose:6 coordinate values [x,y,z,rx,ry,rz] or [j1,j2,j3,j4,j5,j6]
            do_list: DO output list, each element is [Mode, Distance, Index, Status]
                     Mode=0/1, Distance=mm, Index=DO index, Status=0/1
            coord_type: Coordinate system type
            user: User coordinate system index (0-50)
            tool: Tool coordinate system index (0-50)
            a: Acceleration ratio (1-100)
            v: Velocity ratio (1-100)
            cp: Smoothing ratio (0-100)

        Returns:
            str: ErrorID,{ResultID},MovJIO(...);
        """
        pose_str = self._fmt_pose(pose, coord_type)
        
        params = [pose_str]
        for do_item in do_list:
            if len(do_item) != 4:
                raise ValueError("Each DO parameter requires4 values[Mode, Distance, Index, Status]")
            mode, distance, index, status = do_item
            params.append(f"{{{mode},{distance},{index},{status}}}")
        if user != -1:
            params.append(f"user={user}")
        if tool != -1:
            params.append(f"tool={tool}")
        if a != -1:
            params.append(f"a={a}")
        if v != -1:
            params.append(f"v={v}")
        if cp != -1:
            params.append(f"cp={cp}")
        
        cmd = f"MovJIO({','.join(params)})"
        return self._send_cmd(cmd)
    
    def Arc(self, p1: Sequence[float], p2: Sequence[float],
            coord_type: CoordinateType,
            user: int = -1, tool: int = -1,
            a: int = -1, v: int = -1, speed: int = -1,
            cp: int = -1, r: int = -1, mode: int = 0) -> str:
        """
        Arc Interpolation Motion (Queued Command)
        
        Args:
            p1: Arc midpoint
            p2: Target point pose
            coord_type: Coordinate system type
            user: User coordinate system index (0-50, -1 for current)
            tool: Tool coordinate system index (0-50, -1 for current)
            a: Acceleration ratio (1-100, -1 for global)
            v: Velocity ratio (1-100, -1 for global)
            speed: Target speed (mm/s), mutually exclusive with v
            cp: Smoothing ratio (0-100), mutually exclusive with r
            r: Smoothing radius (mm), mutually exclusive with cp
            mode: Pose control mode (0-linear 1-through midpoint, 2-fixed)

        Returns:
            str: ErrorID,{ResultID},Arc(...);
        """
        if len(p1) != 6 or len(p2) != 6:
            raise ValueError(f"Pose requires6 parameters")
        
        if coord_type == CoordinateType.JOINT:
            p1_str = f"joint={{{','.join([f'{v:.6f}' for v in p1])}}}"
            p2_str = f"joint={{{','.join([f'{v:.6f}' for v in p2])}}}"
        else:
            p1_str = f"pose={{{','.join([f'{v:.6f}' for v in p1])}}}"
            p2_str = f"pose={{{','.join([f'{v:.6f}' for v in p2])}}}"
        
        params = [p1_str, p2_str]
        
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
        if r != -1:
            params.append(f"r={r}")
        elif cp != -1:
            params.append(f"cp={cp}")
        if mode != 0:
            params.append(f"mode={mode}")
        
        cmd = f"Arc({','.join(params)})"
        return self._send_cmd(cmd)
    
    def ArcIO(self, p1: Sequence[float], p2: Sequence[float],
               do_list: list,
               coord_type: CoordinateType,
               user: int = -1, tool: int = -1,
               a: int = -1, v: int = -1, speed: int = -1,
               cp: int = -1, r: int = -1, mode: int = 0) -> str:
        """
        ArcIO Arc Motion with DO Output (Queued Command)
        
        Args:
            p1: Arc midpoint
            p2: Target point pose
            do_list: DO output list, each element is [Mode, Distance, Index, Status]
                     Mode=0/1, Distance=mm, Index=DO index, Status=0/1
            coord_type: Coordinate system type
            user: User coordinate system index (0-50)
            tool: Tool coordinate system index (0-50)
            a: Acceleration ratio (1-100)
            v: Velocity ratio (1-100)
            speed: Target speed (mm/s), mutually exclusive with v
            cp: Smoothing ratio (0-100), mutually exclusive with r
            r: Smoothing radius (mm), mutually exclusive with cp
            mode: Pose control mode (0-2)

        Returns:
            str: ErrorID,{ResultID},ArcIO(...);
        """
        if len(p1) != 6 or len(p2) != 6:
            raise ValueError(f"Pose requires6 parameters")
        
        if coord_type == CoordinateType.JOINT:
            p1_str = f"joint={{{','.join([f'{v:.6f}' for v in p1])}}}"
            p2_str = f"joint={{{','.join([f'{v:.6f}' for v in p2])}}}"
        else:
            p1_str = f"pose={{{','.join([f'{v:.6f}' for v in p1])}}}"
            p2_str = f"pose={{{','.join([f'{v:.6f}' for v in p2])}}}"
        
        params = [p1_str, p2_str]
        for do_item in do_list:
            if len(do_item) != 4:
                raise ValueError("Each DO parameter requires4 values[Mode, Distance, Index, Status]")
            mode_do, distance, index, status = do_item
            params.append(f"{{{mode_do},{distance},{index},{status}}}")
        
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
        if r != -1:
            params.append(f"r={r}")
        elif cp != -1:
            params.append(f"cp={cp}")
        if mode != 0:
            params.append(f"mode={mode}")
        
        cmd = f"ArcIO({','.join(params)})"
        return self._send_cmd(cmd)
    
    def Circle(self, p1: Sequence[float], p2: Sequence[float],
               count: int, coord_type: CoordinateType,
               user: int = -1, tool: int = -1,
               a: int = -1, v: int = -1, speed: int = -1,
               cp: int = -1, r: int = -1, mode: int = 0) -> str:
        """
        Circle Full Circle Interpolation Motion (Queued Command)
        
        Args:
            p1: Full circle midpoint pose
            p2: Full circle endpoint pose (should be same as start point)
            count: Number of circles (1-999)
            coord_type: Coordinate system type
            user: User coordinate system index (0-50)
            tool: Tool coordinate system index (0-50)
            a: Acceleration ratio (1-100)
            v: Velocity ratio (1-100)
            speed: Target speed (mm/s), mutually exclusive with v
            cp: Smoothing ratio (0-100), mutually exclusive with r
            r: Smoothing radius (mm), mutually exclusive with cp
            mode: Pose control mode (0-2)

        Returns:
            str: ErrorID,{ResultID},Circle(...);
        """
        if not 1 <= count <= 999:
            raise ValueError(f"Count must be between1-999")
        
        if len(p1) != 6 or len(p2) != 6:
            raise ValueError(f"Pose requires6 parameters")
        
        if coord_type == CoordinateType.JOINT:
            p1_str = f"joint={{{','.join([f'{v:.6f}' for v in p1])}}}"
            p2_str = f"joint={{{','.join([f'{v:.6f}' for v in p2])}}}"
        else:
            p1_str = f"pose={{{','.join([f'{v:.6f}' for v in p1])}}}"
            p2_str = f"pose={{{','.join([f'{v:.6f}' for v in p2])}}}"
        
        params = [p1_str, p2_str, str(count)]
        
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
        if r != -1:
            params.append(f"r={r}")
        elif cp != -1:
            params.append(f"cp={cp}")
        if mode != 0:
            params.append(f"mode={mode}")
        
        cmd = f"Circle({','.join(params)})"
        return self._send_cmd(cmd)
    
    # ==================== Servo Motion ====================
    
    def ServoJ(self, joints: Sequence[float],
                t: float = 0.1, aheadtime: float = 50.0, gain: float = 500.0) -> str:
        """
        ServoJ Joint-space Dynamic Following Command (Queued Command)        
        Args:
            joints:6 joint angles [j1,j2,j3,j4,j5,j6]
            t: Runtime (seconds) 0.004-3600.0
            aheadtime: Advance time (20.0-100.0), similar to PID D parameter
            gain: Proportional gain (200.0-1000.0), similar to PID P parameter
        Returns:
            str: ErrorID,{ResultID},ServoJ(...);
        """
        if len(joints) != 6:
            raise ValueError("joints requires6 joint angles")
        if not 0.004 <= t <= 3600.0:
            raise ValueError(f"t must be between0.004-3600.0")
        if not 20.0 <= aheadtime <= 100.0:
            raise ValueError(f"aheadtime must be between20.0-100.0")
        if not 200.0 <= gain <= 1000.0:
            raise ValueError(f"gain must be between200.0-1000.0")
        
        cmd = f"ServoJ({joints[0]:.6f},{joints[1]:.6f},{joints[2]:.6f},{joints[3]:.6f},{joints[4]:.6f},{joints[5]:.6f},t={t:.3f},aheadtime={aheadtime:.1f},gain={gain:.1f})"
        return self._send_cmd(cmd)
    
    def ServoP(self, pose: Sequence[float],
                t: float = 0.1, aheadtime: float = 50.0, gain: float = 500.0) -> str:
        """
        ServoP Cartesian-space Dynamic Following Command (Queued Command)        
        Args:
            pose: Cartesian pose [x,y,z,rx,ry,rz]
            t: Runtime (seconds) 0.004-3600.0
            aheadtime: Advance time (20.0-100.0)
            gain: Proportional gain (200.0-1000.0)

        Returns:
            str: ErrorID,{ResultID},ServoP(...);
        """
        if len(pose) != 6:
            raise ValueError("pose requires6 Cartesian pose parameters")
        if not 0.004 <= t <= 3600.0:
            raise ValueError(f"t must be between0.004-3600.0")
        if not 20.0 <= aheadtime <= 100.0:
            raise ValueError(f"aheadtime must be between20.0-100.0")
        if not 200.0 <= gain <= 1000.0:
            raise ValueError(f"gain must be between200.0-1000.0")
        
        cmd = f"ServoP({pose[0]:.6f},{pose[1]:.6f},{pose[2]:.6f},{pose[3]:.6f},{pose[4]:.6f},{pose[5]:.6f},t={t:.3f},aheadtime={aheadtime:.1f},gain={gain:.1f})"
        return self._send_cmd(cmd)
    
    # ==================== Jog ====================
    
    def MoveJog(self, axis: str = "", coord_type: CoordinateType = None,
                 user: int = None, tool: int = None) -> str:
        """
        MoveJog Robot Arm Jogging (Immediate Command)

        Notes (matches documentation exactly):
        - coordtype default is "last successful call setting", not sent if not provided
        - user/tool not sent if not explicitly provided, controller uses its default
        - When axisID is joint axis (J1~J6), coordtype can only be0 (ignores input)
        - When axisID is Cartesian axis (X/Y/Z/Rx/Ry/Rz), coordtype can only be1 or2,0 returns error code-6

        Args:
            axis: "X+", "X-", "J1+" etc., empty string stops
            coord_type: Coordinate system type, optional. None=use controller's last successful setting
                        JOINT=0(joint jog), USER/CARTESIAN=1(user coordinate), TOOL=2(tool coordinate)
            user: User coordinate system index, optional. None=use controller default
            tool: Tool coordinate system index, optional. None=use controller default
        Returns:
            str: ErrorID,{},MoveJog(...);
        """
        if not axis:
            return self._send_cmd("MoveJog()")

        params = [axis]
        if coord_type is not None:
            params.append(f"coordtype={int(coord_type)}")
        if user is not None:
            params.append(f"user={user}")
        if tool is not None:
            params.append(f"tool={tool}")

        cmd = f"MoveJog({','.join(params)})"
        return self._send_cmd(cmd)
    
    # ==================== Move to Point ====================
    
    def RunTo(self, point: Sequence[float], move_type: int,
              user: int = -1, tool: int = -1,
              a: int = -1, v: int = -1,
              coord_type: CoordinateType = CoordinateType.CARTESIAN) -> str:
        """
        RunTo Move to Specified Point (Immediate Command)
        
        Args:
            point:6 coordinate values [x,y,z,rx,ry,rz] or [j1,j2,j3,j4,j5,j6]
            move_type: Motion type
                       0=Joint motion, 1=Linear motion
                       2=Joint motion to specified offset angle (relative joint)
                       3=Relative linear motion along tool coordinate system
                       4=Relative linear motion along user coordinate system
            user: User coordinate system index (0-50, -1 for current)
            tool: Tool coordinate system index (0-50, -1 for current)
            a: Acceleration ratio (1-100, -1 for global)
            v: Velocity ratio (1-100, -1 for global)
            coord_type: Coordinate system type (default CARTESIAN)

        Returns:
            str: ErrorID,{ResultID},RunTo(...);
        """
        if move_type not in [0, 1, 2, 3, 4]:
            raise ValueError("move_type must be within [0,4] range:0=joint,1=linear, "
                             "2=joint offset,3=tool coordinate relative linear,4=user coordinate relative linear")
        
        point_str = self._fmt_pose(point, coord_type)
        
        params = [point_str, str(move_type)]
        if user != -1:
            params.append(f"user={user}")
        if tool != -1:
            params.append(f"tool={tool}")
        if a != -1:
            params.append(f"a={a}")
        if v != -1:
            params.append(f"v={v}")
        
        cmd = f"RunTo({','.join(params)})"
        return self._send_cmd(cmd)
    
    # ==================== Trajectory Playback ====================
    
    def GetStartPose(self, trace_name: str, path_type: int = 1) -> str:
        """
        GetStartPose Get First Point of Specified Trajectory (Immediate Command)        
        Args:
            trace_name: Trajectory file name (with extension.csv)
            path_type: Trajectory type (1-for playback,2-for fitting, default1)

        Returns:
            str: ErrorID,{X,Y,Z,Rx,Ry,Rz},GetStartPose(traceName,pathType);
        """
        if path_type not in [1, 2]:
            raise ValueError("path_type must be1 or2")
        
        cmd = f"GetStartPose(\"{trace_name}\",{path_type})"
        return self._send_cmd(cmd)
    
    def MovS(self,
             trace_or_points,
             coord_type: CoordinateType = CoordinateType.CARTESIAN,
             freq: float = -1,
             user: int = -1, tool: int = -1,
             a: int = -1, v: int = -1, speed: int = -1) -> str:
        """
        MovS Fitting Motion (Queued Command)
        Supports two calling methods:
        1. Point list method: MovS([p1, p2, p3, ...], coord_type, freq, user, tool, a, v|speed, freq)
        2. File method: MovS("xxx.csv", coord_type, freq, user, tool, a, v|speed, freq)

        Args:
            trace_or_points: 
                - str: Trajectory file name (with extension, e.g."xxx.csv") -> File method
                - Sequence[Sequence[float]]: Point list, each point is [x,y,z,rx,ry,rz] or [j1..j6]
            coord_type: Point coordinate system type (only used for point list method)
            freq: Filter coefficient (range0-1,1=disable filter,-1=not set)
            user: User coordinate system index (0-50, -1 for current)
            tool: Tool coordinate system index (0-50, -1 for current)
            a: Acceleration ratio (1-100, -1 for global)
            v: Velocity ratio (1-100, -1 for global), mutually exclusive with speed
            speed: Target speed (mm/s), mutually exclusive with v (speed priority)

        Returns:
            str: ErrorID,{ResultID},MovS(...);
        """
        params = []

        if isinstance(trace_or_points, str):
            params.append(f"\"{trace_or_points}\"")
        else:
            points = list(trace_or_points)
            if len(points) < 4 or len(points) > 50:
                raise ValueError("Point list method requires4~50 points")
            for p in points:
                if len(p) != 6:
                    raise ValueError("Each point requires6 values [x,y,z,rx,ry,rz] or [j1..j6]")
                params.append(self._fmt_pose(p, coord_type))

        if freq != -1:
            params.append(f"freq={freq}")
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

        cmd = f"MovS({','.join(params)})"
        return self._send_cmd(cmd)
    
    def StartPath(self, trace_name: str, is_const: int = 0, 
                   multi: float = 1.0, sample: int = 50,
                   freq: float = 0.2, user: int = -1, tool: int = -1) -> str:
        """
        StartPath Playback Recorded Trajectory (Queued Command)        
        Args:
            trace_name: Trajectory file name (with extension)
            is_const: Constant speed playback (0-original 1-constant speed)
            multi: Speed multiplier (only meaningful when is_const=0, range0.25-2)
            sample: Sampling interval (ms, range8-1000)
            freq: Filter coefficient (range0-1,1=disable filter)
            user: User coordinate system index (0-50, -1 for current)
            tool: Tool coordinate system index (0-50, -1 for current)

        Returns:
            str: ErrorID,{ResultID},StartPath(...);
        """
        params = [f"\"{trace_name}\""]
        params.append(f"isConst={is_const}")
        params.append(f"multi={multi}")
        params.append(f"sample={sample}")
        params.append(f"freq={freq}")
        if user != -1:
            params.append(f"user={user}")
        if tool != -1:
            params.append(f"tool={tool}")
        
        cmd = f"StartPath({','.join(params)})"
        return self._send_cmd(cmd)
    
    # ==================== Relative Motion ====================
    
    def RelMovJTool(self, offsetX: float, offsetY: float, offsetZ: float,
                    offsetRx: float, offsetRy: float, offsetRz: float,
                    user: int = -1, tool: int = -1,
                    a: int = -1, v: int = -1, cp: int = -1) -> str:
        """
        RelMovJTool Relative Joint Motion Along Tool Coordinate System (Queued Command)
        
        Args:
            offsetX: X direction offset (mm)
            offsetY: Y direction offset (mm)
            offsetZ: Z direction offset (mm)
            offsetRx: Rx direction offset (degrees)
            offsetRy: Ry direction offset (degrees)
            offsetRz: Rz direction offset (degrees)
            user: User coordinate system index (0-50, -1 for current)
            tool: Tool coordinate system index (0-50, -1 for current)
            a: Acceleration ratio (1-100, -1 for global)
            v: Velocity ratio (1-100, -1 for global)
            cp: Smoothing ratio (0-100, -1 for disabled)

        Returns:
            str: ErrorID,{ResultID},RelMovJTool(...);
        """
        params = [
            f"{offsetX:.6f}", f"{offsetY:.6f}", f"{offsetZ:.6f}",
            f"{offsetRx:.6f}", f"{offsetRy:.6f}", f"{offsetRz:.6f}"
        ]
        if user != -1:
            params.append(f"user={user}")
        if tool != -1:
            params.append(f"tool={tool}")
        if a != -1:
            params.append(f"a={a}")
        if v != -1:
            params.append(f"v={v}")
        if cp != -1:
            params.append(f"cp={cp}")
        
        cmd = f"RelMovJTool({','.join(params)})"
        return self._send_cmd(cmd)
    
    def RelMovLTool(self, offsetX: float, offsetY: float, offsetZ: float,
                    offsetRx: float, offsetRy: float, offsetRz: float,
                    user: int = -1, tool: int = -1,
                    a: int = -1, v: int = -1, speed: int = -1,
                    cp: int = -1, r: int = -1) -> str:
        """
        RelMovLTool Relative Linear Motion Along Tool Coordinate System (Queued Command)
        
        Args:
            offsetX: X direction offset (mm)
            offsetY: Y direction offset (mm)
            offsetZ: Z direction offset (mm)
            offsetRx: Rx direction offset (degrees)
            offsetRy: Ry direction offset (degrees)
            offsetRz: Rz direction offset (degrees)
            user: User coordinate system index (0-50, -1 for current)
            tool: Tool coordinate system index (0-50, -1 for current)
            a: Acceleration ratio (1-100, -1 for global)
            v: Velocity ratio (1-100, -1 for global), mutually exclusive with speed
            speed: Target speed (mm/s), mutually exclusive with v (speed priority)
            cp: Smoothing ratio (0-100, -1 for disabled), mutually exclusive with r
            r: Smoothing radius (mm), mutually exclusive with cp (r priority)

        Returns:
            str: ErrorID,{ResultID},RelMovLTool(...);
        """
        params = [
            f"{offsetX:.6f}", f"{offsetY:.6f}", f"{offsetZ:.6f}",
            f"{offsetRx:.6f}", f"{offsetRy:.6f}", f"{offsetRz:.6f}"
        ]
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
        if r != -1:
            params.append(f"r={r}")
        elif cp != -1:
            params.append(f"cp={cp}")
        
        cmd = f"RelMovLTool({','.join(params)})"
        return self._send_cmd(cmd)
    
    def RelMovJUser(self, offsetX: float, offsetY: float, offsetZ: float,
                    offsetRx: float, offsetRy: float, offsetRz: float,
                    user: int = -1, tool: int = -1,
                    a: int = -1, v: int = -1, cp: int = -1) -> str:
        """
        RelMovJUser Relative Joint Motion Along User Coordinate System (Queued Command)
        
        Args:
            offsetX: X direction offset (mm)
            offsetY: Y direction offset (mm)
            offsetZ: Z direction offset (mm)
            offsetRx: Rx direction offset (degrees)
            offsetRy: Ry direction offset (degrees)
            offsetRz: Rz direction offset (degrees)
            user: User coordinate system index (0-50, -1 for current)
            tool: Tool coordinate system index (0-50, -1 for current)
            a: Acceleration ratio (1-100, -1 for global)
            v: Velocity ratio (1-100, -1 for global)
            cp: Smoothing ratio (0-100, -1 for disabled)

        Returns:
            str: ErrorID,{ResultID},RelMovJUser(...);
        """
        params = [
            f"{offsetX:.6f}", f"{offsetY:.6f}", f"{offsetZ:.6f}",
            f"{offsetRx:.6f}", f"{offsetRy:.6f}", f"{offsetRz:.6f}"
        ]
        if user != -1:
            params.append(f"user={user}")
        if tool != -1:
            params.append(f"tool={tool}")
        if a != -1:
            params.append(f"a={a}")
        if v != -1:
            params.append(f"v={v}")
        if cp != -1:
            params.append(f"cp={cp}")
        
        cmd = f"RelMovJUser({','.join(params)})"
        return self._send_cmd(cmd)
    
    def RelMovLUser(self, offsetX: float, offsetY: float, offsetZ: float,
                    offsetRx: float, offsetRy: float, offsetRz: float,
                    user: int = -1, tool: int = -1,
                    a: int = -1, v: int = -1, speed: int = -1,
                    cp: int = -1, r: int = -1) -> str:
        """
        RelMovLUser Relative Linear Motion Along User Coordinate System (Queued Command)
        
        Args:
            offsetX: X direction offset (mm)
            offsetY: Y direction offset (mm)
            offsetZ: Z direction offset (mm)
            offsetRx: Rx direction offset (degrees)
            offsetRy: Ry direction offset (degrees)
            offsetRz: Rz direction offset (degrees)
            user: User coordinate system index (0-50, -1 for current)
            tool: Tool coordinate system index (0-50, -1 for current)
            a: Acceleration ratio (1-100, -1 for global)
            v: Velocity ratio (1-100, -1 for global), mutually exclusive with speed
            speed: Target speed (mm/s), mutually exclusive with v (speed priority)
            cp: Smoothing ratio (0-100, -1 for disabled), mutually exclusive with r
            r: Smoothing radius (mm), mutually exclusive with cp (r priority)

        Returns:
            str: ErrorID,{ResultID},RelMovLUser(...);
        """
        params = [
            f"{offsetX:.6f}", f"{offsetY:.6f}", f"{offsetZ:.6f}",
            f"{offsetRx:.6f}", f"{offsetRy:.6f}", f"{offsetRz:.6f}"
        ]
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
        if r != -1:
            params.append(f"r={r}")
        elif cp != -1:
            params.append(f"cp={cp}")
        
        cmd = f"RelMovLUser({','.join(params)})"
        return self._send_cmd(cmd)
    
    def RelJointMovJ(self, offset1: float, offset2: float, offset3: float,
                     offset4: float, offset5: float, offset6: float,
                     user: int = -1, tool: int = -1,
                     a: int = -1, v: int = -1, cp: int = -1) -> str:
        """
        RelJointMovJ Relative Joint Motion Along Joint Coordinate System (Queued Command)
        
        Args:
            offset1: J1 joint offset (degrees)
            offset2: J2 joint offset (degrees)
            offset3: J3 joint offset (degrees)
            offset4: J4 joint offset (degrees)
            offset5: J5 joint offset (degrees)
            offset6: J6 joint offset (degrees)
            user: User coordinate system index (0-50, -1 for current)
            tool: Tool coordinate system index (0-50, -1 for current)
            a: Acceleration ratio (1-100, -1 for global)
            v: Velocity ratio (1-100, -1 for global)
            cp: Smoothing ratio (0-100, -1 for disabled)

        Returns:
            str: ErrorID,{ResultID},RelJointMovJ(...);
        """
        params = [
            f"{offset1:.6f}", f"{offset2:.6f}", f"{offset3:.6f}",
            f"{offset4:.6f}", f"{offset5:.6f}", f"{offset6:.6f}"
        ]
        if user != -1:
            params.append(f"user={user}")
        if tool != -1:
            params.append(f"tool={tool}")
        if a != -1:
            params.append(f"a={a}")
        if v != -1:
            params.append(f"v={v}")
        if cp != -1:
            params.append(f"cp={cp}")
        
        cmd = f"RelJointMovJ({','.join(params)})"
        return self._send_cmd(cmd)
    
    def RelPointTool(self, p: Sequence[float], offset: Sequence[float],
                     coord_type: CoordinateType = CoordinateType.CARTESIAN) -> str:
        """
        RelPointTool Cartesian Point Offset Along Tool Coordinate System (Immediate Command)
        
        Args:
            p:6-value point [x,y,z,rx,ry,rz] or [j1..j6]
            offset:6-value offset [offsetX,offsetY,offsetZ,offsetRx,offsetRy,offsetRz]
            coord_type: Point coordinate system type. Default is Cartesian (pose), can also be joint (joint)

        Returns:
            str: ErrorID,{X,Y,Z,Rx,Ry,Rz},RelPointTool(...);
        """
        if len(p) != 6:
            raise ValueError("p requires6 point parameters")
        if len(offset) != 6:
            raise ValueError("offset requires6 offset parameters[offsetX,offsetY,offsetZ,offsetRx,offsetRy,offsetRz]")
        
        p_str = self._fmt_pose(p, coord_type)
        offset_values = ",".join([f"{v:.6f}" for v in offset])
        cmd = f"RelPointTool({p_str},{{{offset_values}}})"
        return self._send_cmd(cmd)
    
    def RelPointUser(self, p: Sequence[float], offset: Sequence[float],
                     coord_type: CoordinateType = CoordinateType.CARTESIAN) -> str:
        """
        RelPointUser Cartesian Point Offset Along User Coordinate System (Immediate Command)
        
        Args:
            p:6-value point [x,y,z,rx,ry,rz] or [j1..j6]
            offset:6-value offset [offsetX,offsetY,offsetZ,offsetRx,offsetRy,offsetRz]
            coord_type: Point coordinate system type. Default is Cartesian (pose), can also be joint (joint)

        Returns:
            str: ErrorID,{X,Y,Z,Rx,Ry,Rz},RelPointUser(...);
        """
        if len(p) != 6:
            raise ValueError("p requires6 point parameters")
        if len(offset) != 6:
            raise ValueError("offset requires6 offset parameters[offsetX,offsetY,offsetZ,offsetRx,offsetRy,offsetRz]")
        
        p_str = self._fmt_pose(p, coord_type)
        offset_values = ",".join([f"{v:.6f}" for v in offset])
        cmd = f"RelPointUser({p_str},{{{offset_values}}})"
        return self._send_cmd(cmd)
    
    def RelJoint(self, joints: Sequence[float], offset: Sequence[float]) -> str:
        """
        RelJoint Joint Point Offset (Immediate Command)
        
        Args:
            joints:6 joint angles [J1,J2,J3,J4,J5,J6]
            offset:6 offsets [offset1,offset2,offset3,offset4,offset5,offset6]

        Returns:
            str: ErrorID,{J1,J2,J3,J4,J5,J6},RelJoint(...);
        """
        if len(joints) != 6:
            raise ValueError("joints requires6 joint angles [J1,J2,J3,J4,J5,J6]")
        if len(offset) != 6:
            raise ValueError("offset requires6 offsets [offset1,offset2,offset3,offset4,offset5,offset6]")
        
        joints_str = ",".join([f"{v:.6f}" for v in joints])
        offset_values = ",".join([f"{v:.6f}" for v in offset])
        cmd = f"RelJoint({joints_str},{{{offset_values}}})"
        return self._send_cmd(cmd)
    
    # ==================== Command ID Query ====================
    
    def GetCurrentCommandID(self) -> str:
        """
        GetCurrentCommandID Get Algorithm Queue ID of Current Executing Command (Immediate Command)
        
        Returns:
            str: ErrorID,{ResultID},GetCurrentCommandID();
        """
        return self._send_cmd("GetCurrentCommandID()")
    
    # ==================== Coordinate System Offset ====================
    
    def StartRTOffset(self) -> str:
        """
        StartRTOffset Start Coordinate System Offset (Queued Command)
        
        Returns:
            str: ErrorID,{ResultID},StartRTOffset();
        """
        return self._send_cmd("StartRTOffset()")
    
    def EndRTOffset(self) -> str:
        """
        EndRTOffset End Coordinate System Offset (Queued Command)        
        Returns:
            str: ErrorID,{ResultID},EndRTOffset();
        """
        return self._send_cmd("EndRTOffset()")
    
    def OffsetPara(self, x: float, y: float, z: float,
                   rx: float, ry: float, rz: float) -> str:
        """
        OffsetPara Set Coordinate System Offset Values (Immediate Command)
        
        Args:
            x: X direction offset (mm)
            y: Y direction offset (mm)
            z: Z direction offset (mm)
            rx: Rx direction offset (degrees)
            ry: Ry direction offset (degrees)
            rz: Rz direction offset (degrees)

        Returns:
            str: ErrorID,{},OffsetPara(...);
        """
        cmd = f"OffsetPara({x:.6f},{y:.6f},{z:.6f},{rx:.6f},{ry:.6f},{rz:.6f})"
        return self._send_cmd(cmd)
    
    # ==================== Trajectory Recovery ====================
    
    def SetResumeOffset(self, distance: float) -> str:
        """
        SetResumeOffset Set Trajectory Recovery Retraction Distance (Immediate Command)
        
        Args:
            distance: Retraction distance (mm)

        Returns:
            str: ErrorID,{},SetResumeOffset(distance);
        """
        return self._send_cmd(f"SetResumeOffset({distance:.6f})")
    
    def PathRecovery(self) -> str:
        """
        PathRecovery Start Trajectory Recovery (Immediate Command)        
        Returns:
            str: ErrorID,{},PathRecovery();
        """
        return self._send_cmd("PathRecovery()")
    
    def PathRecoveryStop(self) -> str:
        """
        PathRecoveryStop Stop Robot During Trajectory Recovery (Immediate Command)
        
        Returns:
            str: ErrorID,{},PathRecoveryStop();
        """
        return self._send_cmd("PathRecoveryStop()")
    
    def PathRecoveryStatus(self) -> str:
        """
        PathRecoveryStatus Query Trajectory Recovery Status (Immediate Command)        
        Returns:
            str: ErrorID,{status},PathRecoveryStatus();
                 status: 0-returned to pause position,1-small deviation,2-large deviation
        """
        return self._send_cmd("PathRecoveryStatus()")
