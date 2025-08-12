# leafsdk/cli/start.py

from  connection.mavlink_interface import MAVLinkInterface
from  utils.logger import get_logger
import time

logger = get_logger("LeafCLI")

def add_arguments(parser):
    parser.add_argument('--conn', type=str, default="udp:127.0.0.1:14550", help='MAVLink connection string')

def pre_flight_check(mav):
    logger.info("Running pre-flight checks...")

    # Check battery
    msg = mav.connection.recv_match(type='SYS_STATUS', blocking=True, timeout=5)
    if not msg:
        logger.error("No SYS_STATUS received!")
        return False

    battery = msg.battery_remaining
    logger.info(f"Battery: {battery}%")
    if battery < 30:
        logger.error("Battery too low for mission start (need >30%)")
        return False

    # Check GPS
    gps_msg = mav.connection.recv_match(type='GPS_RAW_INT', blocking=True, timeout=5)
    if not gps_msg:
        logger.error("No GPS_RAW_INT received!")
        return False

    fix_type = gps_msg.fix_type  # 3 = 3D fix
    logger.info(f"GPS Fix Type: {fix_type}")
    if fix_type < 3:
        logger.error("GPS not ready (need 3D fix or better)")
        return False

    logger.info("Pre-flight checks passed ✅.")
    return True

def run(args):
    mav = MAVLinkInterface(args.conn)

    if not pre_flight_check(mav):
        logger.error("Pre-flight checks failed. Aborting mission start.")
        return

    logger.info("Sending START mission command...")
    mav.connection.mav.command_long_send(
        mav.connection.target_system,
        mav.connection.target_component,
        300,  # MAV_CMD_MISSION_START
        0,
        0, 0, 0, 0, 0, 0, 0
    )
    logger.info("Mission started infofully 🚀.")
