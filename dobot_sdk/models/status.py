# Copyright (c) 2026 Dobot
# Licensed under the MIT License

"""
Robot status data model
"""

from dataclasses import dataclass, field
from typing import List
from enum import IntEnum


class RobotMode(IntEnum):
    """Robot operating mode
    
    Refer to TCP/IP protocol documentation
    """
    UNKNOWN = 0         # Unknown/uninitialized (may be returned by Feedback packet)
    INIT = 1           # Initialization state
    BRAKE_OPEN = 2     # Any joint brake released
    POWEROFF = 3       # Power off state
    DISABLED = 4       # Disabled (no brake released)
    ENABLE = 5         # Enabled and idle
    BACKDRIVE = 6      # Drag mode
    RUNNING = 7        # Running state (project, TCP queue motion, etc.)
    SINGLE_MOVE = 8    # Single motion state (jog, RunTo, etc.)
    ERROR = 9          # Error state
    PAUSE = 10         # Pause state
    JOG = 11           # Jog state


@dataclass
class JointState:
    """Joint state"""
    q_actual: List[float] = field(default_factory=lambda: [0.0] * 6)  # Actual angles
    q_target: List[float] = field(default_factory=lambda: [0.0] * 6)  # Target angles
    qd_actual: List[float] = field(default_factory=lambda: [0.0] * 6)  # Actual velocity
    qd_target: List[float] = field(default_factory=lambda: [0.0] * 6)  # Target velocity
    qdd_target: List[float] = field(default_factory=lambda: [0.0] * 6)  # Target acceleration
    i_actual: List[float] = field(default_factory=lambda: [0.0] * 6)  # Actual current
    i_target: List[float] = field(default_factory=lambda: [0.0] * 6)  # Target current
    m_actual: List[float] = field(default_factory=lambda: [0.0] * 6)  # Actual torque
    m_target: List[float] = field(default_factory=lambda: [0.0] * 6)  # Target torque
    temperatures: List[float] = field(default_factory=lambda: [0.0] * 6)  # Motor temperatures
    joint_modes: List[float] = field(default_factory=lambda: [0.0] * 6)  # Joint control modes
    voltages: List[float] = field(default_factory=lambda: [0.0] * 6)  # Joint voltages


