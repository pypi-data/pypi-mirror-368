# 🌿 LeafSDK

## 🏗 High-Level Architecture

| Component | Description |
|:----------|:------------|
| **LeafSDK Core** | Main Python library for mission planning, gimbal control, vision-based landing, etc. |
| **MAVLink Interface** | Communicates with LeafFC through MAVLink Router |
| **Mission Planner** | High-level user API to define missions (waypoints, conditionals, checkpoints) |
| **Gimbal Controller** | Gimbal control abstraction (positioning, stabilization) |
| **Vision Module** | Vision-based landing, precision landing helpers |
| **Service Daemon** | Python service running on the mission computer, keeping connection alive |
| **CLI Tool (Optional)** | For simple mission upload/test |
| **Example Applications** | Templates for common mission scripts |
| **Internal Utilities** | Common classes for timeouts, retries, MAVLink message generation etc. |

---

# 📈 Full Architecture Diagram for LeafSDK

```
           +-----------------------+
           |  User Mission Scripts |
           | (Python Programs)     |
           +----------+------------+
                      |
                      v
          +------------------------+
          |      LeafSDK Core      |
          |                        |
          | Mission Planner        |
          | Gimbal Controller      |
          | Vision Landing         |
          | Condition Manager      |
          +------------------------+
                      |
                      v
         +---------------------------+
         |  MAVLink Interface Layer  |
         |  (pymavlink)              |
         +---------------------------+
                      |
                      v
       +---------------------------------+
       |      MAVLink Router Service     |
       | (forwarding UDP/TCP messages)   |
       +---------------------------------+
                      |
                      v
              +-------------------+
              |     LeafFC        |
              |  (Flight Control  |
              |    Firmware)      |
              +-------------------+
```

---

## 📚 Code / Library Structure

```
src/
│
├── __init__.py
│
├── connection/                      # MAVLink connection layer
│   ├── __init__.py
│   ├── mavlink_interface.py        # Low-level MAVLink connection handling
│   ├── heartbeat_monitor.py        # Check heartbeat / link health
│   └── connection_manager.py       # High-level connect/health lifecycle
│
├── core/                            # High-level drone 
mavlink
│
├── [mavlink submodule]/             # Mavlink submodule
│   ├── __init__.py
│
│   ├── gimbal/                      # Gimbal pitch/yaw/roll control
│   │   ├── __init__.py
│   │   └── gimbal_controller.py
│
│   ├── mission/                     # Mission planner and waypoint logic
│   │   ├── __init__.py
│   │   ├── waypoint.py
│   │   ├── condition.py
│   │   └── mission_planner.py
│
│   └── vision/                      # Camera-based features
│       ├── __init__.py
│       ├── vision_landing.py       # ArUco marker detection for landing
│       └── camera_stabilizer.py    # Optical flow drift estimation
│
├── service/                         # Persistent background service
│   ├── __init__.py
│   ├── leaf_service.py             # Main entry point
│   ├── service_manager.py          # Controls lifecycle of connection/loop
│   └── health_checker.py           # Monitors heartbeat and battery
│
├── cli/                             # Command-line interface (leafcli)
│   ├── __init__.py
│   ├── leafcli.py                  # CLI dispatcher
│   ├── upload.py                   # Upload mission
│   ├── validate.py                 # Validate mission file
│   ├── start.py                    # Start mission
│   ├── abort.py                    # Abort mission
│   ├── monitor.py                  # Live mission monitor
│   └── wizard.py                   # Interactive mission builder
│
├── utils/                           # Utility modules shared across SDK
│   ├── __init__.py
│   ├── logger.py                   # Rich-formatted global logger
│   └── mavlink_helpers.py          # MAVLink message helpers (optional)
│
├── examples/                        # Usage examples and demos
│   ├── example_mission.py
│   ├── example_gimbal.py
│   ├── example_vision_landing.py
│
└── setup.py                         # setuptools config for installation
```

---

## 🧩 Core Functionality

### 1. `connection/`

#### a. `mavlink_interface.py`

* Handles MAVLink connection (UDP/TCP/Serial)
* Heartbeat wait and validation
* Message send/receive interface
* Auto-reconnect logic ready

#### b. `heartbeat_monitor.py`

* Monitors heartbeat periodically
* Detects connection loss

#### c. `connection_manager.py`

* High-level controller for connection + heartbeat
* Clean connect/disconnect lifecycle

---

### 2. `core/gimbal/`

