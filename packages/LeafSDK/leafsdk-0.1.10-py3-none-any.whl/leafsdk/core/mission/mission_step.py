# leafsdk/core/mission/mission_step.py
import traceback
from pymavlink import mavutil
from pymavlink.dialects.v20 import droneleaf_mav_msgs as leafMAV
from abc import ABC, abstractmethod
from  leafsdk.core.mission.trajectory import WaypointTrajectory #, TrajectorySampler
import leafsdk.utils.mavlink_helpers as mav_helpers
import time
import redis
import json

from petal_app_manager.plugins.base import Petal
from petal_app_manager.plugins.decorators import http_action, websocket_action
from petal_app_manager.proxies.localdb import LocalDBProxy
from petal_app_manager.proxies.external import MavLinkExternalProxy
from petal_app_manager.proxies.redis import RedisProxy


from typing import Dict, Any, List, Optional, Tuple

from leafsdk import logger
import uuid

class _MissionStep(ABC):
    @abstractmethod
    def __init__(self, mav_proxy: MavLinkExternalProxy = None):
        self.result = True # Indicates the logical output of the step (mostly used for conditional steps)
        self.completed = False # Indicates if the step has been completed
        self.paused = False # Indicates if the step is currently paused
        self.info = None # Used to store any additional information about the step
        self._exec_count = 0 # Counter to track how many times the step has been executed
        self._start_count = 0 # Counter to when the step was started
        self._is_pausable = True # Indicates if the step can be paused
        self.mav_proxy = mav_proxy
        self.is_cancelled = False

    @abstractmethod
    def _execute_step_mission_step_logic(self):
        raise NotImplementedError("Each subclass must implement `execute()`")
        

    @abstractmethod
    def to_dict(self) -> dict:
        raise NotImplementedError("Each subclass must implement `to_dict()`")
    
    @abstractmethod
    def log_info(self):
        raise NotImplementedError("Each subclass must implement `__str__()`")
    
    @abstractmethod
    def description(self) -> str:
        """
        Returns a string description of the step.
        This is used for logging and debugging purposes.
        """
        raise NotImplementedError("Each subclass must implement `description()`")

    @classmethod
    @abstractmethod
    def from_dict(cls, params: dict):
        raise NotImplementedError("Each subclass must implement `from_dict()`")
    
    def execute_step(self):
        # Check cancellation before executing
        if self.is_cancelled:
            return self.result, self.completed, self.info
        
        if self._exec_count == 0:
            self.log_info()
        if not self.completed and not self.is_cancelled: 
            self._execute_step_mission_step_logic()
            self._exec_count += 1
            
        return self.result, self.completed, self.info
    
    def feed_info(self, info: Dict[str, Any]):
        """
        Feed additional information to the step.
        This can be used to pass data from the mission plan to the step.
        """
        self.info = info
        logger.debug(f"Feeding info to {self.__class__.__name__}: {info}")


