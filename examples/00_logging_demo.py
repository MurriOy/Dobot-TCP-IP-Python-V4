# Copyright (c) 2026 Dobot
# Licensed under the MIT License

"""
Logging functionality demo example

Demonstrates how to use the SDK's logging functionality
"""

import sys
sys.path.insert(0, '..')

from dobot_sdk import DobotRobot, CoordinateType, get_logger, set_log_level, get_log_directory


def main():
    # Set log level to DEBUG (optional, default is INFO)
    # Available levels: DEBUG, INFO, WARNING, ERROR
    set_log_level("DEBUG")
    
    # Get logger (can be used for custom log output)
    logger = get_logger()
    
    # Get log directory path
    log_dir = get_log_directory()
    print(f"Log files will be saved to: {log_dir}")
    
    # Create robot object (using example IP here, replace with actual IP for real use)
    robot = DobotRobot("192.168.1.100")
    
    try:
        # Connect to robot (logs will automatically record the connection process)
        robot.Connect()
        
        # Request control mode
        robot.robot_control.RequestControl()
        
        # Clear alarms
        robot.robot_control.ClearError()
        
        # Enable robot (logs will record API calls)
        robot.robot_control.EnableRobot()
        
        # Set speed (logs will record API calls)
        robot.robot_control.SpeedFactor(50)
        
        # Motion commands (logs will record sent commands and responses)
        start_pose = [400, 0, 300, 180, 0, 0]
        robot.motion.MovL(start_pose, CoordinateType.CARTESIAN)
        
        # Disable robot
        robot.robot_control.DisableRobot()
        
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
    finally:
        # Disconnect (logs will record the disconnection process)
        robot.Disconnect()


if __name__ == "__main__":
    main()
