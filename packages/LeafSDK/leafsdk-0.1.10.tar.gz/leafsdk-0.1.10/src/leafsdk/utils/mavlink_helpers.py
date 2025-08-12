# leafsdk/utils/mavlink_helpers.py

import sys, time
import os
from pymavlink.dialects.v20 import droneleaf_mav_msgs as leafMAV

from leafsdk import logger

def create_msg_external_trajectory_setpoint_enu(
    position_enu,
    velocity_enu,
    acceleration_enu,
    yaw: float = 0.0,
    yaw_rate: float = 0.0,
):
    """
    Create a MAVLink message for external trajectory setpoint in ENU coordinates.
    """
    msg = leafMAV.MAVLink_leaf_external_trajectory_setpoint_enu_message(
        x=position_enu[0],
        y=position_enu[1],
        z=position_enu[2],
        vx=velocity_enu[0],
        vy=velocity_enu[1],
        vz=velocity_enu[2],
        afx=acceleration_enu[0],
        afy=acceleration_enu[1],
        afz=acceleration_enu[2],
        yaw=yaw,
        yaw_rate=yaw_rate,
    )
    logger.debug(f"Created external trajectory setpoint message: {msg}")
    return msg

def parse_heartbeat(msg):
    """
    Parse heartbeat message and return system status info.
    """
    if msg.get_type() != "HEARTBEAT":
        logger.warning("Expected HEARTBEAT message, got something else.")
        return None

    status = {
        "type": msg.type,
        "autopilot": msg.autopilot,
        "base_mode": msg.base_mode,
        "custom_mode": msg.custom_mode,
        "system_status": msg.system_status,
        "mavlink_version": msg.mavlink_version,
    }
    logger.debug(f"Parsed heartbeat: {status}")
    return status
