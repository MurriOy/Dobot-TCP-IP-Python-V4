# -*- coding: utf-8 -*-
"""
Example 10: Blocking RelMovLTool

RelMovLTool is a queued (async) command — it returns as soon as the robot
accepts the move, not when the move finishes. This example wraps it so it
blocks until the robot is idle again, using the feedback stream:

  running_status == 0    -> idle (motion finished)
  running_status != 0    -> moving

Requires StartFeedbackMonitor() so GetStatus() receives the 8 ms packets.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dobot_sdk import DobotRobot, CoordinateType


def wait_for_motion_complete(robot, timeout: float = 30.0,
                             start_timeout: float = 5.0,
                             poll_period: float = 0.05) -> bool:
    """Block until robot finishes the current motion (pattern from example 08).

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
        # Never started (or already idle the whole time)
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


def rel_movl_tool_blocking(robot, offset, timeout: float = 30.0,
                           start_timeout: float = 5.0,
                           **kwargs) -> bool:
    """Send RelMovLTool and block until the robot arrives (idle).

    Args:
        robot: connected DobotRobot (RequestControl done, feedback on)
        offset: [dx, dy, dz, drx, dry, drz] in mm / degrees (tool frame)
        timeout: max wait for motion completion (seconds)
        start_timeout: max wait for motion to start (seconds)
        **kwargs: forwarded to robot.motion.RelMovLTool
                  (user, tool, a, v, speed, cp, r)

    Returns:
        True if the move completed, False on timeout.
    """
    if len(offset) != 6:
        raise ValueError("offset requires 6 values [dx,dy,dz,drx,dry,drz]")

    response = robot.motion.RelMovLTool(
        offset[0], offset[1], offset[2],
        offset[3], offset[4], offset[5],
        **kwargs,
    )
    print(f"  RelMovLTool response: {response}")

    ok = wait_for_motion_complete(
        robot, timeout=timeout, start_timeout=start_timeout
    )
    if ok:
        print("[OK] Move complete")
    else:
        print(f"[TIMEOUT] Move did not finish within {timeout}s")
    return ok


def _print_pose(status):
    if status is None:
        return
    p = status.tool_vector_actual
    print(f"  pose: X={p.x:.2f} Y={p.y:.2f} Z={p.z:.2f} mm | "
          f"Rx={p.rx:.2f} Ry={p.ry:.2f} Rz={p.rz:.2f} deg")


def main():
    ROBOT_IP = "192.168.100.51"

    try:
        with DobotRobot(ROBOT_IP) as robot:
            print("=" * 50)
            print("10. Blocking RelMovLTool Example")
            print("=" * 50)

            robot.robot_control.RequestControl()
            robot.robot_control.ClearError()
            robot.robot_control.EnableRobot(load=1.0)
            robot.robot_control.SpeedFactor(10)

            # Feedback is required for wait_for_motion_complete()
            robot.StartFeedbackMonitor()
            time.sleep(0.5)

            # --- Move to a known start pose (async + blocking wait) ---
            print("\n--- Move to start pose ---")
            start_pose = [0, -350, 350, -180, 0, -180]
            print(f"  MovJ start: {start_pose}")
            robot.motion.MovJ(start_pose, CoordinateType.CARTESIAN)
            if not wait_for_motion_complete(robot, timeout=20.0):
                print("  Failed to reach start pose — aborting")
                robot.StopFeedbackMonitor()
                robot.robot_control.DisableRobot()
                return
            _print_pose(robot.GetStatus())

            # --- Blocking relative moves along tool axes ---
            steps = [
                ("+50 mm along tool Z", [0, 0, 50, 0, 0, 0]),
                ("-50 mm along tool Y", [0, -50, 0, 0, 0, 0]),
                ("+30 mm along tool X", [30, 0, 0, 0, 0, 0]),
                ("return (inverse of all)", [-30, 50, -50, 0, 0, 0]),
            ]

            for label, offset in steps:
                print(f"\n--- RelMovLTool: {label} ---")
                print(f"  offset: {offset}")
                completed = rel_movl_tool_blocking(
                    robot, offset, timeout=30.0, start_timeout=5.0
                )
                if not completed:
                    print("  Stopping sequence on timeout")
                    break
                _print_pose(robot.GetStatus())
                time.sleep(0.2)

            # --- Teardown ---
            print("\nStopping monitor / disabling robot...")
            robot.StopFeedbackMonitor()
            robot.robot_control.DisableRobot()

            print("\n" + "=" * 50)
            print("Blocking RelMovLTool example completed")
            print("=" * 50)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
