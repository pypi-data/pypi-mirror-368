# leafsdk/core/gimbal/gimbal_controller.py

from  connection.mavlink_interface import MAVLinkInterface

from leafsdk import logger

class GimbalController:
    def __init__(self, mav_interface: MAVLinkInterface):
        self.mav = mav_interface

    def set_orientation(self, pitch=0.0, roll=0.0, yaw=0.0, target_system=None, target_component=None):
        """
        Set gimbal orientation using pitch, roll, yaw in degrees.
        """
        logger.info(f"Setting gimbal orientation: pitch={pitch}, roll={roll}, yaw={yaw}")
        
        if target_system is None:
            target_system = self.mav.connection.target_system
        if target_component is None:
            target_component = self.mav.connection.target_component

        self.mav.connection.mav.command_long_send(
            target_system,
            target_component,
            205,  # MAV_CMD_DO_MOUNT_CONTROL
            0,
            pitch,  # pitch (degrees, -90=down)
            roll,   # roll
            yaw,    # yaw
            0, 0, 0  # unused params
        )
        logger.info("Gimbal orientation command sent ✅")

    def point_down(self):
        """
        Point the camera straight down.
        """
        self.set_orientation(pitch=-90.0, yaw=0.0, roll=0.0)

    def point_forward(self):
        """
        Reset to forward-facing orientation.
        """
        self.set_orientation(pitch=0.0, yaw=0.0, roll=0.0)