@dataclass
class CartesianPose:
    """Cartesian pose"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    rx: float = 0.0
    ry: float = 0.0
    rz: float = 0.0
    
    def to_list(self) -> List[float]:
        """Convert to list"""
        return [self.x, self.y, self.z, self.rx, self.ry, self.rz]


@dataclass
class Quaternion:
    """Quaternion [qw, qx, qy, qz]"""
    qw: float = 0.0
    qx: float = 0.0
    qy: float = 0.0
    qz: float = 0.0
    
    def to_list(self) -> List[float]:
        """Convert to list"""
        return [self.qw, self.qx, self.qy, self.qz]


@dataclass
class RobotStatus:
    """
    Complete robot status
    
    Parsed from Feedback packet (1440 bytes)
    """
    # Basic status
    robot_mode: RobotMode = RobotMode.INIT
    speed_scaling: float = 0.0  # Speed ratio 0-100
    enable_status: bool = False  # Enable status
    brake_status: bool = False  # Brake status
    error_status: bool = False  # Error status
    running_status: int = 0  # Running status (byte position: 1028, 0=idle, non-0=moving)
    drag_status: int = 0  # Drag status (0:not dragging, 1:joint drag, 2:force control drag)
    jog_status: int = 0  # Jog status
    robot_type: int = 0  # Robot model
    
    # IO status
    digital_inputs: int = 0  # Digital inputs (64-bit)
    digital_outputs: int = 0  # Digital outputs (64-bit)
    safety_io_in: int = 0  # Safety IO input
    safety_io_out: int = 0  # Safety IO output
    
    # Time information
    timestamp: int = 0  # Unix timestamp (ms)
    run_time: int = 0  # Power-on runtime (ms)
    
    # Electrical information
    voltage: float = 0.0  # Robot voltage
    current: float = 0.0  # Robot current
    
    # Program status
    program_state: float = 0.0  # Script running status
    
    # Current command ID
    current_command_id: int = 0
    
    # Joint state
    joint_state: JointState = field(default_factory=JointState)
    
    # Cartesian pose
    tool_vector_actual: CartesianPose = field(default_factory=CartesianPose)
    tool_vector_target: CartesianPose = field(default_factory=CartesianPose)
    tcp_speed_actual: CartesianPose = field(default_factory=CartesianPose)  # TCP actual speed
    tcp_speed_target: CartesianPose = field(default_factory=CartesianPose)  # TCP target speed
    
    # Force information
    actual_tcp_force: List[float] = field(default_factory=lambda: [0.0] * 6)  # TCP force per axis (six-axis calculation)
    tcp_force: List[float] = field(default_factory=lambda: [0.0] * 6)  # TCP force values (joint current calculation)
    
    # Load information
    load: float = 0.0  # End-effector load weight (kg)
    load_center_x: float = 0.0  # Load X offset (mm)
    load_center_y: float = 0.0  # Load Y offset (mm)
    load_center_z: float = 0.0  # Load Z offset (mm)
    
    # Coordinate system
    user_coordinate: int = 0  # User coordinate system index
    tool_coordinate: int = 0  # Tool coordinate system index
    user_value: List[float] = field(default_factory=lambda: [0.0] * 6)  # User coordinate system values
    tool_value: List[float] = field(default_factory=lambda: [0.0] * 6)  # Tool coordinate system values
    
    # Quaternion
    target_quaternion: Quaternion = field(default_factory=Quaternion)  # Target quaternion
    actual_quaternion: Quaternion = field(default_factory=Quaternion)  # Actual quaternion
    
    # Velocity/acceleration ratio
    velocity_ratio: int = 0  # Joint velocity ratio (0-100)
    acceleration_ratio: int = 0  # Joint acceleration ratio (0-100)
    xyz_velocity_ratio: int = 0  # Cartesian position velocity ratio (0-100)
    r_velocity_ratio: int = 0  # Cartesian orientation velocity ratio (0-100)
    xyz_acceleration_ratio: int = 0  # Cartesian position acceleration ratio (0-100)
    r_acceleration_ratio: int = 0  # Cartesian orientation acceleration ratio (0-100)
    
    # Queue status
    run_queued_cmd: int = 0  # Algorithm queue running flag
    pause_cmd_flag: int = 0  # Algorithm queue pause flag
    
    # Hand type
    hand_type: List[int] = field(default_factory=lambda: [0] * 4)  # Hand type (reserved parameter)
    
    # End-effector button signals
    drag_button_signal: int = 0  # Drag button signal
    enable_button_signal: int = 0  # Enable button signal
    record_button_signal: int = 0  # Record button signal
    reappear_button_signal: int = 0  # Reappear button signal
    jaw_button_signal: int = 0  # Gripper control signal
    
    # Six-axis force sensor
    six_force_online: int = 0  # Six-axis force online status (0:offline, 1:online, 2:abnormal)
    six_force_value: List[float] = field(default_factory=lambda: [0.0] * 6)  # Six-axis force raw values
    
    # Safety status
    collision_state: int = 0  # Collision state
    arm_approach_state: int = 0  # Arm safety skin proximity pause
    j4_approach_state: int = 0  # J4 safety skin proximity pause
    j5_approach_state: int = 0  # J5 safety skin proximity pause
    j6_approach_state: int = 0  # J6 safety skin proximity pause
    safety_state: int = 0  # Safety state (bitmask)
    
    # Vibration detection
    vibration_dis_z: float = 0.0  # Z-axis vibration displacement
    
    # Mode
    auto_manual_mode: int = 0  # Manual/Auto mode
    export_status: int = 0  # USB export status
    
    def is_ready(self) -> bool:
        """Check if robot is ready"""
        return (
            self.robot_mode == RobotMode.ENABLE and
            not self.error_status and
            self.enable_status
        )
    
    def has_error(self) -> bool:
        """Check if there is an error"""
        return self.robot_mode == RobotMode.ERROR or self.error_status
    
    def is_moving(self) -> bool:
        """Check if robot is moving
        
        RunningStatus byte position: 1028
        Status value description:
        - 0: Idle
        - Non-0: Moving (refer to protocol documentation for specific values)
        """
        return self.running_status != 0
    
    def get_safety_state_desc(self) -> str:
        """Get safety state description"""
        states = []
        if self.safety_state & 0x01: states.append("Emergency stop")
        if self.safety_state & 0x02: states.append("Protective stop")
        if self.safety_state & 0x04: states.append("Reduced mode")
        if self.safety_state & 0x08: states.append("Not stopped")
        if self.safety_state & 0x10: states.append("Moving")
        if self.safety_state & 0x20: states.append("System emergency stop")
        if self.safety_state & 0x40: states.append("User emergency stop")
        if self.safety_state & 0x80: states.append("Safety origin")
        return ", ".join(states) if states else "Normal"
