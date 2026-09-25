"""
Reference Python client for Boreas Imaging Vision API.

This client demonstrates interaction with all API endpoints,
logging debug messages at each step using the custom logger module.
"""

import base64
import json
import time
from typing import Any, Dict, Optional

import requests

import bilogger as logger

# Configure logging at module level
log = logger.get_logger(
    __name__, log_file="client.log", console_level=logger.logging.DEBUG
)

# API configuration
BASE_URL = "http://localhost:8000"
REQUEST_TIMEOUT = 30


def log_request(
    method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
) -> None:
    """Log details of an outgoing HTTP request."""
    log.debug("[REQUEST] %s %s", method, endpoint)
    if data:
        log.debug("[REQUEST] Payload: %s", json.dumps(data, indent=2))


def log_response(
    response: requests.Response, label: str, limit: int = 0
) -> Dict[str, Any]:
    """
    Log response details and return parsed JSON body.

    Args:
        response: The requests Response object
        label: A descriptive label for this response (e.g., "GET /get_time")

    Returns:
        Parsed JSON body as dictionary
    """
    RAW_RESPONSE_LOG_LENGTH = 500   # this is to limit log message for binary data, like images for example
    try:
        if response.headers.get('Content-Type', '').startswith('application/json'):
            body = response.json()
            log.debug("[RESPONSE] %s - Status: %d", label, response.status_code)
            log.debug("[RESPONSE] %s - Success: %s", label, body.get('success', 'N/A'))
            if body.get("error"):
                log.debug("[RESPONSE] %s - Error Code: %s", label, body['error']['code'])
                log.debug("[RESPONSE] %s - Error Message: %s", label, body['error']['message'])
            if body.get("data"):
                if limit == 0:
                    log.debug(
                        "[RESPONSE] %s - Data: %s", label, json.dumps(body['data'], indent=2, default=str)
                    )
                else:
                    log.debug(
                        "[RESPONSE] %s - Data: %s", label, json.dumps(body['data'], indent=2, default=str)[:limit]
                    )
            return body
        else:
            body = response.text[:RAW_RESPONSE_LOG_LENGTH]
            log.debug("[RESPONSE] %s - Status: %s", label, response.status_code)
            log.debug("[RESPONSE] %s - Raw response body: %s", label, body)
            return {}
    except Exception as e:
        log.exception("[RESPONSE] %s - Failed to parse response: %s", label, response.text[:RAW_RESPONSE_LOG_LENGTH])
        return {}


def get_server_time(session: requests.Session) -> None:
    """Get server time from /get_time endpoint."""
    log.info("GET /get_time")
    endpoint = f"{BASE_URL}/get_time"
    log_request("GET", endpoint)
    response = session.get(endpoint, timeout=REQUEST_TIMEOUT)
    body = log_response(response, "GET /get_time")

    if body.get("success"):
        timestamp = body.get("data", {}).get("timestamp")
        log.info("Server timestamp: %s", timestamp)


def list_models(session: requests.Session) -> None:
    log.info("GET /list_models")
    endpoint = f"{BASE_URL}/list_models"
    log_request("GET", endpoint)
    response = session.get(endpoint, timeout=REQUEST_TIMEOUT)
    body = log_response(response, "GET /list_models")

    if body.get("success"):
        models = body.get("data", {}).get("models", [])
        log.info("Models count: %d", len(models))


def create_test_model(session: requests.Session) -> None:
    """Create a test model."""
    log.info("POST /create_model")
    endpoint = f"{BASE_URL}/create_model"
    payload = {"model_name": "test_model", "override": False}
    log_request("POST", endpoint, payload)
    response = session.post(endpoint, json=payload, timeout=REQUEST_TIMEOUT)
    body = log_response(response, "POST /create_model")

    if body.get("success"):
        log.info("Model 'test_model' created successfully")
    else:
        log.warning("Failed to create model: %s", body.get("error", {}).get("message"))