#### a. `gimbal_controller.py`

* Controls gimbal pitch/yaw/roll
* Supports forward/down camera presets
* Ready for visual tracking input integration

---

### 3. `core/mission/`

#### a. `mission_planner.py`

* Adds and manages waypoints
* Uploads mission to LeafFC
* Supports conditional logic for mission execution

#### b. `waypoint.py`

* Defines structured waypoint format
* Converts to MAVLink `MISSION_ITEM`

#### c. `condition.py`

* Defines mission triggers (battery %, GPS lock, etc.)
* Integrates into mission execution flow

---

### 4. `core/vision/`

#### a. `vision_landing.py`

* Uses ArUco marker detection
* Computes marker center for landing alignment
* Designed to guide landing via vision

#### b. `camera_stabilizer.py`

* Uses optical flow for drift detection
* Frame-to-frame motion estimation for stabilization

---

### 5. `service/`

#### a. `leaf_service.py`

* Main service loop with signal handling
* Launches connection, heartbeat, and monitoring

#### b. `service_manager.py`

* Initializes and manages runtime modules (gimbal, mission, vision)
* Periodic update handler

#### c. `health_checker.py`

* Reads `SYS_STATUS` and `HEARTBEAT`
* Logs battery and connection status

---

### 6. `cli/`

#### a. `leafcli.py`

* CLI entrypoint and dispatcher

#### b. `upload.py`

* Uploads mission file to drone

#### c. `validate.py`

* Validates structure and content of mission JSON

#### d. `start.py`

* Starts mission with pre-flight checks

#### e. `abort.py`

* Sends RTL (Return to Launch) or mission abort

#### f. `monitor.py`

* Monitors live mission status and telemetry

#### g. `wizard.py`

* Interactive CLI-based mission builder

---

### 7. `utils/`

#### a. `logger.py`

* Centralized `rich`-based logger

#### b. `mavlink_helpers.py`

* Factory functions to generate MAVLink messages
* Parses heartbeat or `SYS_STATUS` into dict

---

### 8. `examples/`

#### a. `example_mission.py`

* Shows how to build and upload a mission via SDK

#### b. `example_gimbal.py`

* Demonstrates setting gimbal orientation

#### c. `example_vision_landing.py`

* Detects landing field markers and prints coordinates

---

## 🔥 Example Usage

**Note:** You need to run as module, e.g. `python3 -m src.test`

```python
from leafsdk.connection.mavlink_interface import MAVLinkInterface
from leafsdk.mission.mission_planner import MissionPlanner
from leafsdk.gimbal.gimbal_controller import GimbalController
from leafsdk.vision.vision_landing import VisionLanding
from leafsdk.service.leaf_service import LeafService

# Connect to LeafFC
mav = MAVLinkInterface("udp:127.0.0.1:14550")

# Plan a mission
mission = MissionPlanner(mav)
mission.add_waypoint(25.276987, 55.296249, 50)
mission.add_waypoint(25.277000, 55.296500, 50)
mission.add_checkpoint("midpoint")
mission.add_waypoint(25.277200, 55.296700, 10)  # Landing point
mission.upload_mission()

# Control gimbal
gimbal = GimbalController(mav)
gimbal.set_orientation(pitch=-90, yaw=0)

# Vision Landing (optional)
# vision = VisionLanding(camera_feed="/dev/video0", mav_interface=mav)
# vision.start_detection()
# vision.guide_landing()

# Start mission
mission.start_mission()
```
## 🛰️ Complex Mission Examples

### Example A: Mission with Loop (Patrol Mission)

```python
mission.add_waypoint(lat1, lon1, 30)
mission.add_waypoint(lat2, lon2, 30)
mission.add_checkpoint("patrol_point")
mission.add_waypoint(lat3, lon3, 30)

# After reaching last waypoint, go back to patrol point and repeat 3 times
mission.add_condition(LoopCondition(target_checkpoint="patrol_point", times=3))
```

This would allow continuous patrolling between points.

---

### Example B: Mission with Failsafe (Return to Checkpoint if Battery Low)

```python
mission.add_waypoint(lat1, lon1, 50)
mission.add_checkpoint("safe_point")

mission.add_waypoint(lat2, lon2, 10)

# Condition: if battery below 20%, go back to "safe_point"
mission.add_condition(BatteryBelowCondition(threshold=20, return_checkpoint="safe_point"))
```

---

