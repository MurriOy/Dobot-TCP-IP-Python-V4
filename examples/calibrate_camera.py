# -*- coding: utf-8 -*-
"""
Calibrate Camera

Runs the full Boreas intrinsic-calibration workflow (mirroring
run_intrinsic_calibration in external_libraries/demo_api_client/client.py)
driven by robot motion instead of manual prompts:

    start_intrinsic_calibration(session)
    get_initial_status(session)
    for each position in check_camera_calibration_positions.POSITIONS:
        move to the absolute position      -> MovJ(pose, CoordinateType.CARTESIAN)
        settle, then collect one frame     -> collect_calibration_frame(session)
    stop_intrinsic_calibration(session, accept=True)
    get_status_after_calibration(session)

Movement method:
    MovJ(pose, CoordinateType.CARTESIAN) — absolute move to a Cartesian target
    [x, y, z, rx, ry, rz] (mm / deg) in the user coordinate system. MovJ lets
    the controller plan the joint path to each absolute pose, which is safer
    for arbitrary calibration points than a straight-line MovL. MovJ is a
    queued command, so each move is followed by a blocking wait on the
    feedback stream (running_status / is_moving()) before the frame is
    captured.

Poses and motion helpers are imported from check_camera_calibration_positions.

Environment:
    ROBOT_IP       robot dashboard IP (default 192.168.100.51)
    VISION_API_URL vision API base URL (default http://localhost:8000)

Requires: requests, bilogger (used by the vision client), camera API running.
"""

import os
import sys
import time

import requests

EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(EXAMPLES_DIR)
CLIENT_DIR = os.path.join(ROOT_DIR, "external_libraries", "demo_api_client")

sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, EXAMPLES_DIR)
sys.path.insert(0, CLIENT_DIR)

from dobot_sdk import DobotRobot, CoordinateType  # noqa: E402,F401
from check_camera_calibration_positions import POSITIONS, move_to  # noqa: E402

try:
    import client as vision_client
except ImportError as e:
    print(f"Failed to import vision API client from {CLIENT_DIR}: {e}")
    print("Ensure 'requests' and 'bilogger' are installed and the vision API "
          "client dependencies are available.")
    sys.exit(1)


ROBOT_IP = os.environ.get("ROBOT_IP", "192.168.100.51")
VISION_API_URL = os.environ.get("VISION_API_URL", "http://localhost:8000")

SETTLE_SECONDS = 1.0  # let the arm settle (vibration) before capturing


def run_calibration(robot, session) -> None:
    """Full intrinsic-calibration workflow with a move before each frame.

    Args:
        robot: connected DobotRobot with feedback monitor running
        session: requests.Session used by the vision API client
    """
    vision_client.start_intrinsic_calibration(session)
    vision_client.get_initial_status(session)

    try:
        for label, pose in POSITIONS:
            if not move_to(robot, label, pose):
                print("Stopping calibration sequence on motion timeout")
                break

            time.sleep(SETTLE_SECONDS)

            print(f"  Collecting calibration frame at {label}...")
            vision_client.collect_calibration_frame(session)
    except KeyboardInterrupt:
        print("\nInterrupted — accepting collected frames")
    finally:
        vision_client.stop_intrinsic_calibration(session, accept=True)
        vision_client.get_status_after_calibration(session)


def main() -> None:
    session = requests.Session()
    vision_client.BASE_URL = VISION_API_URL

    try:
        with DobotRobot(ROBOT_IP) as robot:
            print("=" * 50)
            print("Camera Intrinsic Calibration")
            print("=" * 50)
            print(f"Robot: {ROBOT_IP} | Vision API: {VISION_API_URL}")
            print(f"Positions: {len(POSITIONS)}")

            robot.robot_control.RequestControl()
            robot.robot_control.ClearError()
            robot.robot_control.EnableRobot(load=1.0)
            robot.robot_control.SpeedFactor(10)

            # Resolve poses in world frame + flange
            robot.robot_control.User(0)
            robot.robot_control.Tool(0)

            # Required for move_to()'s blocking wait
            robot.StartFeedbackMonitor()
            time.sleep(0.5)

            try:
                run_calibration(robot, session)
            finally:
                print("\nStopping monitor / disabling robot...")
                robot.StopFeedbackMonitor()
                robot.robot_control.DisableRobot()

            print("\n" + "=" * 50)
            print("Camera calibration completed")
            print("=" * 50)

    except requests.exceptions.ConnectionError:
        print("\nConnection error: ensure the vision API server is running "
              f"on {VISION_API_URL}")
    except requests.exceptions.Timeout:
        print("\nVision API request timeout")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    main()
