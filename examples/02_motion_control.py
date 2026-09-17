"""
Example 2: Motion Control

Demonstrates how to use various motion commands
"""

from dobot_sdk import DobotRobot
from dobot_sdk import CoordinateType
import time

def main():
    ROBOT_IP = "192.168.100.51"
    
    try:
        with DobotRobot(ROBOT_IP) as robot:
            print("=" * 50)
            print("2. Motion Control Example")
            print("=" * 50)
            
            # Initialize
            robot.robot_control.RequestControl()
            robot.robot_control.ClearError()
            robot.robot_control.EnableRobot(load=1.0)
            robot.robot_control.SpeedFactor(30)
            
            # Start status monitoring
            robot.StartFeedbackMonitor()
            time.sleep(1)
            
            # ========== Joint Motion (MovJ) ==========
            print("\n--- Joint Motion (MovJ) ---")
            print("Moving to safe position...")
            safe_pose = [0, -30, -60, 0, 90, 0]
            robot.motion.MovJ(safe_pose, CoordinateType.JOINT)
            time.sleep(3)
            
            # ========== Cartesian Motion (MovJ) ==========
            print("\n--- Cartesian Joint Motion (MovJ) ---")
            pose_a = [400, 0, 300, 180, 0, 0]
            print(f"Moving to point A: {pose_a}")
            robot.motion.MovJ(pose_a, CoordinateType.CARTESIAN)
            time.sleep(3)
            
            # ========== Linear Motion (MovL) ==========
            print("\n--- Linear Motion (MovL) ---")
            pose_b = [400, 100, 300, 180, 0, 0]
            print(f"Linearly moving to point B: {pose_b}")
            robot.motion.MovL(pose_b, CoordinateType.CARTESIAN)
            time.sleep(3)
            
            # ========== Arc Motion ==========
            print("\n--- Arc Motion ---")
            pose_via = [450, 150, 300, 180, 0, 0]
            pose_c = [500, 100, 300, 180, 0, 0]
            print(f"Arc motion: B -> Via -> C")
            robot.motion.Arc(pose_via, pose_c, CoordinateType.CARTESIAN)
            time.sleep(3)
            
            # ========== Circle Motion ==========f
            print("\n--- Circle Motion ---")
            print(f"Circle motion: C -> Via -> B")
            robot.motion.Circle(pose_via, pose_b, count=1, coord_type=CoordinateType.CARTESIAN)
            time.sleep(4)
            
            # ========== Relative Motion ==========
            print("\n--- Relative Motion (RelMovLTool) ---")
            offset = [0, -50, 0, 0, 0, 0]
            print(f"Relative offset: {offset}")
            robot.motion.RelMovLTool(offset[0], offset[1], offset[2], offset[3], offset[4], offset[5])
            time.sleep(2)
            
            # ========== Get Current Status ==========
            print("\n--- Get Current Status ---")
            status = robot.GetStatus()
            if status:
                print(f"Current speed ratio: {status.speed_scaling:.1f}%")
                print(f"Current pose:")
                print(f"  X: {status.tool_vector_actual.x:.2f}")
                print(f"  Y: {status.tool_vector_actual.y:.2f}")
                print(f"  Z: {status.tool_vector_actual.z:.2f}")
            
            # Return to safe position
            print("\nReturning to safe position...")
            robot.motion.MovJ(safe_pose, CoordinateType.JOINT)
            time.sleep(3)
            
            # Stop monitoring
            robot.StopFeedbackMonitor()
            robot.robot_control.DisableRobot()
            
            print("\n" + "=" * 50)
            print("Motion control example completed")
            print("=" * 50)
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