### Example C: Vision Based Landing (Dynamic landing)

```python
vision = VisionLanding(camera_feed="/dev/video0", mav_interface=mav)
vision.start_detection()

# VisionLanding will constantly adjust landing coordinates
vision.guide_landing()
```

You can even **blend** GPS and Vision Landing together depending on use-case.

---

## 📦 Packaging

- Structure project with `setup.py`
- Publish to a private/internal PyPI
- Use **`setuptools`** and package as:
  ```bash
  pip install leafsdk/
  ```

Example `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name="leafsdk",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pymavlink",
        "opencv-python",
        "numpy",
        "scipy",
    ],
    entry_points={
        'console_scripts': [
            'leafcli=leafsdk.cli.leafcli:main',
        ],
    },
)
```

---

## 🧩 Mission JSON Format (for uploading via script or CLI)

Here's how you can define a **Leaf Mission** in JSON format:

```json
{
  "mission_name": "inspection_mission_001",
  "start_takeoff_altitude": 30,
  "waypoints": [
    {
      "latitude": 25.276987,
      "longitude": 55.296249,
      "altitude": 30,
      "speed": 5,
      "checkpoint": "start"
    },
    {
      "latitude": 25.277500,
      "longitude": 55.297000,
      "altitude": 50,
      "speed": 5
    },
    {
      "latitude": 25.278000,
      "longitude": 55.297500,
      "altitude": 20,
      "speed": 3,
      "actions": [
        {
          "type": "gimbal_set",
          "pitch": -90,
          "yaw": 0
        }
      ]
    }
  ],
  "conditions": [
    {
      "type": "battery_above",
      "threshold": 30,
      "action": "continue"
    },
    {
      "type": "battery_below",
      "threshold": 20,
      "action": "return_to_checkpoint",
      "checkpoint": "start"
    }
  ],
  "landing": {
    "precision_landing": true
  }
}
```

Each waypoint can have **actions** (like adjusting gimbal, taking a photo).  
You can define **global mission conditions** too (battery failsafe, timeouts, etc.).

---

## 🌟 Summary

| Layer | Example |
|:------|:--------|
| SDK Core | Python classes and modules |
| MAVLink | `pymavlink` connection layer |
| Mission Planner | High-level mission API |
| Gimbal Control | Orientation, stabilization |
| Vision | Visual landing capabilities |
| Packaging | pip installable library |
| Service | Systemd managed service |
| Example Scripts | Provided inside `examples/` |
| Mission Format | JSON-based, extendable |
| Mission Features | Checkpoints, Looping, Failsafes, Vision Landing |
| Extensions | Web API, Live Monitoring, OTA updates |

--- 

#
# LeafSDK Modules

---

## 📡 LeafSDK Connection Module

The `leafsdk.connection` module provides all the functionality needed for establishing, maintaining, and monitoring MAVLink communication with the LeafFC flight controller.

It is designed to be **robust**, **expandable**, and **operator-friendly**, supporting rich logging and future extensions like automatic reconnection or multi-vehicle management.

---

## 📦 Structure

| File | Purpose |
|:-----|:--------|
| `mavlink_interface.py` | Core MAVLink connection handling (send, receive, heartbeat wait, close) |
| `heartbeat_monitor.py` | Live monitoring of heartbeat signals to ensure link health |
| `connection_manager.py` | High-level management of connection lifecycle (connect, health check, close) |

---

## ✈️ Features

- Easy-to-use MAVLink connection via UDP, TCP, Serial
- Automatic heartbeat waiting at connection
- Heartbeat-based link monitoring
- Clean disconnection handling
- Rich colorized logging with `rich`
- Modular structure for easy upgrades (reconnect logic, multi-vehicle, etc.)

---

## ⚙️ How to Use

### 1. Connect to the Drone

```python
from leafsdk.connection.mavlink_interface import MAVLinkInterface

mav = MAVLinkInterface("udp:192.168.1.10:14550")
```

✅ Automatically waits for heartbeat before proceeding.

---

### 2. Send and Receive Messages

```python
# Send a MAVLink message
mav.send_message(my_message)

# Receive a specific type of message
msg = mav.receive_message(type='SYS_STATUS', timeout=5)
if msg:
    print(f"Battery remaining: {msg.battery_remaining}%")
```

---

### 3. Monitor Heartbeat

