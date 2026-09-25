# -*- coding: utf-8 -*-
"""
Check Camera Calibration Positions

Visits each recorded camera-calibration pose so you can verify the camera
view / alignment at every position.

Movement method:
    MovJ(pose, CoordinateType.CARTESIAN) — an absolute move to a Cartesian
    target [x, y, z, rx, ry, rz] (mm / deg) in the user coordinate system.
    MovJ lets the controller plan the joint path to each absolute pose,
    which is safer for arbitrary calibration points than a straight-line
    MovL (less chance of singularity / joint-limit errors).

    MovJ is a queued command (returns when accepted, not when finished),
    so each move is followed by a blocking wait on the feedback stream
    (running_status / is_moving()), then a prompt: press ENTER to proceed
    to the next position.

Requires StartFeedbackMonitor() so GetStatus() receives the 8 ms packets.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dobot_sdk import DobotRobot, CoordinateType


POSITION_1 = [5.6989, -422.6, 374.6, 165.6, 2.181, 179.9]
POSITION_2 = [-112.8, -277.4, 354.9, 176.8, 18.7145, 160.2]
POSITION_3 = [107.4, -348.1, 397.6, 175.7, -10.3037, -154.502]
POSITION_4 = [27.1113, -339.4, 392.5, -179.358, -0.7155, -163.299]

POSITIONS = [
    ("Position 1", POSITION_1),
    ("Position 2", POSITION_2),
    ("Position 3", POSITION_3),
    ("Position 4", POSITION_4),
]


def wait_for_motion_complete(robot, timeout: float = 30.0,
                             start_timeout: float = 5.0,
                             poll_period: float = 0.05) -> bool:
    """Block until robot finishes the current motion (pattern from example 10).

    Args:
        robot: connected DobotRobot with feedback monitor running
        timeout: max seconds to wait for motion to finish
        start_timeout: max seconds to wait for motion to start
                       (skipped if already moving)
        poll_period: seconds between status polls

    Returns:
        True if motion completed (became idle), False on timeout.
    """
    deadline = time.time() + start_timeout
    while time.time() < deadline:
        status = robot.GetStatus()
        if status is not None and status.is_moving():
            break
        time.sleep(poll_period)
    else:
        status = robot.GetStatus()
        if status is None or not status.is_moving():
            print("[WAIT] Motion never started (already idle?)")
            return True

    deadline = time.time() + timeout
    while time.time() < deadline:
        status = robot.GetStatus()
        if status is not None and not status.is_moving():
            return True
        time.sleep(poll_period)

    return False


def move_to(robot, label: str, pose, timeout: float = 30.0) -> bool:
    """Move to an absolute Cartesian pose and block until the robot arrives.

    Args:
        robot: connected DobotRobot (RequestControl done, feedback on)
        label: display name of the target position
        pose: [x, y, z, rx, ry, rz] in mm / degrees (user coordinate system)
        timeout: max wait for motion completion (seconds)

    Returns:
        True if the move completed, False on timeout.
    """
    if len(pose) != 6:
        raise ValueError(f"{label}: pose requires 6 values [x,y,z,rx,ry,rz]")

    print(f"\n--- {label} ---")
    print(f"  target: {pose}")
    response = robot.motion.MovJ(pose, CoordinateType.CARTESIAN)
    print(f"  MovJ response: {response}")

    ok = wait_for_motion_complete(robot, timeout=timeout)
    if not ok:
        print(f"[TIMEOUT] {label} not reached within {timeout}s")
        return False

    status = robot.GetStatus()
    if status is not None:
        p = status.tool_vector_actual
        print(f"  actual: X={p.x:.2f} Y={p.y:.2f} Z={p.z:.2f} mm | "
              f"Rx={p.rx:.2f} Ry={p.ry:.2f} Rz={p.rz:.2f} deg")
    return True


def main():
    ROBOT_IP = "192.168.100.51"

    try:
        with DobotRobot(ROBOT_IP) as robot:
            print("=" * 50)
            print("Check Camera Calibration Positions")
            print("=" * 50)

            robot.robot_control.RequestControl()
            robot.robot_control.ClearError()
            robot.robot_control.EnableRobot(load=1.0)
            robot.robot_control.SpeedFactor(10)

            # Resolve poses in world frame + flange
            robot.robot_control.User(0)
            robot.robot_control.Tool(0)

            # Required for wait_for_motion_complete()
            robot.StartFeedbackMonitor()
            time.sleep(0.5)

            for label, pose in POSITIONS:
                if not move_to(robot, label, pose):
                    print("Stopping sequence on timeout")
                    break
                input(f"  {label} reached — check the camera, press ENTER "
                      f"for the next position... ")

            print("\nStopping monitor / disabling robot...")
            robot.StopFeedbackMonitor()
            robot.robot_control.DisableRobot()

            print("\n" + "=" * 50)
            print("Camera calibration position check completed")
            print("=" * 50)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
