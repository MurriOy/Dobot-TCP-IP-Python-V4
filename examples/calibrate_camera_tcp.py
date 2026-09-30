# -*- coding: utf-8 -*-
"""
Calibrate Camera TCP (eye-in-hand hand-eye calibration)

Computes the camera TCP — the rigid transform from the robot flange (gripper)
to the camera optical frame — using the positions defined in
check_camera_calibration_positions and detect_calibration_pattern from the
vision client. Solves the classic AX=XB problem with
cv2.calibrateHandEye (Park method).

Setup (eye-in-hand):
    - The camera is mounted on the robot end-effector.
    - The calibration pattern is fixed in the world.

Per position i:
    gripper2base  (T_g2b)  : actual flange pose in world, read from the
                             feedback stream (User 0 / Tool 0 active):
                             tool_vector_actual -> R = Rz(rz)Ry(ry)Rx(rx)
                             (scipy euler 'xyz'), translation in mm.
    target2cam    (T_t2c)  : detect_calibration_pattern response:
                             position (m -> mm) and orientation [x,y,z,w]
                             (scipy as_quat order, OpenCV optical frame).

Solve:
    cv2.calibrateHandEye(R_g2b, t_g2b, R_t2c, t_t2c, Park)
        -> R_cam2gripper, t_cam2gripper  (camera optical frame in flange, mm)

The result is printed as a Dobot pose [x,y,z,rx,ry,rz] (mm / deg) plus a
consistency residual (the target->base transform should be constant across
positions). The result is NOT written to the controller (print only).

Prerequisite: intrinsics must be calibrated first (run calibrate_camera.py),
otherwise detect_calibration_pattern returns NOT_CALIBRATED.

Environment:
    ROBOT_IP       robot dashboard IP (default 192.168.100.51)
    VISION_API_URL vision API base URL (default http://localhost:8000)

Requires: numpy, scipy, opencv-python (cv2), spatialmath (roboticstoolbox),
          requests, bilogger (vision client), camera API running.
"""

import os
import sys
import time

import numpy as np
import requests

try:
    import cv2
except ImportError:
    print("This example requires opencv-python (cv2).\n"
          "  pip install opencv-python")
    sys.exit(1)

from scipy.spatial.transform import Rotation  # noqa: E402

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

SETTLE_SECONDS = 3.0     # let the arm settle (vibration) before reading pose
MIN_PAIRS = 3           # minimum valid pose pairs for hand-eye
HAND_EYE_METHOD = cv2.CALIB_HAND_EYE_PARK


# ==================== Pose conversions ====================

def dobot_euler_to_matrix(rx: float, ry: float, rz: float) -> np.ndarray:
    """Dobot fixed-axis Euler R = Rz(rz)Ry(ry)Rx(rx) -> 3x3 (deg input).

    Equivalent to spatialmath SE3.RPY(rx,ry,rz, order='zyx'): scipy lowercase
    'xyz' (intrinsic xyz == extrinsic zyx) builds the same R = RzRyRx.
    """
    return Rotation.from_euler("xyz", [rx, ry, rz], degrees=True).as_matrix(
    ).astype(np.float64)


def _orthonormalize(R: np.ndarray) -> np.ndarray:
    """Nearest proper rotation matrix (fixes cv2 numerical drift)."""
    U, _, Vt = np.linalg.svd(R)
    D = np.eye(3)
    D[2, 2] = np.linalg.det(U @ Vt)
    return (U @ D @ Vt)


def matrix_to_dobot_pose(R: np.ndarray, t: np.ndarray):
    """3x3 rotation + 3 translation (mm) -> [x,y,z,rx,ry,rz] (mm / deg).

    R is orthonormalized first so a slightly non-SE(3) matrix from
    cv2.calibrateHandEye does not raise.
    """
    R = _orthonormalize(np.asarray(R, dtype=np.float64))
    rx, ry, rz = Rotation.from_matrix(R).as_euler("xyz", degrees=True)
    return [float(t[0]), float(t[1]), float(t[2]),
            float(rx), float(ry), float(rz)]


def read_flange_pose(robot):
    """Actual flange pose in world (User 0 / Tool 0) -> (R 3x3, t 3 mm)."""
    status = robot.GetStatus()
    if status is None:
        raise RuntimeError("No feedback status — StartFeedbackMonitor first")
    p = status.tool_vector_actual
    R = dobot_euler_to_matrix(p.rx, p.ry, p.rz)
    t = np.array([p.x, p.y, p.z], dtype=np.float64)
    return R, t


def parse_target_pose(body):
    """detect_calibration_pattern response body -> (R target2cam 3x3, t mm).

    position is in meters (OpenCV optical frame) -> converted to mm.
    orientation is a unit quaternion [x,y,z,w] (scipy as_quat order).

    Raises ValueError if the detection was not successful.
    """
    if not body.get("success"):
        err = body.get("error", {})
        raise ValueError(
            f"{err.get('code', 'ERROR')}: "
            f"{err.get('message', 'calibration pattern detection failed')}"
        )
    data = body.get("data", {})
    position = data.get("position")
    orientation = data.get("orientation")
    if position is None or orientation is None:
        raise ValueError("response missing position/orientation")
    t = np.array(position, dtype=np.float64) * 1000.0           # m -> mm
    R = Rotation.from_quat(orientation).as_matrix().astype(np.float64)
    return R, t


# ==================== Workflow ====================