```python
from leafsdk.connection.heartbeat_monitor import HeartbeatMonitor

monitor = HeartbeatMonitor(mav)
monitor.wait_for_heartbeat(timeout=10)
if monitor.is_alive():
    print("Connection healthy ✅")
```

---

### 4. High-Level Connection Management

```python
from leafsdk.connection.connection_manager import ConnectionManager

conn = ConnectionManager("udp:192.168.1.10:14550")
conn.connect()

# Check connection health periodically
conn.check_health()

conn.close()
```

---

## 🛡️ Logging Example

All connection-related activities are logged clearly in the terminal:

```text
[INFO] 16:24:15 - MAVLinkInterface - Connecting to udp:192.168.1.10:14550 ...
[SUCCESS] 16:24:18 - MAVLinkInterface - Heartbeat received ✅ (System ID: 1)
[INFO] 16:24:22 - HeartbeatMonitor - Waiting for heartbeat...
[SUCCESS] 16:24:24 - HeartbeatMonitor - Heartbeat received ✅ (System ID: 1)
[INFO] 16:24:30 - ConnectionManager - Connection healthy ✅.
```

✅ Consistent  
✅ Colorized  
✅ Operator-friendly

---

## 🏗️ Future Improvements

- Automatic reconnection if heartbeat is lost
- Connection retries with exponential backoff
- Multi-vehicle connection manager
- Connection pooling for fleets
- Logging to files for post-flight analysis

---

## 📋 Quick Reference

| Task | How |
|:-----|:----|
| Open MAVLink connection | `MAVLinkInterface(connection_str)` |
| Close MAVLink connection | `mav.close()` |
| Monitor heartbeat manually | `HeartbeatMonitor(mav)` |
| High-level connect/check/close | `ConnectionManager(connection_str)` |

#
---

# 🚀 Get Connected and Fly!

The `leafsdk.connection` module ensures **reliable**, **traceable**, and **safe** communication between LeafSDK and the drone hardware —  
essential for every critical mission.

#
---

# 🛠️ `leafsdk.service` — LeafSDK Service Module

---

## 🚀 Overview

The `leafsdk.service` module runs LeafSDK as a **background mission service**, managing the **MAVLink connection**, **health monitoring**, and preparing for future mission execution and automation.

It is designed to be run as a **CLI**, **Docker container**, or a **systemd service** on a mission computer or edge device.

---

## 📦 Module Structure

| File                 | Description                                          |
| -------------------- | ---------------------------------------------------- |
| `leaf_service.py`    | Main entry point for launching the service           |
| `service_manager.py` | Manages service lifecycle and connections            |
| `health_checker.py`  | Periodically checks link, battery, and system health |

---

## ✈️ Core Responsibilities

* Establish and maintain a MAVLink connection to LeafFC
* Continuously monitor heartbeat and battery status
* Log system health to the terminal (colorized with `rich`)
* Shut down safely on interrupt (e.g., Ctrl+C or signal)
* Designed for extensibility (mission management, watchdogs)

---

## 🧪 Quick Start

### 🖥️ Run the Service

```bash
python3 -m leafsdk.service.leaf_service
```

This will:

1. Connect to LeafFC (default: `udp:127.0.0.1:14550`)
2. Wait for heartbeat
3. Begin a loop to monitor health and print status

---

## 🧬 Runtime Behavior

```text
[INFO] 12:00 - LeafService - Starting LeafService...
[SUCCESS] 12:01 - MAVLinkInterface - Heartbeat received ✅ (System ID: 1)
[INFO] 12:02 - HeartbeatMonitor - System 1 alive
[INFO] 12:02 - Battery: 72% remaining
...
```

✅ Logs are colorized
✅ Service handles signals and disconnects gracefully

---

## 📋 Service Lifecycle

| Phase              | Description                                |
| ------------------ | ------------------------------------------ |
| Start              | Connects to LeafFC, waits for heartbeat    |
| Running            | Periodically checks system status and logs |
| Interrupt (SIGINT) | Closes connection and shuts down cleanly   |

---

## 🧩 Example Usage in Code

```python
from leafsdk.service.leaf_service import main
main("udp:192.168.1.10:14550")
```

or run from CLI:

```bash
python3 -m leafsdk.service.leaf_service --conn udp:192.168.1.10:14550
```

> 🔧 *Parameterization (e.g., CLI flags for logging, debug, etc.) can be added as needed.*

---

## 🛡️ Health Monitoring Features

