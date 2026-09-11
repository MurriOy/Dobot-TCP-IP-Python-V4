"""
Example 6: Force Control and Conveyor

Demonstrates force sensor control and conveyor tracking functionality
"""

from dobot_sdk import DobotRobot
from dobot_sdk import CoordinateType
import time


def main():
    ROBOT_IP = "120.79.211.106"
    
    try:
        with DobotRobot(ROBOT_IP) as robot:
            print("=" * 50)
            print("6. Force Control and Conveyor Example")
            print("=" * 50)
            
            # Initialize
            robot.robot_control.RequestControl()
            robot.robot_control.ClearError()
            robot.robot_control.EnableRobot(load=1.0)
            robot.robot_control.SpeedFactor(30)
            
            # ========== Force Sensor Control ==========
            print("\n--- Force Sensor Control ---")
            
            # Enable force sensor
            print("Enabling force sensor...")
            response = robot.plugins.EnableFTSensor(1)
            print(f"Response: {response}")
            time.sleep(1)
            
            # Force sensor zeroing
            print("Force sensor zeroing...")
            response = robot.plugins.SixForceHome()
            print(f"Response: {response}")
            time.sleep(1)
            
            # Get force sensor data
            print("Reading force sensor data...")
            for i in range(3):
                force_data = robot.plugins.GetForce()
                print(f"Force data {i+1}: {force_data}")
                time.sleep(0.5)
            
            # Enter force control drag mode
            print("\nEntering force control drag mode...")
            response = robot.plugins.ForceDriveMode(1)
            print(f"Response: {response}")
            print("Waiting 5 seconds, you can manually drag the robot...")
            time.sleep(5)
            
            # Exit force control drag mode
            print("Exiting force control drag mode...")
            response = robot.plugins.ForceDriveMode(0)
            print(f"Response: {response}")
            
            # Disable force sensor
            print("Disabling force sensor...")
            response = robot.plugins.EnableFTSensor(0)
            print(f"Response: {response}")
            
            # ========== Conveyor Control (Demo) ==========
            print("\n--- Conveyor Control ---")
            
            # Note: Actual conveyor use requires encoder configuration first
            print("Enabling conveyor...")
            response = robot.plugins.CnvInit(1)
            print(f"Response: {response}")
            
            # Enable conveyor tracking
            print("Enabling conveyor tracking...")
            response = robot.plugins.StartSyncCnv()
            print(f"Response: {response}")
            
            # Simulate conveyor tracking motion
            print("Waiting for workpiece to enter gripping area...")
            # response = robot.plugins.GetCnvObject(0)
            # print(f"Workpiece detection response: {response}")
            
            print("Stopping conveyor tracking...")
            response = robot.plugins.StopSyncCnv()
            print(f"Response: {response}")
            
            print("Disabling conveyor...")
            response = robot.plugins.CnvInit(0)
            print(f"Response: {response}")
            
            # Return to safe position
            print("\nReturning to safe position...")
            safe_pose = [0, -30, -60, 0, 90, 0]
            robot.motion.MovJ(safe_pose, CoordinateType.JOINT)
            time.sleep(3)
            
            # Disable robot
            robot.robot_control.DisableRobot()
            
            print("\n" + "=" * 50)
            print("Force control and conveyor example completed")
            print("=" * 50)
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
