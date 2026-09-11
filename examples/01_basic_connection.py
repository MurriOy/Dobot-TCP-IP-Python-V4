"""
Example 1: Basic Connection and Enabling

Demonstrates how to connect to the robot, enable it, set parameters, and safely shut down
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dobot_sdk import DobotRobot
import time


def main():
    # Robot IP address (modify according to actual setup)
    ROBOT_IP = "192.168.5.1"
    
    # Using context manager (recommended approach)
    try:
        with DobotRobot(ROBOT_IP) as robot:
            print("=" * 50)
            print("1. Connection successful")
            print("=" * 50)
            
            # Request TCP control mode
            print("Requesting TCP control mode...")
            response = robot.robot_control.RequestControl()
            print(f"Response: {response}")
            
            # Clear alarms (if any)
            print("Clearing alarms...")
            robot.robot_control.ClearError()
            
            # Enable robot (set 1kg load)
            print("Enabling robot...")
            response = robot.robot_control.EnableRobot(load=1.0)
            print(f"Response: {response}")
            
            # Set global speed ratio
            speed = 50
            print(f"Setting global speed to {speed}%...")
            robot.robot_control.SpeedFactor(speed)
            
            # Get robot status
            print("\nGetting robot status...")
            mode = robot.robot_control.RobotMode()
            print(f"Robot mode: {mode}")
            
            # Wait 2 seconds
            print(f"\nWaiting {2} seconds...")
            time.sleep(2)
            
            # Disable robot
            print("\nDisabling robot...")
            response = robot.robot_control.DisableRobot()
            print(f"Response: {response}")
            
            print("\n" + "=" * 50)
            print("Basic connection example completed")
            print("=" * 50)
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