| Check              | Description                         |
| ------------------ | ----------------------------------- |
| ✅ Heartbeat        | Warns if lost or missing            |
| ⚡ Battery          | Warns below 30%, errors below 20%   |
| (🛰️ GPS - Future) | Check GPS fix status before takeoff |

---

## 📦 Ready for Production?

Yes. This service is:

* ✅ Runnable via CLI or systemd
* ✅ Logs errors clearly
* ✅ Modular and extensible
* 🧩 Ready for mission queuing, reconnection, simulation, or telemetry streaming

---

## 🏗️ Future Improvements

| Feature                  | Description                                          |
| ------------------------ | ---------------------------------------------------- |
| Mission Executor         | Run a mission automatically if uploaded              |
| Auto-Reconnect           | Retry MAVLink connection on heartbeat loss           |
| WebSocket/REST Interface | Expose service data externally                       |
| Systemd Integration      | Run as background Linux service                      |
| Remote Logging           | Stream status to a central server or cloud dashboard |

---

## 🧠 Summary

`leafsdk.service` turns your SDK into a **live, autonomous mission daemon** —
ready for flight, health tracking, mission uploads, and future mission execution.
It forms the **core background process** that enables the rest of LeafSDK.

#
---
# 🧭 `leafsdk.core.mission` — Mission Planning Module

---

## 🚀 Overview

The `leafsdk.core.mission` module provides a robust and flexible interface for creating, validating, and uploading autonomous drone missions to the LeafFC flight controller. It allows users to define waypoints, incorporate conditional logic, and manage the entire mission lifecycle programmatically or via CLI tools.

---

## 🗂️ Module Structure

| File                 | Description                                                               |
| -------------------- | ------------------------------------------------------------------------- |
| `mission_planner.py` | Core planner for building, uploading, and managing mission steps          |
| `waypoint.py`        | Lightweight data structure representing a waypoint (lat, lon, alt, speed) |
| `condition.py`       | Define and evaluate conditions (e.g., battery level, GPS lock)            |

---

## ✈️ Core Features

* Add and manage GPS waypoints
* Upload full missions to the drone over MAVLink
* Create and apply conditional mission triggers
* Modular design for integration with service and CLI layers
* Easy to extend for gimbal actions, vision, and return-to-launch

---

## 🧱 Waypoint Definition

Waypoints are defined using:

```python
from leafsdk.core.mission.waypoint import Waypoint

wp = Waypoint(latitude=37.7749, longitude=-122.4194, altitude=20.0)
```

They can be converted to MAVLink mission items using:

```python
wp.to_mavlink(seq=0)
```

---

## 🧠 Conditions (Optional Checks)

Conditions can be used to delay or control mission flow.
For example, wait until battery level is sufficient:

```python
from leafsdk.core.mission.condition import BatteryCondition

cond = BatteryCondition(threshold_percent=50)
if cond.check(mav_interface):
    print("Battery OK — Proceed with mission")
```

---

## 🧭 Mission Planner Usage

```python
from leafsdk.core.mission.mission_planner import MissionPlanner
from leafsdk.connection.mavlink_interface import MAVLinkInterface

mav = MAVLinkInterface("udp:192.168.1.10:14550")
planner = MissionPlanner(mav)

planner.add_waypoint(37.7749, -122.4194, 20)
planner.add_waypoint(37.7751, -122.4185, 25)
planner.upload_mission()
```

✅ Automatically clears previous mission
✅ Sends new waypoints to LeafFC
✅ Logs steps with rich-formatted output

---

## 📋 Waypoint Format Details

| Field                | Description                  |
| -------------------- | ---------------------------- |
| `latitude`           | GPS latitude in degrees      |
| `longitude`          | GPS longitude in degrees     |
| `altitude`           | Target altitude in meters    |
| `speed` *(optional)* | Suggested ground speed (m/s) |

---

## 🧩 Integration Points

This module is used by:

* ✅ `leafcli mission` commands (upload, validate)
* ✅ `leafsdk.service` for mission execution automation
* ✅ Future mission editor UIs (LeafScript, web, visual tools)

---

## 🔮 Planned Features

| Feature                   | Description                                                    |
| ------------------------- | -------------------------------------------------------------- |
| Gimbal + Mission Triggers | Coordinate camera angles with waypoints                        |
| Mission Export            | Save/load `.json` or `.yaml` mission plans                     |
| Conditional Branching     | Mission decisions based on environment (battery, vision, etc.) |
| Landing Support           | Add `LAND`, `RETURN_TO_LAUNCH`, and `TAKEOFF` commands         |