def collect_pairs(robot, session):
    """Move to each position, read flange pose, detect pattern -> pose pairs.

    Returns four aligned lists: R_g2b, t_g2b, R_t2c, t_t2c.
    """
    R_g2b, t_g2b, R_t2c, t_t2c = [], [], [], []

    for label, pose in POSITIONS:
        if not move_to(robot, label, pose):
            print("Stopping sequence on motion timeout")
            break

        time.sleep(SETTLE_SECONDS)

        R_g, t_g = read_flange_pose(robot)
        print(f"  flange2base: t=[{t_g[0]:.2f} {t_g[1]:.2f} {t_g[2]:.2f}] mm")

        body = vision_client.detect_calibration_pattern(session)
        try:
            R_c, t_c = parse_target_pose(body)
        except ValueError as e:
            print(f"  pattern detection skipped: {e}")
            continue
        print(f"  target2cam:  t=[{t_c[0]:.2f} {t_c[1]:.2f} {t_c[2]:.2f}] mm")

        R_g2b.append(R_g)
        t_g2b.append(t_g.reshape(3, 1))
        R_t2c.append(R_c)
        t_t2c.append(t_c.reshape(3, 1))

    return R_g2b, t_g2b, R_t2c, t_t2c


def solve_hand_eye(R_g2b, t_g2b, R_t2c, t_t2c):
    """Run cv2.calibrateHandEye and report the camera TCP + consistency."""
    n = len(R_g2b)
    if n < MIN_PAIRS:
        print(f"\nOnly {n} valid pose pair(s); need >= {MIN_PAIRS}.")
        print("Add positions to check_camera_calibration_positions or ensure "
              "the pattern is detected at each one.")
        return None

    R_c2g, t_c2g = cv2.calibrateHandEye(
        R_g2b, t_g2b, R_t2c, t_t2c, method=HAND_EYE_METHOD
    )
    R_c2g = R_c2g.reshape(3, 3)
    t_c2g = t_c2g.reshape(3)

    if not np.all(np.isfinite(R_c2g)) or not np.all(np.isfinite(t_c2g)):
        print("Hand-eye solution is non-finite (insufficient rotation "
              "diversity between positions?).")
        return None

    tcp = matrix_to_dobot_pose(R_c2g, t_c2g)

    print("\n" + "=" * 50)
    print("Camera TCP (camera optical frame in flange)")
    print("=" * 50)
    print("  pose [x, y, z, rx, ry, rz] (mm, deg):")
    print("    [" + ", ".join(f"{v:.4f}" for v in tcp) + "]")

    # Consistency: target->base should be constant across positions.
    positions = []
    rotations = []
    for R_g, t_g, R_c, t_c in zip(R_g2b, t_g2b, R_t2c, t_t2c):
        R_g = R_g.reshape(3, 3)
        t_g = t_g.reshape(3)
        R_c = R_c.reshape(3, 3)
        t_c = t_c.reshape(3)
        R_tab = R_g @ R_c2g @ R_c
        t_tab = t_g + R_g @ (t_c2g + R_c2g @ t_c)
        positions.append(t_tab)
        rotations.append(R_tab)

    positions = np.array(positions)
    std = positions.std(axis=0)
    print("\nConsistency (target->base should be constant):")
    print(f"  translation std: [{std[0]:.3f} {std[1]:.3f} {std[2]:.3f}] mm, "
          f"max {np.max(np.abs(std)):.3f} mm")

    R0 = rotations[0]
    angles = []
    for R_i in rotations:
        rel = R0.T @ R_i
        cos = np.clip((np.trace(rel) - 1.0) / 2.0, -1.0, 1.0)
        angles.append(np.degrees(np.arccos(cos)))
    print(f"  rotation spread: max {max(angles):.3f} deg")

    return tcp


def main() -> None:
    session = requests.Session()
    vision_client.BASE_URL = VISION_API_URL

    try:
        with DobotRobot(ROBOT_IP) as robot:
            print("=" * 50)
            print("Camera TCP Calibration (eye-in-hand, cv2.calibrateHandEye)")
            print("=" * 50)
            print(f"Robot: {ROBOT_IP} | Vision API: {VISION_API_URL}")
            print(f"Positions: {len(POSITIONS)} | Method: Park | "
                  f"Min pairs: {MIN_PAIRS}")
            print("Note: intrinsics must be calibrated first "
                  "(run calibrate_camera.py).")

            robot.robot_control.RequestControl()
            robot.robot_control.ClearError()
            robot.robot_control.EnableRobot(load=1.0)
            robot.robot_control.SpeedFactor(10)

            # Resolve poses in world frame + flange
            robot.robot_control.User(0)
            robot.robot_control.Tool(0)

            # Required for move_to()'s blocking wait and read_flange_pose()
            robot.StartFeedbackMonitor()
            time.sleep(0.5)

            vision_client.get_initial_status(session)
            R_g2b, t_g2b, R_t2c, t_t2c = collect_pairs(robot, session)

            tcp = solve_hand_eye(R_g2b, t_g2b, R_t2c, t_t2c)
            if tcp is None:
                print("\nCalibration failed.")
            else:
                print("\n" + "=" * 50)
                print("Camera TCP calibration completed")
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
        print("\nStopping monitor / disabling robot...")
        robot.StopFeedbackMonitor()
        robot.robot_control.DisableRobot()


if __name__ == "__main__":
    main()