class __Goto(_MissionStep):
    def __init__(
            self, 
            mav_proxy: MavLinkExternalProxy = None,
            redis_proxy: RedisProxy = None,
            waypoints: Optional[List[List[float]]] = None,
            yaws_deg: Optional[List[float]] = None,
            speed: float = 2.0,
            yaw_mode: str = 'lock',
            cartesian: bool = False,
            **kwargs
        ):
        super().__init__(mav_proxy)

        if waypoints is None and yaws_deg is None:
            raise ValueError("Either waypoints or yaws_deg must be provided.")
        if waypoints is not None and yaws_deg is not None:
            assert len(waypoints) == len(yaws_deg), \
                f"Expected {len(waypoints)} yaw values, got {len(yaws_deg)}"

        self.speed = speed
        self.yaws_deg = yaws_deg
        self.yaw_mode = yaw_mode
        self.cartesian = cartesian
        self.waypoints = waypoints
        self.target_waypoint = waypoints[-1]  # Last waypoint is the target
        self.target_yaw = yaws_deg[-1] if yaws_deg is not None else 0.0  # Last yaw is the target
        self.yaw_offset = 0.0  # Default yaw offset
        self.waypoint_offset = [0.0, 0.0, 0.0]  # Default position offset
        self.redis_proxy = redis_proxy
        self.trajectory = None
        self.uuid_str = str(uuid.uuid4())
        

    def setup_redis_subscriptions(self):
        """Setup Redis subscriptions - call this after object creation if using Redis"""
        if self.redis_proxy is None:
            logger.warning("Redis proxy not provided, skipping Redis subscriptions")
            return
            
        try:
            # Subscribe to a general broadcast channel
            self.redis_proxy.register_pattern_channel_callback("/petal-leafsdk/__Goto/notify_trajectory_completed", self._handle_notify_trajectory_completed)

            logger.info(f"Redis subscriptions set up successfully for {self.__class__.__name__}")
        except Exception as e:
            logger.error(f"Failed to set up Redis subscriptions: {e}")

    def unsetup_redis_subscriptions(self):
        """Unsubscribe from Redis channels - call this when the step is no longer needed"""
        if self.redis_proxy is None:
            logger.warning("Redis proxy not provided, skipping Redis unsubscriptions")
            return
            
        try:
            self.redis_proxy.unregister_pattern_channel_callback("/petal-leafsdk/__Goto/notify_trajectory_completed")
            logger.info(f"Redis subscriptions for {self.__class__.__name__} have been removed.")
        except Exception as e:
            logger.error(f"Failed to remove Redis subscriptions: {e}")

    def cancel(self):
        """Cancel the current step execution"""
        self.is_cancelled = True
        self.completed = True
        self.result = False
        self.unsetup_redis_subscriptions()
        
        # Send stop trajectory command
        if self.redis_proxy is not None:
            try:
                stop_msg = json.dumps({
                    "command": "stop_trajectory", 
                    "trajectory_id": self.uuid_str
                })
                self.redis_proxy.publish('/traj_sys/stop_trajectory', stop_msg)
                logger.info("Trajectory stop command sent")
            except Exception as e:
                self.is_cancelled = False
                logger.error(f"Failed to send trajectory stop: {e}")

        logger.info(f"Goto step cancelled")

    def _handle_notify_trajectory_completed(self, channel: str, message: str):
        """Handle notification messages for trajectory completion."""
        
        # Check if step is cancelled before processing
        if self.is_cancelled:
            logger.info(f"Ignoring trajectory completion notification - step is cancelled")
            return
    
        logger.info(f"Received notification on {channel}: {message}")

        try:
            # Try to parse as JSON
            command_data = json.loads(message)
            # trajectory_id = command_data.get("value")
            trajectory_id = command_data.get("trajectory_id")
            
            # Example message format:
            # {
            #     "source_queue":"trajectory_queue",
            #     "trajectory_id":"Polynomial/Line/takeoff_1_5m_5s.json",
            #     "current_num_of_queued_trajs":0
            # }

            
            if trajectory_id:
                self.completed = True
                self.unsetup_redis_subscriptions()
                logger.info(f"Trajectory completed: {trajectory_id}")
            else:
                logger.warning(f"Received notification without trajectory_id: {message}")
                    
        except json.JSONDecodeError:
            logger.warning(f"Received non-JSON command: {message}")
        except Exception as e:
            logger.error(f"Error handling command: {e}")

    def _execute_step_mission_step_logic(self):
        if self._exec_count == 0:
            self.setup_redis_subscriptions()
            try:
                self.yaw_offset = self.info["yaw_offset"] # TODO: Not sure when are these received
                self.waypoint_offset = self.info["waypoint_offset"]
                self.info.update({
                    "waypoint_offset": self.waypoints[-1],
                    "yaw_offset": self.yaws_deg[-1]
                })
                logger.debug(f"Using waypoint offset: {self.waypoint_offset} and yaw offset: {self.yaw_offset}")
                traj_data, traj_json = self._compute_trajectory(self.waypoints, self.yaws_deg, self.speed,
                                        home=self.waypoint_offset, home_yaw=self.yaw_offset,
                                        yaw_mode=self.yaw_mode, cartesian=self.cartesian) # TODO: refactor and move to __init__

            except Exception as e:
                logger.error(f"❌ Error computing trajectory: {e}")
                logger.error(traceback.format_exc())
                raise e
            
            try:
                if self.redis_proxy is not None:
                    logger.info(f"📤 Publishing trajectory JSON: {traj_json}")
                    self.redis_proxy.publish(
                        channel='/traj_sys/queue_traj_primitive_pos',
                        message=traj_json,
                    )
                    logger.info(f"✅ Trajectory published to Redis successfully")
                else:
                    logger.warning("⚠️ Redis proxy not available, skipping trajectory publication")
            except Exception as e:
                logger.error(f"❌ Error publishing trajectory through redis: {e}")


    def _compute_trajectory(self,waypoints: Optional[List[List[float]]] = None,yaws_deg: Optional[List[float]] = None,speed: float = 2.0,
                           home : Optional[List[float]] = None,home_yaw: Optional[float] = None,yaw_mode: str = 'lock', cartesian: bool = False) ->  Tuple[Dict[str, Any], str]:

        # Create a trajectory sampler based on the waypoints and yaws
        self.trajectory = WaypointTrajectory(
            waypoints=waypoints,
            yaws_deg=yaws_deg,
            speed=speed,
            home=home,
            home_yaw=home_yaw,
            yaw_mode=yaw_mode,
            cartesian=cartesian
        )
        
        traj_data, traj_json = self.trajectory.build_polynomial_trajectory_json(self.uuid_str)
        
        return traj_data, traj_json

    def to_dict(self):
        return {
            "waypoints": self.waypoints,
            "yaws_deg": self.yaws_deg,
            "yaw_mode": self.yaw_mode,
            "speed": self.speed,
        }
    
    def log_info(self):
        logger.info(f"➡️ Executing Goto to ({self.target_waypoint[0]}, {self.target_waypoint[1]}, {self.target_waypoint[2]})")

    def description(self) -> str:
        """
        Returns a string description of the step.
        This is used for logging and debugging purposes.
        """
        return f"Goto to ({self.target_waypoint[0]}, {self.target_waypoint[1]}, {self.target_waypoint[2]}) with speed {self.speed} m/s and yaw mode {self.yaw_mode}."


    @classmethod
    def from_dict(cls, params: Dict[str, Any]) -> "__Goto":
        if any(key not in params for key in ["waypoints",]):
            logger.error("Missing required parameters for Goto.")
            raise ValueError("Missing required parameters: 'waypoints'.")

        # get required parameters
        args = {
            "waypoints": params.pop("waypoints"),
        }
        args.update(dict(params))

        return cls(**args)


