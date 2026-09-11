"""
Main entry file
"""

from DobotDemo import DobotDemo

if __name__ == '__main__':
    # Modify to actual robot IP
    dobot = DobotDemo("192.168.5.1")
    dobot.start()