def create_model(session: requests.Session, model_name, override) -> None:
    """Create named model."""
    log.info("POST /create_model")
    endpoint = f"{BASE_URL}/create_model"
    payload = {"model_name": model_name, "override": override}
    log_request("POST", endpoint, payload)
    response = session.post(endpoint, json=payload, timeout=REQUEST_TIMEOUT)
    body = log_response(response, "POST /create_model")

    if body.get("success"):
        log.info("Model 'test_model' created successfully")
    else:
        log.warning("Failed to create model: %s", body.get("error", {}).get("message"))


def detect_2d(session: requests.Session, model_name, match_threshold) -> None:
    """Detect 2D with the test model."""
    log.info("POST /detect_2d")
    endpoint = f"{BASE_URL}/detect_2d"
    payload = {"model_name": model_name, "parameters": {}}
    if match_threshold is not None:
        payload["parameters"] = {"match_threshold": match_threshold}
    log_request("POST", endpoint, payload)
    response = session.post(endpoint, json=payload, timeout=REQUEST_TIMEOUT)
    body = log_response(response, "POST /detect_2d")

    if body.get("success"):
        detections = body.get("data", {}).get("detections", [])
        log.info("Detections count: %d", len(detections))
        if detections:
            detection = detections[0]
            log.info(
                "First detection - Center: %s, Diameter: %s", detection.get("center"), detection.get("diameter")
            )
    else:
        log.warning("Detection failed: %s", body.get("error", {}).get("message"))
    return response


def delete_test_model(session: requests.Session) -> None:
    """Delete the test model."""
    log.info("POST /delete_model")
    endpoint = f"{BASE_URL}/delete_model"
    payload = {"model_name": "test_model"}
    log_request("POST", endpoint, payload)
    response = session.post(endpoint, json=payload, timeout=REQUEST_TIMEOUT)
    body = log_response(response, "POST /delete_model")

    if body.get("success"):
        log.info("Model 'test_model' deleted successfully")
    else:
        log.warning("Failed to delete model: %s", body.get("error", {}).get("message"))


def get_image(session: requests.Session) -> None:
    """Get sample image from /get_image endpoint."""
    log.info("GET /get_image")
    endpoint = f"{BASE_URL}/get_image"
    log_request("GET", endpoint)
    response = session.get(endpoint, timeout=REQUEST_TIMEOUT)
    body = log_response(
        response,
        "GET /get_image",
        limit=256,
    )  # Log only the first 256 characters

    if body.get("success"):
        image_data = body.get("data", {})
        width = image_data.get("width")
        height = image_data.get("height")
        image_format = image_data.get("format")
        encoded = image_data.get("data", "")

        log.info(
            "Image retrieved - Width: %s, Height: %s, Format: %s", width, height, image_format
        )
        log.info("Encoded data length: %d characters", len(encoded))

        # Decode and validate PNG header
        try:
            decoded = base64.b64decode(encoded)
            if decoded.startswith(b"\x89PNG\r\n\x1a\n"):
                log.info("PNG signature verified")
            else:
                log.warning("PNG signature not found")
        except Exception:
            log.exception("Failed to decode image")
    else:
        log.warning("Failed to get image: %s", body.get("error", {}).get("message"))


def get_initial_status(session: requests.Session) -> None:
    """Get initial status."""
    log.info("GET /get_status (initial)")
    endpoint = f"{BASE_URL}/get_status"
    log_request("GET", endpoint)
    response = session.get(endpoint, timeout=REQUEST_TIMEOUT)
    body = log_response(response, "GET /get_status (initial)")

    if body.get("success"):
        status = body.get("data", {})
        log.info(f"Camera connected: {status.get('camera_connected')}")
        log.info(f"Is calibrated: {status.get('is_calibrated')}")
        log.info(f"Calibration in progress: {status.get('calibration_in_progress')}")


def start_intrinsic_calibration(session: requests.Session) -> None:
    """Start intrinsic calibration."""
    log.info("POST /start_intrinsic_calibration")
    endpoint = f"{BASE_URL}/start_intrinsic_calibration"
    log_request("POST", endpoint)
    response = session.post(endpoint, timeout=REQUEST_TIMEOUT)
    body = log_response(response, "POST /start_intrinsic_calibration")

    if body.get("success"):
        log.info("Intrinsic calibration started")
    else:
        log.warning(
            f"Failed to start calibration: {body.get('error', {}).get('message')}"
        )


