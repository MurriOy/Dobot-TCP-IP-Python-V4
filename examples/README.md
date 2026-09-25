# Examples

This directory contains example code for the DOBOT SDK, categorized by functionality:

## Example List

| # | File | Description |
|:---:|------|----------|
| 00 | `00_logging_demo.py` | Logging system demo |
| 01 | `01_basic_connection.py` | Basic connection and enabling |
| 02 | `02_motion_control.py` | Motion control (joint/linear/arc/circle) |
| 03 | `03_error_monitor.py` | Error code monitoring and status query |
| 04 | `04_io_control.py` | IO control (digital/analog/tool IO) |
| 05 | `05_coordinate_system.py` | Coordinate system setup (user/tool coordinates) |
| 06 | `06_force_and_conveyor.py` | Force control and conveyor |
| 07 | `07_status_monitor.py` | Status monitoring |
| 08 | `08_multi_thread_control.py` | Multi-thread control |
| 09 | `09_flange_pose_rtb.py` | Flange pose as SE3 + quaternion for Robotics Toolbox for Python |
| 10 | `10_blocking_relmovltool.py` | Blocking RelMovLTool (wait for motion complete via feedback) |

## Running Examples

```bash
# Run basic connection example
python examples/01_basic_connection.py

# Run motion control example
python examples/02_motion_control.py

# Run error monitoring example
python examples/03_error_monitor.py

# Run IO control example
python examples/04_io_control.py

# Run coordinate system setup example
python examples/05_coordinate_system.py

# Run force control and conveyor example
python examples/06_force_and_conveyor.py

# Run status monitoring example
python examples/07_status_monitor.py

# Run multi-thread control example
python examples/08_multi_thread_control.py

# Run flange pose (SE3 / quaternion) example for Robotics Toolbox
python examples/09_flange_pose_rtb.py

# Run blocking relative tool motion example
python examples/10_blocking_relmovltool.py
```

## Usage Notes

1. **Modify IP address**: Each example file has a `ROBOT_IP` variable at the top - modify it to match your actual robot IP
2. **Safety first**: Before running motion examples, ensure there is sufficient safe space around the robot
3. **TCP mode**: Ensure the robot has switched to TCP/IP control mode
4. **Install dependencies**: Ensure necessary dependencies are installed
   ```bash
   pip install numpy requests
   # Optional — only for example 09 (Robotics Toolbox SE3 / quaternion):
   pip install spatialmath-python
   # or: pip install roboticstoolbox-python
   ```

## Example Structure

All examples follow a unified structure pattern:

```python
from dobot_sdk import DobotRobot

def main():
    ROBOT_IP = "192.168.1.100"
    
    try:
        with DobotRobot(ROBOT_IP) as robot:
            # 1. Request control mode
            robot.robot_control.RequestControl()
            
            # 2. Clear alarms
            robot.robot_control.ClearError()
            
            # 3. Enable robot
            robot.robot_control.EnableRobot(load=1.0)
            
            # 4. Execute operations...
            # ...
            
            # 5. Disable robot
            robot.robot_control.DisableRobot()
            
    except Exception as e:
        print(f"Error: {e}")
```

## Module Overview

| Module | Description |
|------|------|
| `robot.robot_control` | Basic control (enable, mode, coordinate system, status query) |
| `robot.motion` | Motion control (MovJ/MovL/Arc/Circle, etc.) |
| `robot.io` | IO control (digital/analog input/output) |
| `robot.communication` | Communication control (register operations) |
| `robot.plugins` | Plugin modules (force control, conveyor) |
