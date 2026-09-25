# -*- coding: utf-8 -*-
"""
Example 9: Flange Pose for Robotics Toolbox for Python (RTB)

Reads the robot flange (tool coordinate system 0) pose expressed in the
world / user coordinate system 0 and returns it as:

  - spatialmath.SE3  — homogeneous transform (easy for RTB fkine / pose math)
  - spatialmath.UnitQuaternion — orientation as [w, x, y, z]

Two data paths are shown:

  1. On-demand (primary): GetPose(user=0, tool=0) over the dashboard port.
     Always world + flange, independent of the currently selected User/Tool.
     Dobot Euler angles (deg) use fixed-axis X→Y→Z, i.e. R = Rz(rz)·Ry(ry)·Rx(rx),
     which matches spatialmath SE3.RPY(..., order='zyx').

  2. Real-time (feedback): status.tool_vector_actual + status.actual_quaternion
     from the 8 ms feedback stream (or tool_vector_target + target_quaternion
     for the commanded target pose via get_target_flange_pose_feedback()).
     The frame follows the *currently selected* User/Tool — call User(0) and
     Tool(0) first so the frame is world + flange.

Units: translation defaults to meters (RTB convention); pass unit='mm' to keep
native Dobot millimeters.

Optional dependency:
    pip install roboticstoolbox-python   # pulls spatialmath-python
    # or: pip install spatialmath-python
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dobot_sdk import DobotRobot


def parse_pose_response(response: str):
    """Parse GetPose response: 'ErrorID,{x,y,z,rx,ry,rz},GetPose(...);'

    Returns:
        list[float]: [x, y, z, rx, ry, rz] in mm and degrees
    Raises:
        ValueError: if the response does not contain 6 numbers
    """
    start = response.find("{")
    end = response.find("}", start + 1)
    if start == -1 or end == -1:
        raise ValueError(f"Malformed GetPose response: {response!r}")
    payload = response[start + 1 : end]
    values = [float(v.strip()) for v in payload.split(",") if v.strip()]
    if len(values) != 6:
        raise ValueError(f"Expected 6 pose values, got {len(values)}: {response!r}")
    return values


def _scale_translation(xyz, unit: str):
    if unit == "m":
        return [v / 1000.0 for v in xyz]
    if unit == "mm":
        return list(xyz)
    raise ValueError("unit must be 'm' or 'mm'")


def get_flange_pose(robot, user: int = 0, tool: int = 0, unit: str = "m"):
    """Flange pose in world coordinates via on-demand GetPose (primary path).

    Args:
        robot: connected DobotRobot (RequestControl already done)
        user: user coordinate index (0 = world)
        tool: tool coordinate index (0 = flange / default tool)
        unit: 'm' (default, meters) or 'mm'

    Returns:
        (SE3, UnitQuaternion): pose of the flange frame relative to world,
        and the same orientation as a unit quaternion [w, x, y, z].
    """
    from spatialmath import SE3, UnitQuaternion

    raw = robot.robot_control.GetPose(user=user, tool=tool)
    x, y, z, rx, ry, rz = parse_pose_response(raw)
    x, y, z = _scale_translation([x, y, z], unit)

    # Dobot fixed-axis X→Y→Z  ≡  R = Rz(rz)·Ry(ry)·Rx(rx)
    T = SE3(x, y, z) * SE3.RPY(rx, ry, rz, unit="deg", order="zyx")
    q = UnitQuaternion(T.R)
    return T, q


def get_flange_pose_feedback(robot, unit: str = "m"):
    """Flange pose from the real-time feedback stream (8 ms) — actual values.

    Requires User(0) and Tool(0) to be active so the reported frame is
    world + flange. Otherwise the pose is in whatever User/Tool is selected.

    Returns:
        (SE3, UnitQuaternion): same signature as get_flange_pose().
        Raises RuntimeError if feedback monitoring has not produced status yet.
    """
    from spatialmath import SE3, UnitQuaternion

    status = robot.GetStatus()
    if status is None:
        raise RuntimeError(
            "No feedback status yet — call robot.StartFeedbackMonitor() first"
        )

    pose = status.tool_vector_actual
    x, y, z = _scale_translation([pose.x, pose.y, pose.z], unit)

    quat = status.actual_quaternion  # [qw, qx, qy, qz]
    q = UnitQuaternion([quat.qw, quat.qx, quat.qy, quat.qz])
    T = SE3(x, y, z) * q.SE3()
    return T, q


def get_target_flange_pose_feedback(robot, unit: str = "m"):
    """Target (commanded) flange pose from the real-time feedback stream.

    Same frame rules as get_flange_pose_feedback(): User(0) and Tool(0)
    should be active for world + flange. Uses tool_vector_target and
    target_quaternion from the feedback packet (see 07_status_monitor.py).

    Returns:
        (SE3, UnitQuaternion): target flange pose and orientation [w, x, y, z].
        Raises RuntimeError if feedback monitoring has not produced status yet.
    """
    from spatialmath import SE3, UnitQuaternion

    status = robot.GetStatus()
    if status is None:
        raise RuntimeError(
            "No feedback status yet — call robot.StartFeedbackMonitor() first"
        )

    pose = status.tool_vector_target
    x, y, z = _scale_translation([pose.x, pose.y, pose.z], unit)

    quat = status.target_quaternion  # [qw, qx, qy, qz]
    q = UnitQuaternion([quat.qw, quat.qx, quat.qy, quat.qz])
    T = SE3(x, y, z) * q.SE3()
    return T, q


def _print_pose(label: str, T, q, unit: str = "m"):
    unit_str = "m" if unit == "m" else "mm"
    print(f"\n[{label}]")
    print(f"  position ({unit_str}): [{T.t[0]:.6f}, {T.t[1]:.6f}, {T.t[2]:.6f}]")
    print(f"  quaternion [w,x,y,z]: [{q.A[0]:.6f}, {q.A[1]:.6f}, {q.A[2]:.6f}, {q.A[3]:.6f}]")
    print("  SE3:")
    print(np_array_str(T.A))


def np_array_str(A):
    lines = []
    for row in A:
        lines.append("    [" + ", ".join(f"{v:9.5f}" for v in row) + "]")
    return "\n".join(lines)


def main():
    ROBOT_IP = "192.168.100.51"
    UNIT = "m"  # meters for RTB; set to "mm" for native Dobot units

    try:
        from spatialmath import SE3
    except ImportError:
        print(
            "This example requires spatialmath-python.\n"
            "  pip install spatialmath-python\n"
            "  # or: pip install roboticstoolbox-python"
        )
        return

    try:
        with DobotRobot(ROBOT_IP) as robot:
            print("=" * 50)
            print("9. Flange Pose for Robotics Toolbox (SE3 + quaternion)")
            print("=" * 50)

            robot.robot_control.RequestControl()
            robot.robot_control.ClearError()

            # --- Primary path: on-demand GetPose(user=0, tool=0) ---
            print("\n--- On-demand GetPose (user=0, tool=0) ---")
            T, q = get_flange_pose(robot, user=0, tool=0, unit=UNIT)
            _print_pose("GetPose flange in world", T, q, UNIT)

            # --- Real-time path: feedback quaternion ---
            print("\n--- Feedback (8 ms stream) ---")
            robot.robot_control.User(0)   # world frame
            robot.robot_control.Tool(0)   # flange / default tool
            robot.StartFeedbackMonitor()

            # Give the monitor a moment to receive a packet
            import time

            deadline = time.time() + 2.0
            while robot.GetStatus() is None and time.time() < deadline:
                time.sleep(0.05)

            try:
                T_fb, q_fb = get_flange_pose_feedback(robot, unit=UNIT)
                _print_pose("Feedback flange in world (actual)", T_fb, q_fb, UNIT)

                T_tgt, q_tgt = get_target_flange_pose_feedback(robot, unit=UNIT)
                _print_pose("Feedback flange in world (target)", T_tgt, q_tgt, UNIT)
            except RuntimeError as e:
                print(f"  Feedback path skipped: {e}")
            finally:
                robot.StopFeedbackMonitor()

            # --- Minimal RTB usage demo ---
            print("\n--- RTB usage hint ---")
            print("  T, q = get_flange_pose(robot)")
            print("  T, q = get_target_flange_pose_feedback(robot)")
            print("  T * SE3.Trans(0, 0, 0.1)   # 100 mm along flange Z")
            print("  q.A                        # ndarray [w, x, y, z]")
            offset = T * SE3.Trans(0, 0, 0.1)
            print(f"  example offset position ({UNIT}): {offset.t}")

            # robot.robot_control.DisableRobot()
            print("\n" + "=" * 50)
            print("Flange pose example completed")
            print("=" * 50)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
