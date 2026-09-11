"""
Servo control test

Demonstrate ServoP dynamic following functionality, generate circular motion trajectory
"""

import sys
import os

# Add parent directory to path for importing dobot_sdk
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import time
from dobot_sdk import DobotRobot
from dobot_sdk import CoordinateType


def parse_dobot_response(response_str: str) -> tuple:
    """Parse string format data returned by Dobot, extract each part

    Format example: 'part1,{1,2,3},part3'

    Args:
        response_str: String to parse

    Returns:
        tuple: (prefix, number list, suffix), returns None if parsing fails
    """
    first_comma_idx = response_str.find(',')
    if first_comma_idx == -1:
        return None

    prefix = response_str[:first_comma_idx]
    remaining = response_str[first_comma_idx + 1:]

    if not remaining.startswith('{'):
        return None

    brace_depth = 1
    i = 1
    while i < len(remaining) and brace_depth > 0:
        if remaining[i] == '{':
            brace_depth += 1
        elif remaining[i] == '}':
            brace_depth -= 1
        i += 1

    if brace_depth != 0:
        return None

    middle_with_braces = remaining[:i]
    suffix = remaining[i + 1:] if i < len(remaining) else ""

    numbers_str = middle_with_braces[1:-1]
    number_list = [float(x.strip()) for x in numbers_str.split(',')]

    return prefix, number_list, suffix


def generate_circular_trajectory(radius: float, num_points: int) -> list:
    """Generate circular motion trajectory points

    Args:
        radius: Circular radius (mm)
        num_points: Number of trajectory points

    Returns:
        list: List of trajectory points, each point is [x, y, z, rx, ry, rz]
    """
    trajectory_points = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        trajectory_points.append([x, y, 0, 0, 0, 0])
    return trajectory_points

def generate_circle_smooth(radius=50, total_points=300):
    points = []
    for i in range(total_points):
        s = i / (total_points - 1)
        angle = 2 * math.pi * (0.5 - 0.5 * math.cos(math.pi * s))
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        points.append([x, y, 0, 0, 0, 0])
    return points

def execute_trajectory_at_frequency(robot, trajectory_points, frequency_hz: float):
    """Execute trajectory point sequence at specified frequency

    Args:
        robot: DobotRobot instance
        trajectory_points: List of trajectory points
        frequency_hz: Execution frequency (Hz)
    """
    start_time = time.time()
    interval = 1.0 / frequency_hz

    for i, target_point in enumerate(trajectory_points):
        expected_time = start_time + (i + 1) * interval
        cycle_start = time.time()

        # Use new SDK ServoP interface
        robot.motion.ServoP(target_point)

        cycle_duration = time.time() - cycle_start
        current_time = time.time()
        delay_needed = expected_time - current_time

        if delay_needed > 0:
            time.sleep(delay_needed)
        else:
            print(f"Cycle {i + 1} timeout {-delay_needed:.3f} seconds")

def wait_for_robot_ready(robot, target_state=5.0, polling_interval=0.1):
    """Wait for robot to reach ready state

    Args:
        robot: DobotRobot instance
        target_state: Target state value
        polling_interval: Polling interval (seconds)
    """
    while True:
        status_response = robot.robot_control.RobotMode()
        parsed = parse_dobot_response(status_response)

        if parsed is None:
            print("Robot state parsing failed")
            time.sleep(polling_interval)
            continue

        _, state_data, _ = parsed

        if state_data and state_data[0] == target_state:
            print(f"Robot ready, state: {state_data}")
            break

        time.sleep(polling_interval)


def main():
    # Modify to actual robot IP
    ROBOT_IP = "192.168.5.1"
    
    try:
        with DobotRobot(ROBOT_IP) as robot:
            print("=" * 50)
            print("Servo Control Test - Circular Trajectory Following")
            print("=" * 50)
            
            # Initialize
            robot.robot_control.RequestControl()
            robot.robot_control.ClearError()
            robot.robot_control.EnableRobot(load=1.0)
            
            # Activate user coordinate system 0
            robot.robot_control.User(0)
            
            # Get current position
            pose_response = robot.robot_control.GetPose()
            parsed_pose = parse_dobot_response(pose_response)

            if parsed_pose is None:
                print("Error: Position information parsing failed")
                return

            _, current_position, _ = parsed_pose
            print(f"Current position: {current_position}")

            # Set user coordinate system 1 (using current position as origin)
            set_user_result = robot.robot_control.SetUser(1, current_position)
            print(f"Set user coordinate system result: {set_user_result}")

            # Switch to user coordinate system 1
            robot.robot_control.User(1)

            # Move to trajectory starting point (relative position in user coordinate system)
            start_point = [50, 0, 0, 0, 0, 0]
            print(f"\nMoving to trajectory starting point: {start_point}")
            robot.motion.MovL(start_point, CoordinateType.CARTESIAN)
            time.sleep(3)

            # Wait for robot to be ready
            wait_for_robot_ready(robot)

            # Generate circular trajectory
            # trajectory_points = generate_circular_trajectory(radius=50, num_points=300)
            trajectory_points = generate_circle_smooth(radius=50, total_points=300)
            print(f"\nGenerated {len(trajectory_points)} trajectory points")

            # Execute trajectory control
            print("Starting trajectory control execution...")
            execute_trajectory_at_frequency(robot, trajectory_points, frequency_hz=33.0)

            print("\nTrajectory execution completed")

    except KeyboardInterrupt:
        print("\nUser interrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
