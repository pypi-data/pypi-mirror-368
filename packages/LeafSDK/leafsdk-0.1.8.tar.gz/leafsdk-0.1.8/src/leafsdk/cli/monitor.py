# leafsdk/cli/monitor.py

from  connection.mavlink_interface import MAVLinkInterface
from  utils.logger import get_logger

logger = get_logger("LeafCLI")

def add_arguments(parser):
    parser.add_argument('--conn', type=str, default="udp:127.0.0.1:14550", help='MAVLink connection string')

def run(args):
    mav = MAVLinkInterface(args.conn)
    logger.info("Monitoring mission status... (Ctrl+C to exit)")

    try:
        while True:
            msg = mav.connection.recv_match(type=['HEARTBEAT', 'MISSION_CURRENT', 'SYS_STATUS'], blocking=True, timeout=5)
            if msg:
                if msg.get_type() == 'MISSION_CURRENT':
                    logger.info(f"[Status] Current Waypoint: {msg.seq}")
                if msg.get_type() == 'SYS_STATUS':
                    logger.info(f"[Battery] {msg.battery_remaining}% remaining")
    except KeyboardInterrupt:
        logger.info("\nStopped monitoring.")