class GotoGPSWaypoint(__Goto):
    def __init__(self, waypoints, mav_proxy: MavLinkExternalProxy=None, redis_proxy: RedisProxy = None, yaws_deg=None, speed: float=2.0, yaw_mode: str='lock'):
        super().__init__(waypoints=waypoints, mav_proxy=mav_proxy, redis_proxy=redis_proxy, yaws_deg=yaws_deg, speed=speed, yaw_mode=yaw_mode, cartesian=False)

    def log_info(self):
        logger.info(f"➡️ Executing GotoGPSWaypoint to ({self.target_waypoint[0]}, {self.target_waypoint[1]}, {self.target_waypoint[2]})")

class GotoLocalPosition(__Goto):
    def __init__(self, waypoints, mav_proxy: MavLinkExternalProxy=None, redis_proxy: RedisProxy = None, yaws_deg=None, speed: float=2.0, yaw_mode: str='lock'):
        super().__init__(waypoints=waypoints, mav_proxy=mav_proxy, redis_proxy=redis_proxy, yaws_deg=yaws_deg, speed=speed, yaw_mode=yaw_mode, cartesian=True)

    def log_info(self):
        logger.info(f"➡️ Executing GotoLocalPosition to ({self.target_waypoint[0]}, {self.target_waypoint[1]}, {self.target_waypoint[2]})")

class Takeoff(_MissionStep):
    def __init__(self, mav_proxy: MavLinkExternalProxy = None, alt: float = 1.0, redis_proxy: RedisProxy = None):
        super().__init__(mav_proxy)
        self._is_pausable = False  # Takeoff step cannot be paused
        self.alt = alt
        self.waypoint_offset = [0.0, 0.0, 0.0]  # Default position offset
        self.yaw_offset = 0.0  # Default yaw offset
        self.__offset_pos_recved = False
        self.__offset_yaw_recved = False

        def handler_pos(msg: mavutil.mavlink.MAVLink_message) -> bool:
            self.waypoint_offset = [msg.x, msg.y, msg.z]
            self.__offset_pos_recved = True
            logger.info(f"Received external trajectory offset position: {self.waypoint_offset}")
            return True

        def handler_ori(msg: mavutil.mavlink.MAVLink_message) -> bool:
            self.yaw_offset = msg.z
            self.__offset_yaw_recved = True
            logger.info(f"Received external trajectory offset yaw: {self.yaw_offset}")
            return True
        
        self._handler_pos = handler_pos
        self._handler_ori = handler_ori

        if mav_proxy is not None:
            mav_proxy.register_handler(
                key=str(leafMAV.MAVLINK_MSG_ID_LEAF_EXTERNAL_TRAJECTORY_OFFSET_ENU_POS),
                fn=self._handler_pos,
                duplicate_filter_interval=0.7
            )

            mav_proxy.register_handler(
                key=str(leafMAV.MAVLINK_MSG_ID_LEAF_EXTERNAL_TRAJECTORY_OFFSET_ENU_ORI),
                fn=self._handler_ori,
                duplicate_filter_interval=0.7
            )
        else:
            logger.warning("MavLinkExternalProxy is not provided, external trajectory offsets will not be received.")

    def _execute_step_mission_step_logic(self):
        if self.mav_proxy is not None:
            msg = leafMAV.MAVLink_leaf_do_takeoff_message(
                target_system=self.mav_proxy.target_system,
                altitude=self.alt
                )
            self.mav_proxy.send(key='mav', msg=msg,burst_count=4, burst_interval=0.1)
        else:
            logger.warning("MavLinkExternalProxy is not provided, cannot send takeoff message.")

        if self.__offset_pos_recved and self.__offset_yaw_recved:
            self.waypoint_offset[-1] += self.alt  # Adjust the altitude offset
            self.info.update({
                "waypoint_offset": self.waypoint_offset,
                "yaw_offset": self.yaw_offset
            })
            logger.debug(f"Takeoff with waypoint offset: {self.waypoint_offset} and yaw offset: {self.yaw_offset}")
            self.completed = True

    def to_dict(self):
        return {"alt": self.alt}
    
    def log_info(self):
        logger.info(f"🛫 Executing Takeoff to altitude {self.alt}m")
    def description(self) -> str:
        """
        Returns a string description of the step.
        This is used for logging and debugging purposes.
        """
        return f"Takeoff to altitude {self.alt}m."
    @classmethod
    def from_dict(cls, params: Dict[str, Any]) -> "__Goto":
        if any(key not in params for key in ["alt",]):
            logger.error("Missing required parameters for Takeoff.")
            raise ValueError("Missing required parameters: 'alt'.")

        # get required parameters
        args = {
            "alt": params.pop("alt"),
        }
        args.update(dict(params))

        return cls(**args)



