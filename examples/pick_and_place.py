# -*- coding: utf-8 -*-
"""
Pick and Place (vision-driven)

Detects an object on the work plane with the wrist-mounted camera, computes
its world coordinates, and picks it with a suction-cup gripper.

Geometry
--------
- Work plane: Z = WORK_PLANE_Z (90 mm) in the world / User-0 frame. This is
  where objects lie and where the gripper contacts them.
- The camera looks straight down at the plane from FOCUS_DISTANCE (350 mm),
  so the scan height is WORK_PLANE_Z + FOCUS_DISTANCE (440 mm). Scan
  orientation [180, 0, 0] points the camera optical Z axis downward.

Detection -> world
------------------
detect_2d returns the object center as normalized image-plane coordinates
[nx, ny] (already divided by focal length / principal point, so no camera
matrix is needed). At depth d the 3D point in the camera frame is
[nx*d, ny*d, d].

The actual camera pose in world is computed from the actual flange pose
(GetPose(user=0, tool=0), always world + flange) composed with the camera
TCP (T_base<-cam = T_g2b @ T_c2g). The detection ray [nx, ny, 1] is rotated
into the world frame and intersected with the plane Z = WORK_PLANE_Z.

For the ideal perpendicular scan this simplifies to
    obj = [scan_x + 350*nx, scan_y - 350*ny, 90]
but the full ray-plane intersection (using the *actual* camera pose read from
feedback) is used here for accuracy.

Tools
-----
- Camera TCP (index 1): the [x,y,z,rx,ry,rz] printed by
  calibrate_camera_tcp.py (camera optical frame in flange, mm/deg).
- Gripper TCP (index 2): your suction-cup TCP (cup tip in flange, mm/deg).
Both are registered on the controller via SetTool at start.

Prerequisite: intrinsics calibrated (run calibrate_camera.py) and a detection
model created on the vision server.

Environment:
    ROBOT_IP       robot dashboard IP (default 192.168.100.51)
    VISION_API_URL vision API base URL (default http://localhost:8000)

Requires: numpy, scipy, requests, bilogger (vision client), camera API running.
"""

import os
import sys
import time

import numpy as np
import requests
from scipy.spatial.transform import Rotation

EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(EXAMPLES_DIR)
CLIENT_DIR = os.path.join(ROOT_DIR, "external_libraries", "demo_api_client")

sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, EXAMPLES_DIR)
sys.path.insert(0, CLIENT_DIR)

from dobot_sdk import DobotRobot, CoordinateType  # noqa: E402,F401
from check_camera_calibration_positions import (  # noqa: E402
    move_to, wait_for_motion_complete,
)

try:
    import client as vision_client
except ImportError as e:
    print(f"Failed to import vision API client from {CLIENT_DIR}: {e}")
    print("Ensure 'requests' and 'bilogger' are installed and the vision API "
          "client dependencies are available.")
    sys.exit(1)


# ==================== Configuration (adjust to your setup) ====================

ROBOT_IP = os.environ.get("ROBOT_IP", "192.168.100.51")
VISION_API_URL = os.environ.get("VISION_API_URL", "http://localhost:8000")

# Tool coordinate system indices (1-50) registered on the controller.
CAMERA_TOOL_INDEX = 10
GRIPPER_TOOL_INDEX = 11

# Camera TCP: paste the result printed by calibrate_camera_tcp.py
# [x, y, z, rx, ry, rz] in mm / deg (camera optical frame in flange).
CAMERA_TCP = [-79.8088, -1.9769, 48.5972, -2.2512, 0.2884, -89.6780]

# Gripper TCP: your suction-cup TCP [x, y, z, rx, ry, rz] in mm / deg
# (cup contact point in flange).
GRIPPER_TCP = [0.0, 0.0, 83.0, 0.0, 0.0, 0.0]

# Work plane and camera focus
WORK_PLANE_Z = 90.0     # mm, where objects lie / gripper contacts (world Z)
FOCUS_DISTANCE = 300.0  # mm, camera->plane distance
SCAN_Z = WORK_PLANE_Z + FOCUS_DISTANCE  # 440 mm, camera optical-center height
SCAN_X = 0.0            # mm, scan center X (world) -- adjust to your workspace
SCAN_Y = -350.0         # mm, scan center Y (world)
SCAN_ORIENTATION = [-180.0, 0.0, -180.0]   # look straight down (optical Z = -world Z)

# Gripper travel heights (world Z), with the gripper tool active
APPROACH_Z = 150.0      # mm, safe travel / approach height above the plane
PICK_Z = 90.0           # mm, descent height at pick (≈ plane; adjust for cup/object)
PICK_ORIENTATION = [-180.0, 0.0, -180.0]   # gripper pointing down

# Place position (world, with gripper tool active)
PLACE_X = 200.0
PLACE_Y = -350.0
PLACE_Z = 90.0