---

## ✅ Quick API Reference

| Task             | Code                                         |
| ---------------- | -------------------------------------------- |
| Add waypoint     | `planner.add_waypoint(lat, lon, alt, speed)` |
| Clear all        | `planner.clear_waypoints()`                  |
| Upload mission   | `planner.upload_mission()`                   |
| Define condition | `BatteryCondition(threshold_percent=60)`     |
| Check condition  | `condition.check(mav)`                       |

---

## 🧠 Summary

The `leafsdk.core.mission` module empowers developers and operators to define rich autonomous missions for drones. It is:

✅ Modular
✅ MAVLink-compatible
✅ CLI-integrated
✅ Production-ready

#
---

# 📷 `leafsdk.core.vision` — Vision Intelligence Module

---

## 🚀 Overview

The `leafsdk.core.vision` module enables computer vision capabilities for autonomous drones using **OpenCV**. It provides:

* Vision-based landing using **ArUco marker detection**
* Frame-to-frame drift estimation via **optical flow**
* A modular structure ready for advanced features like **object tracking**, **pose estimation**, and **vision-based navigation**

---

## 🧠 Use Cases

| Feature                 | Purpose                                                    |
| ----------------------- | ---------------------------------------------------------- |
| Vision Landing          | Detect landing markers and guide autonomous descent        |
| Optical Flow            | Detect horizontal drift, rotation, or stabilization cues   |
| Vision Condition Checks | Wait for a marker or visual event before next waypoint     |
| Future Additions        | Pose-based control, AI-based object following, visual SLAM |

---

## 🗂️ Module Structure

| File                   | Description                                            |
| ---------------------- | ------------------------------------------------------ |
| `vision_landing.py`    | Detect ArUco markers and track their position in frame |
| `camera_stabilizer.py` | Estimate motion drift using optical flow (Farneback)   |

---

## 🔧 Installation Requirements

Make sure your project includes these dependencies:

```bash
pip install opencv-python numpy
```

---

## 🛬 Vision-Based Landing

```python
from leafsdk.core.vision.vision_landing import VisionLanding

vl = VisionLanding()
vl.start_camera()

try:
    vl.track_and_land_loop()  # Continuously detect markers
except KeyboardInterrupt:
    vl.stop_camera()
```

### 🔍 How It Works

* Uses `cv2.aruco.detectMarkers()` to find known ArUco tags
* Calculates the center of the marker
* Intended for feedback into **landing logic**

---

## 🎥 Camera Stabilization via Optical Flow

```python
from leafsdk.core.vision.camera_stabilizer import CameraStabilizer
import time

cs = CameraStabilizer()

try:
    while True:
        flow = cs.compute_optical_flow()
        if flow is not None:
            print(f"Drift: dx={flow[0]:.2f}, dy={flow[1]:.2f}")
        time.sleep(0.2)
except KeyboardInterrupt:
    cs.release()
```

### 🔍 How It Works

* Uses Farneback optical flow (`cv2.calcOpticalFlowFarneback`)
* Estimates average drift across entire frame
* Useful for detecting motion instability, tracking drift, or gimbal calibration

---

## ✅ Features Summary

| Capability             | Implemented |
| ---------------------- | ----------- |
| ArUco Marker Detection | ✅           |
| Camera Feed Handling   | ✅           |
| Drift via Optical Flow | ✅           |
| Logging with `rich`    | ✅           |
| Pose Estimation        | 🔜 Planned  |
| AprilTag Support       | 🔜 Optional |
| MAVLink Feedback Loop  | 🔜 Optional |

---

## 🔮 Future Vision Features (Planned / Extendable)

| Feature                 | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| Vision-Aided Landing    | Use offset from center to issue MAVLink commands             |
| AprilTag Support        | Replace/extend ArUco with AprilTags                          |
| Object Tracking         | Use bounding boxes or feature tracking for targets           |
| Vision-Based Conditions | Integrate into mission logic: `wait_until_marker_detected()` |
| Target Following        | Follow a visual target (static or dynamic)                   |

---
## 🧠 Summary

The `leafsdk.core.vision` module gives your drone **eyes** — enabling perception, precision landings, and visual tracking.

✅ Lightweight
✅ OpenCV-based
✅ Plug-and-play
✅ Ready for AI-powered extensions

---

> 🌿 “Vision gives intelligence to movement.” — LeafSDK