class Wait(_MissionStep):
    def __init__(self, duration, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        super().__init__(mav_proxy)
        self.duration = duration
        self._is_pausable = False  # Wait step is not pausable
        self.tick = 0 # Used to track the start time of the wait 

    def _execute_step_mission_step_logic(self):
        if self._exec_count == 0:
            self.tick = time.time()
        else:
            elapsed_time = time.time() - self.tick
            if elapsed_time >= self.duration:
                logger.info("✅ Done: Wait completed!")
                self.completed = True

    def to_dict(self):
        return {"duration": self.duration}
    
    def log_info(self):
        logger.info(f"⏲️ Executing Wait for {self.duration} seconds...")
    def description(self) -> str:
        """
        Returns a string description of the step.
        This is used for logging and debugging purposes.
        """
        return f"Wait for {self.duration} seconds."
    

    
    @classmethod
    def from_dict(cls, params: Dict[str, Any]) -> "__Goto":
        if any(key not in params for key in ["duration",]):
            logger.error("Missing required parameters for Wait.")
            raise ValueError("Missing required parameters: 'duration'.")

        # get required parameters
        args = {
            "duration": params.pop("duration"),
        }
        args.update(dict(params))

        return cls(**args)

class Land(_MissionStep):
    def __init__(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        super().__init__(mav_proxy)
        self._is_pausable = False

    def _execute_step_mission_step_logic(self):
        if self.mav_proxy is not None:
            msg = leafMAV.MAVLink_leaf_do_land_message(
                target_system=self.mav_proxy.target_system,
                )
            self.mav_proxy.send(key='mav', msg=msg,burst_count=4, burst_interval=0.1)
        else:
            logger.warning("MavLinkExternalProxy is not provided, cannot send land message.")

        self.completed = True

    def to_dict(self):
        return {}
    
    def log_info(self):
        logger.info("🛬 Executing Land: Landing...")
    
        
    def description(self) -> str:
        """
        Returns a string description of the step.
        This is used for logging and debugging purposes.
        """
        return "Land: Landing the drone."



    @classmethod
    def from_dict(cls, params):
        return cls(**params)


class Dummy(_MissionStep):
    def __init__(self, dummy=1, mav_proxy: MavLinkExternalProxy = None):
        super().__init__(mav_proxy)
        self.dummy = dummy
        self._is_pausable = False

    def _execute_step_mission_step_logic(self):
        pass

    def to_dict(self):
        return {'dummy': self.dummy}
    
    def log_info(self):
        logger.info(f"➡️ Executing dummy!")
        
    def description(self) -> str:
        """
        Returns a string description of the step.
        This is used for logging and debugging purposes.
        """
        return f"Dummy step with dummy value {self.dummy}."


    @classmethod
    def from_dict(cls, params):
        return cls(**params)
    

def step_from_dict(step_type: str, params: dict, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None) -> _MissionStep:
    step_classes = {
        "Takeoff": Takeoff,
        "GotoGPSWaypoint": GotoGPSWaypoint,
        "GotoLocalPosition": GotoLocalPosition,
        "Wait": Wait,
        "Land": Land,
        "Dummy": Dummy,
        # Add more here
    }
    cls = step_classes.get(step_type)
    if cls is None:
        raise ValueError(f"Unknown mission_step type: {step_type}")
    
    # Always pass mav_proxy to all step constructors
    params['mav_proxy'] = mav_proxy
    params['redis_proxy'] = redis_proxy
    return cls.from_dict(params)