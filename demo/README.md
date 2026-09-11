# Demo Program

This directory contains robot control demonstration programs adapted for the new SDK.

## File Structure

```
demo/
├── DobotDemo.py      # Core class for robot control
├── main.py           # Basic demo entry point
├── ui.py             # Graphical control interface
├── main_UI.py        # UI interface entry point
├── z_Cnv_test.py     # Conveyor tracking test
├── z_servo_test.py   # Servo dynamic following test
└── README.md         # Documentation
```

## Functionality

| File | Functionality | How to Run |
|------|---------------|------------|
| `main.py` | Basic connection and status monitoring | `python main.py` |
| `main_UI.py` | Graphical robot control interface | `python main_UI.py` |
| `z_Cnv_test.py` | Conveyor tracking demonstration | `python z_Cnv_test.py` |
| `z_servo_test.py` | ServoP dynamic trajectory following | `python z_servo_test.py` |

## Prerequisites

1. **Install dependencies**: Ensure project dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure robot IP**: Modify the `ROBOT_IP` variable in each file to the actual robot IP address

3. **Runtime permissions**: Ensure the robot has entered TCP control mode

## Quick Start

### Option 1: Command-line basic demo
```bash
cd demo
python main.py
```

### Option 2: Graphical interface control
```bash
cd demo
python main_UI.py
```

## Important Notes

1. Ensure the robot is properly connected to the network before running
2. First-time usage requires requesting TCP control mode
3. Test motion functions within a safe area
4. Conveyor tracking test requires hardware support
