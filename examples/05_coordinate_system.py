"""
Example 5: Coordinate System Setup

Demonstrates how to set up and use user and tool coordinate systems
"""

from dobot_sdk import DobotRobot
from dobot_sdk import CoordinateType
import time


def main():
    ROBOT_IP = "192.168.1.100"
    
    try:
        with DobotRobot(ROBOT_IP) as robot:
            print("=" * 50)
            print("5. Coordinate System Setup Example")
            print("=" * 50)
            
            # Initialize
            robot.robot_control.RequestControl()
            robot.robot_control.ClearError()
            robot.robot_control.EnableRobot(load=1.0)
            robot.robot_control.SpeedFactor(30)
            
            # ========== Set User Coordinate System ==========
            print("\n--- Set User Coordinate System ---")
            
            # Create user coordinate system 1 (offset relative to world coordinate system)
            user_pose = [100, 50, 0, 0, 0, 0]  # X offset 100, Y offset 50
            print(f"Setting user coordinate system 1: {user_pose}")
            robot.robot_control.SetUser(1, user_pose)
            
            # Switch to user coordinate system 1
            print("Switching to user coordinate system 1...")
            robot.robot_control.User(1)
            
            # Move in user coordinate system
            print("Moving to (100, 0, 300) in user coordinate system 1...")
            pose_in_user = [100, 0, 300, 180, 0, 0]
            robot.motion.MovJ(pose_in_user, CoordinateType.CARTESIAN)
            time.sleep(3)
            
            # Switch back to world coordinate system
            print("Switching back to world coordinate system...")
            robot.robot_control.User(0)
            
            # ========== Set Tool Coordinate System ==========
            print("\n--- Set Tool Coordinate System ---")
            
            # Create tool coordinate system 1 (end effector length 100mm)
            tool_pose = [0, 0, 100, 0, 0, 0]  # Z direction offset 100mm
            print(f"Setting tool coordinate system 1: {tool_pose}")
            robot.robot_control.SetTool(1, tool_pose)
            
            # Switch to tool coordinate system 1
            print("Switching to tool coordinate system 1...")
            robot.robot_control.Tool(1)
            
            # Move in tool coordinate system
            print("Moving relative in tool coordinate system 1...")
            pose_in_tool = [400, 0, 300, 180, 0, 0]
            robot.motion.MovJ(pose_in_tool, CoordinateType.CARTESIAN)
            time.sleep(3)
            
            # Switch back to default tool coordinate system
            print("Switching back to default tool coordinate system...")
            robot.robot_control.Tool(0)
            
            # ========== Set Payload Parameters ==========
            print("\n--- Set Payload Parameters ---")
            print("Setting payload: 2kg, center of gravity (0, 0, 100)...")
            robot.robot_control.SetPayload(2.0, 0, 0, 100)
            
            # ========== Calculate Coordinate System (Three-Point Method) ==========
            print("\n--- Calculate Coordinate System Demo ---")
            print("Note: Actual use of CalcUser/CalcTool requires teaching points first")
            print("This only demonstrates the API call method")
            
            # Calculate user coordinate system example (requires teaching 3 points first)
            # robot.robot_control.CalcUser(1)  # Requires teaching
            
            # Calculate tool coordinate system example (requires teaching 3 points first)
            # robot.robot_control.CalcTool(1)  # Requires teaching
            
            # ========== Get Current Coordinate System Info ==========
            print("\n--- Get Coordinate System Info ---")
            pose = robot.robot_control.GetPose()
            print(f"Current pose: {pose}")
            
            # Return to safe position
            print("\nReturning to safe position...")
            safe_pose = [0, -30, -60, 0, 90, 0]
            robot.motion.MovJ(safe_pose, CoordinateType.JOINT)
            time.sleep(3)
            
            # Disable robot
            robot.robot_control.DisableRobot()
            
            print("\n" + "=" * 50)
            print("Coordinate system setup example completed")
            print("=" * 50)
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