def collect_calibration_frame(session: requests.Session) -> None:
    """Collect calibration frame"""
    log.info("POST /detect_calibration_pattern_intrinsic")
    endpoint = f"{BASE_URL}/detect_calibration_pattern_intrinsic"
    payload = {
        "pattern": {
            "name": "RectangleDotPatternStaggered",
            "data": {"pattern_size": (4, 11), "diagonal_spacing": 15, "diameter": 5},
        }
    }
    log_request("POST", endpoint, payload)
    response = session.post(endpoint, json=payload, timeout=REQUEST_TIMEOUT)
    body = log_response(
        response, f"POST /detect_calibration_pattern_intrinsic"
    )

    if body.get("success"):
        status = body.get("data", {})
        num_frames = status.get("num_frames_accepted")
        reprojection_error = status.get("reprojection_error")
        sufficient = status.get("sufficient")
        log.info(
            f"Frames accepted: {num_frames}, Error: {reprojection_error}, Sufficient: {sufficient}"
        )
    else:
        log.warning(
            f"Detection failed: {body.get('error', {}).get('message')}"
        )


def collect_calibration_frames(session: requests.Session) -> None:
    """Collect calibration frames (5 required)."""
    log.info("collect_calibration_frames (5 frames)")
    for frame_num in range(1, 6):
        log.info("POST /detect_calibration_pattern_intrinsic (frame %s)", frame_num)
        collect_calibration_frame(session)


def stop_intrinsic_calibration(session: requests.Session, accept=True) -> None:
    """Stop intrinsic calibration (accept)."""
    log.info("POST /stop_intrinsic_calibration")
    endpoint = f"{BASE_URL}/stop_intrinsic_calibration"
    payload = {"accept": accept}
    log_request("POST", endpoint, payload)
    response = session.post(endpoint, json=payload, timeout=REQUEST_TIMEOUT)
    body = log_response(response, "POST /stop_intrinsic_calibration")

    if body.get("success"):
        log.info("Intrinsic calibration stopped and accepted")
    else:
        log.warning(
            f"Failed to stop calibration: {body.get('error', {}).get('message')}"
        )


def get_status_after_calibration(session: requests.Session) -> None:
    """Get status after calibration."""
    log.info("GET /get_status (after calibration)")
    endpoint = f"{BASE_URL}/get_status"
    log_request("GET", endpoint)
    response = session.get(endpoint, timeout=REQUEST_TIMEOUT)
    body = log_response(response, "GET /get_status (after calibration)")

    if body.get("success"):
        status = body.get("data", {})
        log.info(f"Camera connected: {status.get('camera_connected')}")
        log.info(f"Is calibrated: {status.get('is_calibrated')}")
        log.info(f"Calibration in progress: {status.get('calibration_in_progress')}")


def detect_calibration_pattern(session: requests.Session) -> None:
    """Detect calibration pattern (extrinsic)."""
    log.info("POST /detect_calibration_pattern")
    endpoint = f"{BASE_URL}/detect_calibration_pattern"
    payload = {"pattern": {"name": "RectangleDotPatternStaggered", "data": {}}}
    log_request("POST", endpoint, payload)
    response = session.post(endpoint, json=payload, timeout=REQUEST_TIMEOUT)
    body = log_response(response, "POST /detect_calibration_pattern")

    if body.get("success"):
        pose = body.get("data", {})
        position = pose.get("position")
        orientation = pose.get("orientation")
        log.info(f"Pose detected - Position: {position}, Orientation: {orientation}")
    else:
        log.warning(
            f"Calibration pattern detection failed: {body.get('error', {}).get('message')}"
        )


