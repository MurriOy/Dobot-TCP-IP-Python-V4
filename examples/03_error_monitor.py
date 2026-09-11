"""
Example 3: Error Code Monitoring and Status Query

Demonstrates how to get robot status, error codes, and other information
"""

from dobot_sdk import DobotRobot
import time


def parse_error_response(response):
    """Parse error code response"""
    # Response format: "ErrorID,{[id,...,id]},GetErrorID();"
    if "ErrorID" in response:
        start = response.find("{") + 1
        end = response.find("}")
        if start > 0 and end > start:
            error_codes_str = response[start:end]
            # Remove internal brackets
            error_codes_str = error_codes_str.strip("[]")
            if error_codes_str.strip():
                return [int(x.strip()) for x in error_codes_str.split(",") if x.strip()]
    return []


def main():
    ROBOT_IP = "192.168.1.100"
    
    try:
        with DobotRobot(ROBOT_IP) as robot:
            print("=" * 50)
            print("3. Error Code Monitoring and Status Query")
            print("=" * 50)
            
            # ========== Get Error Codes ==========
            print("\n--- Get Error Codes ---")
            response = robot.robot_control.GetErrorID()
            print(f"Raw response: {response}")
            
            error_codes = parse_error_response(response)
            if error_codes:
                print(f"\nFound {len(error_codes)} error codes:")
                for code in error_codes:
                    print(f"  - Error code: {code}")
                    print(f"    Please refer to official documentation for details")
            else:
                print("No error codes")
            
            # ========== Get Robot Mode ==========
            print("\n--- Get Robot Mode ---")
            mode = robot.robot_control.RobotMode()
            print(f"Robot mode: {mode}")
            
            # ========== Get Current Pose ==========
            print("\n--- Get Current Cartesian Coordinates ---")
            pose = robot.robot_control.GetPose()
            print(f"Current pose: {pose}")
            
            # ========== Get Joint Angles ==========
            print("\n--- Get Current Joint Angles ---")
            angles = robot.robot_control.GetAngle()
            print(f"Joint angles: {angles}")
            
            # ========== Clear Alarm Demo ==========
            print("\n--- Clear Alarm Demo ---")
            # Note: Only need to clear when there are errors
            if error_codes:
                print("Clearing alarms...")
                robot.robot_control.ClearError()
                # Check again
                response = robot.robot_control.GetErrorID()
                error_codes = parse_error_response(response)
                if not error_codes:
                    print("Alarms cleared")
            
            # ========== Kinematics Calculation Demo ==========
            print("\n--- Kinematics Calculation ---")
            # Forward kinematics: Joint angles -> Cartesian coordinates
            print("Forward kinematics (Joint -> Cartesian)...")
            joints = [0, 0, 0, 0, 90, 0]
            forward_result = robot.robot_control.PositiveKin(joints)
            print(f"Input joints: {joints}")
            print(f"Forward kinematics result: {forward_result}")
            
            # Reachability check
            print("\n--- Linear Motion Reachability Check (CheckOddMovL) ---")
            # CheckOddMovL only supports joint variables, requires start and end joint angles
            joints_start = [0, 0, 90, 0, 0, 0]
            joints_end = [90, 30, 0, 0, 0, 0]
            result = robot.robot_control.CheckOddMovL(joints_start, joints_end)
            print(f"Checking linear motion: {joints_start} -> {joints_end}")
            print(f"Result: {result}")
            
            print("\n--- Arc Motion Reachability Check (CheckOddMovC) ---")
            # CheckOddMovC only supports joint variables, requires start, via, and end joint angles
            joints_via = [60, 30, 0, 0, 0, 0]
            result = robot.robot_control.CheckOddMovC(joints_start, joints_via, joints_end)
            print(f"Checking arc motion: {joints_start} -> {joints_via} -> {joints_end}")
            print(f"Result: {result}")
            
            print("\n" + "=" * 50)
            print("Error monitoring example completed")
            print("=" * 50)
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
