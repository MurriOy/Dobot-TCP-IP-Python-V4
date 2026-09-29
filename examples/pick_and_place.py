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

Logging:
    Configured with logging.config.dictConfig. Console output plus a rotating
    file at <repo>/log/pick_and_place.log (10 files x 10 MB).

Requires: numpy, scipy, requests, bilogger (vision client), camera API running.
"""

import logging
import os
import sys
import time
from logging.config import dictConfig

import numpy as np
import requests
from scipy.spatial.transform import Rotation

EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(EXAMPLES_DIR)
CLIENT_DIR = os.path.join(ROOT_DIR, "external_libraries", "demo_api_client")

sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, EXAMPLES_DIR)
sys.path.insert(0, CLIENT_DIR)


# ==================== Logging (dictConfig) ====================

LOG_DIR = os.path.join(ROOT_DIR, "log")
LOG_FILE = os.path.join(LOG_DIR, "pick_and_place.log")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {"format": "%(message)s"},
        "file": {
            "format": "%(asctime)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "console",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "file",
            "filename": LOG_FILE,
            "maxBytes": 10 * 1024 * 1024,  # 10 MB per file
            "backupCount": 10,             # keep 10 rotated files
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "pick_and_place": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
}


def setup_logging() -> logging.Logger:
    """Configure logging (console + rotating file) and return the script logger."""
    os.makedirs(LOG_DIR, exist_ok=True)
    dictConfig(LOGGING_CONFIG)
    return logging.getLogger("pick_and_place")


logger = setup_logging()

from dobot_sdk import DobotRobot, CoordinateType  # noqa: E402,F401
from check_camera_calibration_positions import (  # noqa: E402
    wait_for_motion_complete,
)

try:
    import client as vision_client
except ImportError as e:
    logger.error("Failed to import vision API client from %s: %s", CLIENT_DIR, e)
    logger.error("Ensure 'requests' and 'bilogger' are installed and the vision API "
                 "client dependencies are available.")
    sys.exit(1)


# ==================== Configuration (adjust to your setup) ====================

ROBOT_IP = os.environ.get("ROBOT_IP", "192.168.100.51")
VISION_API_URL = os.environ.get("VISION_API_URL", "http://localhost:8000")

# Tool coordinate system indices (1-50) registered on the controller.
CAMERA_TOOL_INDEX = 3
GRIPPER_TOOL_INDEX = 4
# CAMERA_TOOL_INDEX = 2
# GRIPPER_TOOL_INDEX = 2

# Camera TCP: paste the result printed by calibrate_camera_tcp.py
# [x, y, z, rx, ry, rz] in mm / deg (camera optical frame in flange).
# CAMERA_TCP = [-79.8088, -1.9769, 48.5972, -2.2512, 0.2884, -89.6780]
CAMERA_TCP = [-83.9743, -3.6767, 51.0055, -2.4953, 0.7329, -90.2043]
# Gripper TCP: your suction-cup TCP [x, y, z, rx, ry, rz] in mm / deg
# (cup contact point in flange).
GRIPPER_TCP = [0.0, 0.0, 83.0, 0.0, 0.0, 0.0]

# Work plane and camera focus
WORK_PLANE_Z = 68.0     # mm, where objects lie / gripper contacts (world Z)
FOCUS_DISTANCE = 332.0  # mm, camera->plane distance
SCAN_Z = WORK_PLANE_Z + FOCUS_DISTANCE  # 440 mm, camera optical-center height
SCAN_X = 83.0            # mm, scan center X (world) -- adjust to your workspace
SCAN_Y = -353.0         # mm, scan center Y (world)
SCAN_ORIENTATION = [177.5047, -0.7329, -89.7957]   # look straight down (optical Z = -world Z)

# Gripper travel heights (world Z), with the gripper tool active
APPROACH_Z = 200.0      # mm, safe travel / approach height above the plane
# PICK_Z = 67.0           # mm, descent height at pick (≈ plane; adjust for cup/object) # cup
PICK_Z = 51.0           # mm, for can_01
PICK_ORIENTATION = [-180.0, 0.0, -180.0]   # gripper pointing down

# Place position (world, with gripper tool active)
PLACE_X = 200.0
PLACE_Y = -350.0
PLACE_Z = 60.0

PLACE_POSITIONS = [
    [-140, -400, PLACE_Z],
    [-140, -300, PLACE_Z],
    [-140, -200, PLACE_Z],
    [-240, -400, PLACE_Z],
    [-240, -300, PLACE_Z],
    [-240, -200, PLACE_Z]
]

# Suction control (end-effector ToolDO)
SUCTION_PORT = 1        # ToolDO index (0 or 1)
SUCTION_ON_DELAY = 0.5  # s, let vacuum establish after turning on
SUCTION_OFF_DELAY = 0.7  # s, pause before lifting after release

# Vision detection
# MODEL_NAME = "paper_cup"           # must already exist on the vision server
MODEL_NAME = "can_01"
MATCH_THRESHOLD = 0.01          # or a float, e.g. 0.3

# Safe / home pose (world, gripper tool)
# SAFE_POSE = [0.0, -300.0, 300.0, -180.0, 0.0, -180.0]
SAFE_POSE = [SCAN_X, SCAN_Y, SCAN_Z, -180.0, 0.0, -180.0]

# Persist registered tool frames on the controller (1 = persist, 0 = session only)
SET_TOOL_PERSIST = 1

# Speed
SPEED_FACTOR = 10

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

def move_to(robot, label: str, pose, tool: int, user: int = 0,
            timeout: float = MOVE_TIMEOUT) -> bool:
    """Joint move (MovJ) to an absolute Cartesian pose with explicit tool; block.

    Args:
        robot: connected DobotRobot with feedback monitor running
        label: display name of the target position
        pose: [x, y, z, rx, ry, rz] in mm / degrees (user coordinate system)
        tool: tool coordinate system index (0-50) — passed explicitly to MovJ
        user: user coordinate system index (default 0 = world)
        timeout: max wait for motion completion (seconds)

    Returns:
        True if the move completed, False on timeout.
    """
    if len(pose) != 6:
        raise ValueError(f"{label}: pose requires 6 values [x,y,z,rx,ry,rz]")

    logger.info("\n--- %s ---", label)
    logger.info("  target: %s (tool=%s, user=%s)", pose, tool, user)
    response = robot.motion.MovJ(pose, CoordinateType.CARTESIAN,
                                 user=user, tool=tool)
    logger.info("  MovJ response: %s", response)

    ok = wait_for_motion_complete(robot, timeout=timeout)
    if not ok:
        logger.warning("  [TIMEOUT] %s not reached within %ss", label, timeout)
        return False

    status = robot.GetStatus()
    if status is not None:
        p = status.tool_vector_actual
        logger.info("  actual: X=%.2f Y=%.2f Z=%.2f mm | "
                    "Rx=%.2f Ry=%.2f Rz=%.2f deg",
                    p.x, p.y, p.z, p.rx, p.ry, p.rz)
    return True


def movl_and_wait(robot, pose, label: str, tool: int, user: int = 0,
                  timeout: float = MOVE_TIMEOUT) -> bool:
    """Linear move (MovL) to an absolute pose with explicit tool; block."""
    logger.info("  MovL %s: %s (tool=%s, user=%s)", label, pose, tool, user)
    response = robot.motion.MovL(pose, CoordinateType.CARTESIAN,
                                 user=user, tool=tool)
    logger.info("    response: %s", response)
    ok = wait_for_motion_complete(robot, timeout=timeout)
    if not ok:
        logger.warning("  [TIMEOUT] %s not reached within %ss", label, timeout)
    return ok


# ==================== Workflow ====================

def scan_and_detect(robot, session, scan_pose=None):
    """Move to scan pose, detect object -> object world position [x, y, z]."""
    logger.info("\n--- Scan (camera tool) ---")
    robot.robot_control.Tool(CAMERA_TOOL_INDEX)
    if scan_pose is None:
        scan_pose = [SCAN_X, SCAN_Y, SCAN_Z] + list(SCAN_ORIENTATION)
    if not move_to(robot, "scan", scan_pose, tool=CAMERA_TOOL_INDEX):
        return None

    # Actual camera pose in world (from real flange pose + camera TCP)
    R_g2b, t_g2b = read_flange_pose(robot)
    R_wcam, c_world = camera_pose_in_world(R_g2b, t_g2b, CAMERA_TCP)
    logger.info("  camera center (world): [%.2f %.2f %.2f] mm",
                c_world[0], c_world[1], c_world[2])

    logger.info("\n--- Detect ---")
    body = vision_client.detect_2d_debug(session, MODEL_NAME, MATCH_THRESHOLD)
    if body.get("success") is False:
        err = body.get("error", {})
        logger.warning("  detection failed: %s: %s", err.get("code"), err.get("message"))
        return None
    if not body.get("detected"):
        logger.info("  no object detected")
        return None

    nx, ny = body["normalized_centre_point_coordinates"]
    logger.info("  detection center (normalized): nx=%.4f ny=%.4f", nx, ny)

    # Save the debug image for inspection (timestamped so it isn't overwritten)
    debug_dir = os.environ.get(
        "DEBUG_IMAGE_DIR", os.path.join(EXAMPLES_DIR, "debug_images"),
    )
    os.makedirs(debug_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    debug_path = os.path.join(debug_dir, f"detect_2d_debug_{timestamp}.png")
    vision_client.get_detect_2d_debug_image(session, save_path=debug_path)
    logger.info("  debug image saved to %s", debug_path)

    obj = back_project_to_world(nx, ny, R_wcam, c_world)
    logger.info("  object (world): [%.2f %.2f %.2f] mm", obj[0], obj[1], obj[2])
    return obj


def double_scan_and_detect(robot, session):
    """Move to scan pose, detect object -> move to scan pose above the detected object
    -> detect object -> object world position [x, y, z]."""
    obj = scan_and_detect(robot, session)
    if obj is None:
        logger.info("  no object detected")
        return None
    else:
        logger.info("  moving on top of the object")
        above_object_pose = [obj[0], obj[1], SCAN_Z] + list(SCAN_ORIENTATION)
        obj = scan_and_detect(robot, session, scan_pose=above_object_pose)
        return obj

# def move_camera_above_object(robot, obj):
#     """Move camera above the object, go to scan height."""
#     print("\n--- Scan (camera tool) ---")
#     robot.robot_control.Tool(CAMERA_TOOL_INDEX)
#
#     scan_position = [obj[0], obj[1], SCAN_Z] + list(SCAN_ORIENTATION)
#     if not move_to(robot, "approach scan", scan_position):
#         return False
#
#     return True


def pick(robot, obj):
    """Move above the object, descend, engage suction, lift."""
    logger.info("\n--- Pick (gripper tool) ---")
    robot.robot_control.Tool(GRIPPER_TOOL_INDEX)

    approach = [obj[0], obj[1], APPROACH_Z] + list(PICK_ORIENTATION)
    if not move_to(robot, "approach pick", approach, tool=GRIPPER_TOOL_INDEX):
        return False

    descend = [obj[0], obj[1], PICK_Z] + list(PICK_ORIENTATION)
    if not movl_and_wait(robot, descend, "descend to pick",
                         tool=GRIPPER_TOOL_INDEX):
        return False

    logger.info("  suction ON")
    robot.io.ToolDO(SUCTION_PORT, 1)
    time.sleep(SUCTION_ON_DELAY)

    if not movl_and_wait(robot, approach, "lift after pick",
                         tool=GRIPPER_TOOL_INDEX):
        return False
    return True


def place(robot):
    """Move to the place position, descend, release, lift."""
    logger.info("\n--- Place (gripper tool) ---")
    approach = [PLACE_X, PLACE_Y, APPROACH_Z] + list(PICK_ORIENTATION)
    if not move_to(robot, "approach place", approach, tool=GRIPPER_TOOL_INDEX):
        return False

    descend = [PLACE_X, PLACE_Y, PLACE_Z] + list(PICK_ORIENTATION)
    if not movl_and_wait(robot, descend, "descend to place",
                         tool=GRIPPER_TOOL_INDEX):
        return False

    logger.info("  suction OFF")
    robot.io.ToolDO(SUCTION_PORT, 0)
    time.sleep(SUCTION_OFF_DELAY)

    if not movl_and_wait(robot, approach, "lift after place",
                         tool=GRIPPER_TOOL_INDEX):
        return False
    return True


def pick_and_stack_loop(robot, session):
    obj = double_scan_and_detect(robot, session)
    if obj is None:
        logger.info("\nNothing to pick — trying again.")
    else:
        if not pick(robot, obj):
            logger.warning("\nPick failed — aborting.")
        elif not place(robot):
            logger.warning("\nPlace failed — aborting.")
        else:
            logger.info("\nPick and place completed.")


def pick_and_place_loop(robot, session):
    obj = double_scan_and_detect(robot, session)
    if obj is None:
        logger.info("\nNothing to pick — trying again.")
    else:
        if not pick(robot, obj):
            logger.warning("\nPick failed — aborting.")
        elif not place(robot):
            logger.warning("\nPlace failed — aborting.")
        else:
            logger.info("\nPick and place completed.")


def main() -> None:
    session = requests.Session()
    vision_client.BASE_URL = VISION_API_URL

    try:
        with DobotRobot(ROBOT_IP) as robot:
            logger.info("=" * 50)
            logger.info("Pick and Place (vision-driven)")
            logger.info("=" * 50)
            logger.info("Robot: %s | Vision API: %s", ROBOT_IP, VISION_API_URL)
            logger.info("Work plane Z=%s mm | Focus=%s mm | Scan Z=%s mm",
                        WORK_PLANE_Z, FOCUS_DISTANCE, SCAN_Z)
            logger.info("Model: %s | Suction ToolDO port: %s", MODEL_NAME, SUCTION_PORT)

            robot.robot_control.RequestControl()
            robot.robot_control.ClearError()
            robot.robot_control.EnableRobot(load=1.0)
            robot.robot_control.SpeedFactor(SPEED_FACTOR)

            # Register tool coordinate systems on the controller
            resp = robot.robot_control.SetTool(
                CAMERA_TOOL_INDEX, CAMERA_TCP, type=SET_TOOL_PERSIST)
            logger.info("  SetTool(camera %s): %s", CAMERA_TOOL_INDEX, resp)
            if not resp.startswith("0,"):
                logger.warning("  [WARNING] SetTool camera failed: %s", resp)
            resp = robot.robot_control.SetTool(
                GRIPPER_TOOL_INDEX, GRIPPER_TCP, type=SET_TOOL_PERSIST)
            logger.info("  SetTool(gripper %s): %s", GRIPPER_TOOL_INDEX, resp)
            if not resp.startswith("0,"):
                logger.warning("  [WARNING] SetTool gripper failed: %s", resp)

            # Required for move_to()'s / movl_and_wait()'s blocking wait
            robot.StartFeedbackMonitor()
            time.sleep(0.5)

            vision_client.get_initial_status(session)

            try:
                while True:
                    pick_and_place_loop(robot, session)
                # robot.robot_control.Tool(GRIPPER_TOOL_INDEX)
                # for idx, position in enumerate(PLACE_POSITIONS):
                #     drop_pose = position + list(PICK_ORIENTATION)
                #     move_to(robot, f"place_{idx}", drop_pose)
            finally:
                # Return to a safe pose (gripper tool) before shutting down
                logger.info("\nReturning to safe pose...")
                robot.robot_control.Tool(GRIPPER_TOOL_INDEX)
                try:
                    move_to(robot, "safe", SAFE_POSE,
                            tool=GRIPPER_TOOL_INDEX)
                except Exception:
                    pass
                logger.info("\nStopping monitor...")
                robot.StopFeedbackMonitor()
                robot.io.ToolDO(SUCTION_PORT, 0)
                # robot.robot_control.DisableRobot()

            logger.info("\n" + "=" * 50)
            logger.info("Done")
            logger.info("=" * 50)

    except requests.exceptions.ConnectionError as e:
        logger.error("Connection error: ensure the vision API server is running "
                     "on %s: %s", VISION_API_URL, e)
    except requests.exceptions.Timeout as e:
        logger.error("Vision API request timeout: %s", e)
    except Exception as e:
        logger.exception(e)
    finally:
        session.close()


if __name__ == "__main__":
    main()
    # with DobotRobot(ROBOT_IP) as robot:
    #     robot.robot_control.Tool(GRIPPER_TOOL_INDEX)
    #     scan_pose = [SCAN_X, SCAN_Y, SCAN_Z] + list(SCAN_ORIENTATION)
    #     move_to(robot, "scan", scan_pose)