# Suction control (end-effector ToolDO)
SUCTION_PORT = 0        # ToolDO index (0 or 1)
SUCTION_ON_DELAY = 0.5  # s, let vacuum establish after turning on
SUCTION_OFF_DELAY = 0.3  # s, pause before lifting after release

# Vision detection
MODEL_NAME = "paper_cup"           # must already exist on the vision server
MATCH_THRESHOLD = None          # or a float, e.g. 0.3

# Safe / home pose (world, gripper tool)
SAFE_POSE = [0.0, -300.0, 300.0, -180.0, 0.0, -180.0]

# Persist registered tool frames on the controller (1 = persist, 0 = session only)
SET_TOOL_PERSIST = 1

# Speed
SPEED_FACTOR = 20

# Motion timeouts
MOVE_TIMEOUT = 30.0


# ==================== Pose helpers ====================

def dobot_euler_to_matrix(rx: float, ry: float, rz: float) -> np.ndarray:
    """Dobot fixed-axis Euler R = Rz(rz)Ry(ry)Rx(rx) -> 3x3 (deg input).

    scipy lowercase 'xyz' builds the same R = RzRyRx (verified against
    spatialmath SE3.RPY order='zyx').
    """
    return Rotation.from_euler(
        "xyz", [rx, ry, rz], degrees=True
    ).as_matrix().astype(np.float64)


def parse_get_pose(response: str):
    """Parse GetPose response 'ErrorID,{x,y,z,rx,ry,rz},GetPose(...);'.

    Returns [x, y, z, rx, ry, rz] (mm, deg).
    """
    start = response.find("{")
    end = response.find("}", start + 1)
    if start == -1 or end == -1:
        raise ValueError(f"Malformed GetPose response: {response!r}")
    values = [float(v.strip()) for v in response[start + 1:end].split(",")
              if v.strip()]
    if len(values) != 6:
        raise ValueError(f"Expected 6 pose values, got {len(values)}: {response!r}")
    return values


def read_flange_pose(robot):
    """Actual flange pose in world (User 0 / Tool 0) -> (R 3x3, t 3 mm).

    GetPose(user=0, tool=0) always returns world + flange regardless of the
    currently selected User/Tool.
    """
    raw = robot.robot_control.GetPose(user=0, tool=0)
    x, y, z, rx, ry, rz = parse_get_pose(raw)
    R = dobot_euler_to_matrix(rx, ry, rz)
    t = np.array([x, y, z], dtype=np.float64)
    return R, t


def camera_pose_in_world(R_g2b, t_g2b, camera_tcp):
    """Actual camera optical pose in world from flange pose + camera TCP.

    T_base<-cam = T_g2b @ T_c2g  ->  R_world<-cam, camera center in world.
    """
    R_c2g = dobot_euler_to_matrix(camera_tcp[3], camera_tcp[4], camera_tcp[5])
    t_c2g = np.array(camera_tcp[:3], dtype=np.float64)
    R_wcam = R_g2b @ R_c2g
    c_world = t_g2b + R_g2b @ t_c2g
    return R_wcam, c_world


def back_project_to_world(nx: float, ny: float, R_wcam, c_world,
                          plane_z: float = WORK_PLANE_Z) -> np.ndarray:
    """Intersect the detection ray with the plane Z = plane_z (world, mm).

    Ray in camera frame: [nx, ny, 1] (toward the scene; camera Z = forward).
    """
    r_cam = np.array([nx, ny, 1.0], dtype=np.float64)
    r_world = R_wcam @ r_cam
    if abs(r_world[2]) < 1e-6:
        raise RuntimeError("Camera ray nearly parallel to the work plane; "
                           "check scan orientation / camera TCP")
    s = (plane_z - c_world[2]) / r_world[2]
    return c_world + s * r_world


# ==================== Motion helpers ====================

def movl_and_wait(robot, pose, label: str, timeout: float = MOVE_TIMEOUT) -> bool:
    """Linear move (MovL) to an absolute pose using the active tool; block."""
    print(f"  MovL {label}: {pose}")
    response = robot.motion.MovL(pose, CoordinateType.CARTESIAN)
    print(f"    response: {response}")
    ok = wait_for_motion_complete(robot, timeout=timeout)
    if not ok:
        print(f"  [TIMEOUT] {label} not reached within {timeout}s")
    return ok


# ==================== Workflow ====================

