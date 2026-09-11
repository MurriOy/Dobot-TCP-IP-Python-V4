"""
Example 4: IO Control

Demonstrates how to use digital IO, analog IO, and tool IO
"""

from dobot_sdk import DobotRobot
import time


def main():
    ROBOT_IP = "192.168.1.100"
    
    try:
        with DobotRobot(ROBOT_IP) as robot:
            print("=" * 50)
            print("4. IO Control Example")
            print("=" * 50)
            
            # Initialize
            robot.robot_control.RequestControl()
            robot.robot_control.ClearError()
            robot.robot_control.EnableRobot(load=1.0)
            
            # ========== Digital Output Control ==========
            print("\n--- Digital Output Control (DO) ---")
            
            # Method 1: Using DO(index, status)
            print("Turning on DO1...")
            robot.io.DO(1, 1)
            time.sleep(1)
            
            print("Turning off DO1...")
            robot.io.DO(1, 0)
            time.sleep(1)
            
            # Method 2: Using DO (queued command)
            print("Setting DO2 to ON...")
            robot.io.DO(2, 1)
            time.sleep(1)
            
            print("Setting DO2 to OFF...")
            robot.io.DO(2, 0)
            time.sleep(1)
            
            # Method 3: Using DOInstant (immediate command)
            print("Setting DO3 using immediate command...")
            robot.io.DOInstant(3, 1)
            time.sleep(1)
            robot.io.DOInstant(3, 0)
            time.sleep(1)
            
            # ========== Digital Input Reading ==========
            print("\n--- Digital Input Reading (DI) ---")
            for i in range(1, 5):
                di_status = robot.io.DI(i)
                print(f"DI{i} status: {di_status}")
            
            # ========== Digital Output Status Reading ==========
            print("\n--- Digital Output Status Reading (DO) ---")
            for i in range(1, 4):
                do_status = robot.io.GetDO(i)
                print(f"DO{i} status: {do_status}")
            
            # ========== Analog Output Control ==========
            print("\n--- Analog Output Control (AO) ---")
            print("Setting AO1 to 25%...")
            robot.io.AO(1, 25)
            time.sleep(2)
            
            print("Setting AO1 to 75%...")
            robot.io.AO(1, 75)
            time.sleep(2)
            
            print("Setting AO1 to 0%...")
            robot.io.AO(1, 0)
            time.sleep(1)
            
            # ========== Analog Input Reading ==========
            print("\n--- Analog Input Reading (AI) ---")
            for i in range(1, 3):
                ai_value = robot.io.AI(i)
                print(f"AI{i} value: {ai_value}")
            
            # ========== Tool IO Control ==========
            print("\n--- Tool IO Control ---")
            
            # Set tool DO
            print("Setting tool DO1 to ON...")
            robot.io.ToolDO(1, 1)
            time.sleep(1)
            
            print("Setting tool DO1 to OFF...")
            robot.io.ToolDO(1, 0)
            time.sleep(1)
            
            # Read tool DI
            print("Reading tool DI...")
            tool_di_status = robot.io.ToolDI(1)
            print(f"Tool DI status: {tool_di_status}")
            
            # Enable tool power supply
            print("\nEnabling tool power supply...")
            robot.io.SetToolPower(1)  # 1 = enable
            
            # ========== Batch IO Operations ==========
            print("\n--- Batch IO Operations ---")
            print("Setting DO1~DO4 all to ON...")
            robot.io.DOGroup(1, 1, 2, 1, 3, 1, 4, 1)
            time.sleep(2)
            
            print("Setting DO1~DO4 all to OFF...")
            robot.io.DOGroup(1, 0, 2, 0, 3, 0, 4, 0)
            time.sleep(1)
            
            # Disable robot
            robot.robot_control.DisableRobot()
            
            print("\n" + "=" * 50)
            print("IO control example completed")
            print("=" * 50)
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
