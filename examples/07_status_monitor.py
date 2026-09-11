# -*- coding: utf-8 -*-
"""
Example 7: Complete Status Monitoring

Displays all fields parsed from the Feedback data packet
"""

import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dobot_sdk import DobotRobot, set_log_level


def print_status(status):
    """
    Print complete robot status information
    
    Args:
        status: RobotStatus object
    """
    # Focus on RunningStatus
    running_status = status.running_status
    
    # RunningStatus values (based on protocol documentation)
    # 0: Idle
    # 1028: Moving
    # Other values defined based on actual conditions
    
    status_text = "Unknown"
    status_icon = ""
    if running_status == 0:
        status_text = "Idle"
        status_icon = "[OK]"
    elif running_status == 1028:
        status_text = "Moving"
        status_icon = "[RUN]"
    else:
        status_text = f"Status code: {running_status}"
        status_icon = "[WARN]"
    
    print(f"\n{'='*60}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # Running status
    print(f"\n[Running Status]")
    print(f"  RunningStatus: {status_icon} {status_text}")
    print(f"  Robot mode: {status.robot_mode.name}")
    print(f"  Enable status: {'Enabled' if status.enable_status else 'Disabled'}")
    print(f"  Brake status: {'Released' if status.brake_status else 'Engaged'}")
    print(f"  Error status: {'Has error' if status.error_status else 'Normal'}")
    print(f"  Speed ratio: {status.speed_scaling:.1f}%")
    print(f"  Drag status: {status.drag_status} (0:not dragging, 1:joint drag, 2:force control drag)")
    print(f"  Robot model: {status.robot_type}")
    
    # Cartesian coordinates
    print(f"\n[Cartesian Coordinates]")
    print(f"  X: {status.tool_vector_actual.x:.2f} mm")
    print(f"  Y: {status.tool_vector_actual.y:.2f} mm")
    print(f"  Z: {status.tool_vector_actual.z:.2f} mm")
    print(f"  Rx: {status.tool_vector_actual.rx:.2f} degrees")
    print(f"  Ry: {status.tool_vector_actual.ry:.2f} degrees")
    print(f"  Rz: {status.tool_vector_actual.rz:.2f} degrees")
    
    # TCP velocity
    print(f"\n[TCP Velocity]")
    print(f"  Vx: {status.tcp_speed_actual.x:.2f} mm/s")
    print(f"  Vy: {status.tcp_speed_actual.y:.2f} mm/s")
    print(f"  Vz: {status.tcp_speed_actual.z:.2f} mm/s")
    
    # Joint angles
    print(f"\n[Joint Angles]")
    joint_names = ['J1', 'J2', 'J3', 'J4', 'J5', 'J6']
    for i, (name, angle) in enumerate(zip(joint_names, status.joint_state.q_actual)):
        print(f"  {name}: {angle:.2f} degrees")
    
    # Joint velocity
    print(f"\n[Joint Velocity]")
    for i, (name, speed) in enumerate(zip(joint_names, status.joint_state.qd_actual)):
        print(f"  {name}: {speed:.2f} deg/s")
    
    # Electrical information
    print(f"\n[Electrical Information]")
    print(f"  Voltage: {status.voltage:.2f} V")
    print(f"  Current: {status.current:.2f} A")
    print(f"  Load: {status.load:.2f} kg")
    print(f"  Load center: ({status.load_center_x:.1f}, {status.load_center_y:.1f}, {status.load_center_z:.1f}) mm")
    
    # Motor temperature
    print(f"\n[Motor Temperature]")
    for i, (name, temp) in enumerate(zip(joint_names, status.joint_state.temperatures)):
        print(f"  {name}: {temp:.1f} degrees C")
    
    # IO status
    print(f"\n[IO Status]")
    print(f"  Digital inputs: {bin(status.digital_inputs)}")
    print(f"  Digital outputs: {bin(status.digital_outputs)}")
    print(f"  Safety IO input: {status.safety_io_in}")
    print(f"  Safety IO output: {status.safety_io_out}")
    
    # Velocity/acceleration ratio
    print(f"\n[Velocity/Acceleration Ratio]")
    print(f"  Joint velocity: {status.velocity_ratio}%")
    print(f"  Joint acceleration: {status.acceleration_ratio}%")
    print(f"  Cartesian position velocity: {status.xyz_velocity_ratio}%")
    print(f"  Cartesian orientation velocity: {status.r_velocity_ratio}%")
    print(f"  Cartesian position acceleration: {status.xyz_acceleration_ratio}%")
    print(f"  Cartesian orientation acceleration: {status.r_acceleration_ratio}%")
    
    # Coordinate system
    print(f"\n[Coordinate System]")
    print(f"  User coordinate: {status.user_coordinate}")
    print(f"  Tool coordinate: {status.tool_coordinate}")
    
    # Quaternion
    print(f"\n[Quaternion]")
    print(f"  Target: [{status.target_quaternion.qw:.4f}, {status.target_quaternion.qx:.4f}, {status.target_quaternion.qy:.4f}, {status.target_quaternion.qz:.4f}]")
    print(f"  Actual: [{status.actual_quaternion.qw:.4f}, {status.actual_quaternion.qx:.4f}, {status.actual_quaternion.qy:.4f}, {status.actual_quaternion.qz:.4f}]")
    
    # Safety status
    print(f"\n[Safety Status]")
    print(f"  Safety state: {status.get_safety_state_desc()}")
    print(f"  Collision state: {status.collision_state}")
    print(f"  Arm approach: {status.arm_approach_state}")
    print(f"  J4 approach: {status.j4_approach_state}")
    print(f"  J5 approach: {status.j5_approach_state}")
    print(f"  J6 approach: {status.j6_approach_state}")
    
    # Six-axis force sensor
    print(f"\n[Six-Axis Force Sensor]")
    force_status = {0: 'offline', 1: 'online', 2: 'abnormal'}.get(status.six_force_online, 'unknown')
    print(f"  Online status: {force_status}")
    if status.six_force_online == 1:
        print(f"  Raw values: {[f'{v:.2f}' for v in status.six_force_value]}")
    
    # End effector button signals
    print(f"\n[End Effector Button Signals]")
    print(f"  Drag button: {status.drag_button_signal}")
    print(f"  Enable button: {status.enable_button_signal}")
    print(f"  Record button: {status.record_button_signal}")
    print(f"  Reappear button: {status.reappear_button_signal}")
    print(f"  Jaw button: {status.jaw_button_signal}")
    
    # Command information
    print(f"\n[Command Information]")
    print(f"  Current command ID: {status.current_command_id}")
    print(f"  Run time: {status.run_time // 1000} seconds")
    print(f"  Queue running: {status.run_queued_cmd}")
    print(f"  Queue paused: {status.pause_cmd_flag}")
    
    # Mode
    print(f"\n[Mode]")
    print(f"  Manual/Auto: {status.auto_manual_mode}")
    print(f"  USB export: {status.export_status}")
    
    # Vibration detection
    print(f"\n[Vibration Detection]")
    print(f"  Z-axis vibration displacement: {status.vibration_dis_z:.4f} mm")
    
    print(f"\n{'='*60}")
    print("Press Ctrl+C to stop monitoring")


def main():
    # Set log level (optional)
    set_log_level("INFO")
    
    # Robot IP address
    ROBOT_IP = "192.168.1.100"
    
    print(f"Connecting to robot {ROBOT_IP}...")
    
    # Create robot object with timeout settings
    robot = DobotRobot(
        ROBOT_IP,
        connect_timeout=10.0,
        receive_timeout=15.0
    )
    
    try:
        # Connect to robot
        robot.Connect()
        print("Connection successful!")
        
        # Request control
        robot.robot_control.RequestControl()
        
        # Clear errors
        robot.robot_control.ClearError()
        
        # Start feedback monitoring
        robot.StartFeedbackMonitor(callback=print_status)
        
        print("\nStarting robot status monitoring...")
        print("Press Ctrl+C to stop monitoring\n")
        
        # Continuously monitor
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nUser stopped monitoring")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Stop monitoring and disconnect
        robot.StopFeedbackMonitor()
        robot.Disconnect()
        print("Disconnected")


if __name__ == "__main__":
    main()
