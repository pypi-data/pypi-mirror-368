# leafsdk/cli/wizard.py

import json
from  utils.logger import get_logger

logger = get_logger("LeafCLI")

def add_arguments(parser):
    parser.add_argument('output_file', type=str, help='Path to save the generated mission JSON')

def run(args):
    logger.info("🚀 Welcome to the LeafSDK Mission Wizard 🚀")
    
    mission = {
        "mission_name": input("Mission Name: "),
        "start_takeoff_altitude": float(input("Takeoff Altitude (m): ")),
        "waypoints": []
    }
    
    while True:
        lat = float(input("Waypoint Latitude: "))
        lon = float(input("Waypoint Longitude: "))
        alt = float(input("Waypoint Altitude (m): "))
        speed = float(input("Speed (optional, 0 to skip): "))

        wp = {"latitude": lat, "longitude": lon, "altitude": alt}
        if speed > 0:
            wp["speed"] = speed
        mission["waypoints"].append(wp)

        cont = input("Add another waypoint? (y/n): ")
        if cont.lower() != 'y':
            break

    with open(args.output_file, 'w') as f:
        json.dump(mission, f, indent=2)

    logger.info(f"Mission saved to {args.output_file} ✅.")
