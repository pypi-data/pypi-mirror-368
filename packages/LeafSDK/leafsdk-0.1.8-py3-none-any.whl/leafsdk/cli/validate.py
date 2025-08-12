# leafsdk/cli/validate.py

import os
import sys
import json
from  utils.logger import get_logger

logger = get_logger("LeafCLI")

def add_arguments(parser):
    parser.add_argument('mission_file', type=str, help='Path to the mission JSON file')

def run(args):
    if not os.path.exists(args.mission_file):
        logger.error(f"Mission file {args.mission_file} not found!")
        sys.exit(1)

    with open(args.mission_file, 'r') as f:
        mission_data = json.load(f)

    if not mission_data.get('waypoints'):
        logger.error("Validation failed: No waypoints defined.")
        sys.exit(1)

    logger.info("Mission validation infoful ✅.")
