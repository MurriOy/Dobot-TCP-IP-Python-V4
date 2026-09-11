"""
Conveyor test

Demonstrate the use of conveyor tracking functionality
"""

import sys
import os

# Add parent directory to path for importing dobot_sdk
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dobot_sdk import DobotRobot
from dobot_sdk import CoordinateType
import time


def main():
    # Modify to actual robot IP
    ROBOT_IP = "192.168.5.1"
    
    try:
        with DobotRobot(ROBOT_IP) as robot:
            print("=" * 50)
            print("Conveyor Test")
            print("=" * 50)
            
            # Initialize
            robot.robot_control.RequestControl()
            robot.robot_control.ClearError()
            robot.robot_control.EnableRobot(load=1.0)
            
            # Query robot mode
            mode_response = robot.robot_control.RobotMode()
            print(f"Robot mode: {mode_response}")
            
            while True:
                # Initialize conveyor
                print("\nInitializing conveyor...")
                robot.plugins.CnvInit(1)
                
                # Move to photo/waiting position
                print("Moving to waiting position...")
                robot.motion.MovJ(
                    [-29.3427, -386.0646, 248.1024, 180.0000, -0.0000, -154.3856],
                    CoordinateType.CARTESIAN,
                    user=0, tool=0
                )
                time.sleep(3)
                
                # Poll conveyor for object detection
                print("\nWaiting for object to enter gripping area...")
                while True:
                    cnv_status = robot.plugins.GetCnvObject(0)
                    print(f"Conveyor status: {cnv_status}")
                    
                    # Parse returned status
                    try:
                        # Response format similar to: "GetCnvObject,{status},GetCnvObject();"
                        start = cnv_status.find("{") + 1
                        end = cnv_status.find("}")
                        if start > 0 and end > start:
                            status_values = cnv_status[start:end].split(",")
                            if len(status_values) > 3:
                                object_detected = int(status_values[3])
                                if object_detected == 1:
                                    print("Object detected!")
                                    break
                    except Exception as e:
                        print(f"Parse status failed: {e}")
                    
                    time.sleep(0.2)
                
                # Start synchronized following
                print("\nStarting conveyor synchronization...")
                robot.plugins.StartSyncCnv()
                
                # Execute conveyor following motion
                print("Executing conveyor following motion...")
                robot.plugins.CnvMovL([0, 0, 0, 0, 0, 153])
                time.sleep(2)
                
                # Trigger suction cup or gripper (DO6)
                print("Triggering suction cup...")
                robot.io.DO(6, 1)
                
                # Descend to grip
                print("Descending to grip...")
                robot.plugins.CnvMovL([0, 0, -50, 0, 0, 153])
                time.sleep(3)
                
                # Stop synchronization
                print("Stopping conveyor synchronization...")
                robot.plugins.StopSyncCnv()
                
                # Query robot mode
                mode_response = robot.robot_control.RobotMode()
                print(f"Robot mode: {mode_response}")
                
                # Stop motion
                robot.robot_control.Stop()
                
                # Move to placement position
                print("Moving to placement position...")
                robot.motion.MovL(
                    [212.5693, -395.0977, 209.9998, 179.9999, -0.0001, -154.3857],
                    CoordinateType.CARTESIAN,
                    user=0, tool=0
                )
                time.sleep(3)
                
                # Release suction cup
                robot.io.DO(6, 0)
                
                # Return to standby position
                print("Returning to standby position...")
                robot.motion.MovJ(
                    [-29.3427, -386.0646, 248.1024, 180.0000, -0.0000, -154.3856],
                    CoordinateType.CARTESIAN,
                    user=0, tool=0
                )
                time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nUser interrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
