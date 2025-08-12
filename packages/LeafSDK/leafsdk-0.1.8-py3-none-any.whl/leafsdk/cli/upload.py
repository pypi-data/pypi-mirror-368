# leafsdk/cli/upload.py

from  connection.mavlink_interface import MAVLinkInterface
from  core.mission.mission_planner import MissionPlanner
import os
import sys
import json
from  utils.logger import get_logger

logger = get_logger("LeafCLI")

def add_arguments(parser):
    parser.add_argument('mission_file', type=str, help='Path to the mission JSON file')
    parser.add_argument('--conn', type=str, default="udp:127.0.0.1:14550", help='MAVLink connection string')

def run(args):
    if not os.path.exists(args.mission_file):
        logger.error(f"Mission file {args.mission_file} not found!")
        sys.exit(1)

    mav = MAVLinkInterface(args.conn)
    planner = MissionPlanner(mav)

    with open(args.mission_file, 'r') as f:
        mission_data = json.load(f)

    for wp in mission_data['waypoints']:
        planner.add_waypoint(
            lat=wp['latitude'],
            lon=wp['longitude'],
            alt=wp['altitude'],
            speed=wp.get('speed')
        )

    planner.upload_mission()
    logger.info("Mission uploaded infofully.")