def scan_and_detect(robot, session):
    """Move to scan pose, detect object -> object world position [x, y, z]."""
    print("\n--- Scan (camera tool) ---")
    robot.robot_control.Tool(CAMERA_TOOL_INDEX)
    scan_pose = [SCAN_X, SCAN_Y, SCAN_Z] + list(SCAN_ORIENTATION)
    if not move_to(robot, "scan", scan_pose):
        return None

    # Actual camera pose in world (from real flange pose + camera TCP)
    R_g2b, t_g2b = read_flange_pose(robot)
    R_wcam, c_world = camera_pose_in_world(R_g2b, t_g2b, CAMERA_TCP)
    print(f"  camera center (world): [{c_world[0]:.2f} {c_world[1]:.2f} "
          f"{c_world[2]:.2f}] mm")

    print("\n--- Detect ---")
    body = vision_client.detect_2d(session, MODEL_NAME, MATCH_THRESHOLD)
    if not body.get("success"):
        err = body.get("error", {})
        print(f"  detection failed: {err.get('code')}: {err.get('message')}")
        return None
    detections = body.get("data", {}).get("detections", [])
    if not detections:
        print("  no object detected")
        return None

    det = detections[0]
    nx, ny = det["center"]
    print(f"  detection center (normalized): nx={nx:.4f} ny={ny:.4f}")

    obj = back_project_to_world(nx, ny, R_wcam, c_world)
    print(f"  object (world): [{obj[0]:.2f} {obj[1]:.2f} {obj[2]:.2f}] mm")
    return obj


def pick(robot, obj):
    """Move above the object, descend, engage suction, lift."""
    print("\n--- Pick (gripper tool) ---")
    robot.robot_control.Tool(GRIPPER_TOOL_INDEX)

    approach = [obj[0], obj[1], APPROACH_Z] + list(PICK_ORIENTATION)
    if not move_to(robot, "approach pick", approach):
        return False

    descend = [obj[0], obj[1], PICK_Z] + list(PICK_ORIENTATION)
    if not movl_and_wait(robot, descend, "descend to pick"):
        return False

    print("  suction ON")
    robot.io.ToolDO(SUCTION_PORT, 1)
    time.sleep(SUCTION_ON_DELAY)

    if not movl_and_wait(robot, approach, "lift after pick"):
        return False
    return True


def place(robot):
    """Move to the place position, descend, release, lift."""
    print("\n--- Place (gripper tool) ---")
    approach = [PLACE_X, PLACE_Y, APPROACH_Z] + list(PICK_ORIENTATION)
    if not move_to(robot, "approach place", approach):
        return False

    descend = [PLACE_X, PLACE_Y, PLACE_Z] + list(PICK_ORIENTATION)
    if not movl_and_wait(robot, descend, "descend to place"):
        return False

    print("  suction OFF")
    robot.io.ToolDO(SUCTION_PORT, 0)
    time.sleep(SUCTION_OFF_DELAY)

    if not movl_and_wait(robot, approach, "lift after place"):
        return False
    return True


def main() -> None:
    session = requests.Session()
    vision_client.BASE_URL = VISION_API_URL

    try:
        with DobotRobot(ROBOT_IP) as robot:
            print("=" * 50)
            print("Pick and Place (vision-driven)")
            print("=" * 50)
            print(f"Robot: {ROBOT_IP} | Vision API: {VISION_API_URL}")
            print(f"Work plane Z={WORK_PLANE_Z} mm | Focus={FOCUS_DISTANCE} mm "
                  f"| Scan Z={SCAN_Z} mm")
            print(f"Model: {MODEL_NAME} | Suction ToolDO port: {SUCTION_PORT}")

            robot.robot_control.RequestControl()
            robot.robot_control.ClearError()
            robot.robot_control.EnableRobot(load=1.0)
            robot.robot_control.SpeedFactor(SPEED_FACTOR)

            # Register tool coordinate systems on the controller
            robot.robot_control.SetTool(CAMERA_TOOL_INDEX, CAMERA_TCP,
                                        type=SET_TOOL_PERSIST)
            robot.robot_control.SetTool(GRIPPER_TOOL_INDEX, GRIPPER_TCP,
                                        type=SET_TOOL_PERSIST)

            # Required for move_to()'s / movl_and_wait()'s blocking wait
            robot.StartFeedbackMonitor()
            time.sleep(0.5)

            vision_client.get_initial_status(session)

            try:
                obj = scan_and_detect(robot, session)
                if obj is None:
                    print("\nNothing to pick — finishing.")
                else:
                    if not pick(robot, obj):
                        print("\nPick failed — aborting.")
                    elif not place(robot):
                        print("\nPlace failed — aborting.")
                    else:
                        print("\nPick and place completed.")
            finally:
                # Return to a safe pose (gripper tool) before shutting down
                print("\nReturning to safe pose...")
                robot.robot_control.Tool(GRIPPER_TOOL_INDEX)
                try:
                    move_to(robot, "safe", SAFE_POSE)
                except Exception:
                    pass
                print("\nStopping monitor / disabling robot...")
                robot.StopFeedbackMonitor()
                robot.robot_control.DisableRobot()

            print("\n" + "=" * 50)
            print("Done")
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
