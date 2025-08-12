# leafsdk/cli/abort.py

from  connection.mavlink_interface import MAVLinkInterface
from leafsdk import logger

def add_arguments(parser):
    parser.add_argument('--conn', type=str, default="udp:127.0.0.1:14550", help='MAVLink connection string')

def run(args):
    mav = MAVLinkInterface(args.conn)
    
    logger.info("Sending ABORT command (Return to Home)...")
    mav.connection.mav.command_long_send(
        mav.connection.target_system,
        mav.connection.target_component,
        20,  # MAV_CMD_NAV_RETURN_TO_LAUNCH
        0,
        0, 0, 0, 0, 0, 0, 0
    )
    logger.info("Abort command sent (Return To Launch).")