def get_camera_setting(session: requests.Session, name: str) -> None:
    """Get a camera setting by name."""
    log.info("GET /camera_setting?name=%s", name)
    endpoint = f"{BASE_URL}/camera_setting"
    params = {"name": name}
    log_request("GET", endpoint, params)
    response = session.get(endpoint, params=params, timeout=REQUEST_TIMEOUT)
    body = log_response(response, f"GET /camera_setting (name={name})")

    if body.get("success"):
        value = body.get("data")
        log.info("Camera setting '%s' = %s", name, value)
    else:
        log.warning("Failed to get camera setting: %s", body.get("error", {}).get("message"))


def set_camera_setting(session: requests.Session, name: str, value: Any) -> None:
    """Set a camera setting by name."""
    log.info("POST /camera_setting (name=%s, value=%s)", name, value)
    endpoint = f"{BASE_URL}/camera_setting"
    payload = {"name": name, "value": value}
    log_request("POST", endpoint, payload)
    response = session.post(endpoint, json=payload, timeout=REQUEST_TIMEOUT)
    body = log_response(response, f"POST /camera_setting (name={name}, value={value})")

    if body.get("success"):
        log.info("Camera setting '%s' set to %s", name, value)
    else:
        log.warning("Failed to set camera setting: %s", body.get("error", {}).get("message"))


def main() -> None:
    """Execute the reference client workflow."""
    log.info("=" * 70)
    log.info("Boreas Imaging Vision API - Reference Client")
    log.info("=" * 70)

    session = requests.Session()

    try:
        get_server_time(session)
        list_models(session)
        create_test_model(session)
        list_models(session)
        detect_2d(session)
        delete_test_model(session)
        get_image(session)
        get_initial_status(session)

        get_camera_setting(session, "exposure_time")
        get_camera_setting(session, "gain")

        start_intrinsic_calibration(session)
        collect_calibration_frames(session)
        stop_intrinsic_calibration(session)
        get_status_after_calibration(session)
        detect_calibration_pattern(session)

        log.info("=" * 70)
        log.info("Reference client execution completed successfully!")
        log.info("=" * 70)

    except requests.exceptions.ConnectionError:
        log.exception("Connection error: ensure the API server is running on http://localhost:8000")
    except requests.exceptions.Timeout:
        log.exception("Request timeout")
    except Exception:
        log.exception("Unexpected error")
    finally:
        session.close()
        log.info("Session closed")


def run_intrinsic_calibration(session: requests.Session) -> None:
    start_intrinsic_calibration(session)
    get_initial_status(session)
    while True:
        try:
            output = input("Press any key to collect calibration frame. CTRL+C, CTRL+D or q to stop calibration.")
            if output.strip().lower() == "q":
                break
            collect_calibration_frame(session)
        except (KeyboardInterrupt, EOFError):
            print("Exiting loop")
            break
    stop_intrinsic_calibration(session, accept=True)
    get_status_after_calibration(session)


if __name__ == "__main__":
    # BASE_URL = "http://192.168.1.103:8000"
    # BASE_URL = "http://10.10.10.2:8000"
    BASE_URL = "http://127.0.0.1:8000"
    session = requests.Session()
    # detect_2d(session)

    # get_camera_setting(session, "exposure_time")
    # get_camera_setting(session, "gain")
    # set_camera_setting(session, "exposure_time", 150000.0)  # μs
    # run intrinsic calibration
    # run_intrinsic_calibration()

    # get and set exposure_time and gain
    # get_camera_setting(session, "exposure_time")
    # get_camera_setting(session, "gain")
    # set_camera_setting(session, "gain", 1.0)
    # set_camera_setting(session, "exposure_time", 150000.0)  # μs
    # get_camera_setting(session, "exposure_time")
    # get_camera_setting(session, "gain")

    detect_calibration_pattern(session)
    # get_image(session)
    # detect_2d(session)

    # list_models(session)
    # import numpy as np
    # create_model(session, "paper_cup", False)
    # angles = []
    # for _ in range(10):
    #     response = detect_2d(session, model_name="paper_cup", match_threshold=0.3)
    #     angle = float(response.json().get("data")["detections"][0]["angle"])
    #     angles.append(angle)
    # print(angles)
    # print(np.degrees(np.std(angles)))
    print("done")
