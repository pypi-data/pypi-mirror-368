# leafsdk/core/mission/mission_plan.py

import sys, time
import os
import json
import traceback
import networkx as nx
import matplotlib.pyplot as plt
from leafsdk import logger
# Add pymavlink to path
from petal_app_manager.proxies.external import MavLinkExternalProxy
from petal_app_manager.proxies.redis import RedisProxy
from leafsdk.core.mission.mission_step import _MissionStep, step_from_dict
from pymavlink.dialects.v20 import droneleaf_mav_msgs as leafMAV


class MissionPlan:
    def __init__(self, mav_proxy: MavLinkExternalProxy = None, name: str="UnnamedMission", redis_proxy: RedisProxy = None):
        self.name = name
        self.status = {
            "completed_mission_step_id": None,
            "completed_mission_step_description": None,
            "next_mission_step_id": None,
            "next_mission_step_description": None,
            "step_completed": False,
            "is_paused": False,
            "is_cancelled": False,
        }
        self.running = False
        self.__current_step = None
        self.__info = {}
        self.__validated = False
        self.__mav_proxy = mav_proxy
        self.__redis_proxy = redis_proxy
        self.__graph = nx.MultiDiGraph()
        self.__current_node = None
        self.__head_node = None
        self.__last_added_node = None
        self.__is_paused = False
        self.__is_cancelled = False

    def add(self, to_name: str, to_step: _MissionStep, from_name: str=None, condition=None):
        first_node = not self.__graph.nodes
        self.add_step(to_name, to_step)
        if first_node:
            self.set_start(to_name)
        if from_name:
            self.add_transition(from_name, to_name, condition)
        elif self.__last_added_node:
            self.add_transition(self.__last_added_node, to_name, condition)
        self.__last_added_node = to_name

    def add_step(self, name: str, step: _MissionStep):
        if name in self.__graph:
            raise ValueError(f"Node name '{name}' already exists in mission plan '{self.name}'.")
        self.__graph.add_node(name, step=step)

    def add_transition(self, from_step: str, to_step: str, condition=None):
        self.__graph.add_edge(from_step, to_step, condition=condition, key=None)

    def set_start(self, name: str):
        if name not in self.__graph:
            raise ValueError(f"Start node '{name}' not found in mission graph.")
        self.__current_node = name
        self.__head_node = name
        self.__current_step = self.__graph.nodes[name]['step']

    def run_step(self):
        self.running = True

        # Add null check for current_step before accessing its attributes
        if self.__current_step is None:
            logger.error("❌ Cannot run step: no current step available")
            self.running = False
            self.status = {
                "completed_mission_step_id": None,
                "completed_mission_step_description": "No step available",
                "next_mission_step_id": None,
                "next_mission_step_description": "Mission failed or completed",
                "step_completed": False,
                "is_paused": self.__is_paused,
                "is_cancelled": self.__is_cancelled
            }
            return self.running, self.status

        if self.__current_step._exec_count == 0:
            self.__current_step.feed_info(self.__info)
            logger.info(f"➡️ Executing step: {self.__current_node}")

        try:
            result, completed, self.__info = self.__current_step.execute_step()
        except Exception as e:
            logger.error(f"❌ Step {self.__current_node} failed: {e}\n{traceback.format_exc()}")
            self.running = False
            # Store the failed node info before clearing
            failed_node = self.__current_node
            self.__current_node = None
            self.__current_step = None
            self.status = {
                "completed_mission_step_id": str(failed_node) if failed_node else None,
                "completed_mission_step_description": "Step failed with error",
                "next_mission_step_id": None,
                "next_mission_step_description": "Mission failed",
                "step_completed": False,
                "is_paused": False,
                "is_cancelled": True  # Mark as cancelled when step fails
            }
            return self.running, self.status

        if completed:
            if self.__is_paused:
                # msg = leafMAV.MAVLink_leaf_control_cmd_message(
                #             target_system=self.__mav_proxy.target_system,
                #             cmd=0
                #         )
                # self.__mav_proxy.send(key='mav', msg=msg, burst_count=4, burst_interval=0.1)
                self.status={
                    "completed_mission_step_id": str(self.__current_node),
                    "completed_mission_step_description": self.__graph.nodes[self.__current_node]['step'].description(),
                    "next_mission_step_id": None,
                    "next_mission_step_description": "Mission paused!",
                    "step_completed": completed,
                    "is_paused": True,
                    "is_cancelled": False
                }
                return self.running, self.status
            
            if self.__is_cancelled:
                self.running = False
                self.status={
                        "completed_mission_step_id": str(self.__current_node),
                        "completed_mission_step_description": self.__graph.nodes[self.__current_node]['step'].description(),
                        "next_mission_step_id": None,
                        "next_mission_step_description": "Mission cancelled!",
                        "step_completed": completed,
                        "is_paused": False,
                        "is_cancelled": True
                    }
                return self.running, self.status
            
            next_node = None
            for successor in self.__graph.successors(self.__current_node):
                condition = self.__graph.edges[self.__current_node, successor, 0].get("condition")
                if condition is None or condition == result:
                    next_node = successor
                    break
            prev_node = self.__current_node
            self.__current_node = next_node

            if self.__current_node is None:
                self.running = False
                logger.info("✅ Mission complete.")
                return self.running, self.status
            else:
                self.__current_step = self.__graph.nodes[next_node]['step']
            
            self.status={
                "completed_mission_step_id": str(prev_node),
                "completed_mission_step_description": self.__graph.nodes[prev_node]['step'].description(),
                "next_mission_step_id": str(next_node) if next_node else None,
                "next_mission_step_description": self.__graph.nodes[next_node]['step'].description() if next_node else "Mission completed!",
            }
        self.status["step_completed"] = completed
        self.status["is_paused"] = False
        self.status["is_cancelled"] = False

        return self.running, self.status

    @property
    def current_step(self):
        """Get the current mission step being executed."""
        return self.__current_step

    def pause(self):
        """Pause the mission execution."""
        if self.__is_paused:
            logger.warning("⚠️ Mission is already paused.")
            return False
        
        if self.__is_cancelled:
            logger.error("❌ Cannot pause a cancelled mission.")
            return False
        
        if self.__current_step is None:
            logger.error("❌ Cannot pause, no current step to pause.")
            return False
        
        # Call the pause method of the current step
        # self.current_step.pause()
        self.__is_paused = True
        self.__paused_at_node = self.__current_node
        logger.info(f"⏸️ Mission paused at step: {self.__current_node}")
        
        # Update status to reflect pause state
        self.status["is_paused"] = True
        
        return True

    def resume(self):
        """Resume the mission execution."""
        if not self.__is_paused:
            logger.warning("⚠️ Mission is not paused.")
            return False
        
        if self.__is_cancelled:
            logger.error("❌ Cannot resume a cancelled mission.")
            return False
        
        if self.__current_step is None:
            logger.error("❌ Cannot resume, no current step to resume.")
            return False

        # Call the resume method of the current step
        # self.current_step.resume()
        self.__is_paused = False
        logger.info(f"▶️ Mission resumed from step: {self.__current_node}")
        
        # Update status to reflect resumed state
        self.status["is_paused"] = False

        msg = leafMAV.MAVLink_leaf_control_cmd_message(
                            target_system=self.__mav_proxy.target_system,
                            cmd=1
                        )
        self.__mav_proxy.send(key='mav', msg=msg, burst_count=4, burst_interval=0.1)
        
        return True

    def is_paused(self):
        """Check if the mission is currently paused."""
        return self.__is_paused

    def cancel(self):
        """Cancel the mission execution completely."""
        if self.__is_cancelled:
            logger.warning("⚠️ Mission is already cancelled.")
            return False
        
        if self.__current_step is None:
            logger.error("❌ Cannot cancel, no current step to cancel.")
            return False
        
        # Call the cancel method of the current step
        # self.current_step.cancel()  # Ensure the current step can handle cancellation
        # ACTUALLY CANCEL THE CURRENT STEP
        if hasattr(self.__current_step, 'cancel'):
            self.__current_step.cancel()
            logger.info(f"❌ Current step cancelled: {self.__current_step}")

        self.__is_cancelled = True
        self.__is_paused = False
        logger.info(f"❌ Mission cancelled at step: {self.__current_node}")
        
        # Update status to reflect cancelled state
        self.status["is_cancelled"] = True
        self.status["is_paused"] = False

        # msg = leafMAV.MAVLink_leaf_control_cmd_message(
        #                     target_system=self.__mav_proxy.target_system,
        #                     cmd=2
        #                 )
        # self.__mav_proxy.send(key='mav', msg=msg, burst_count=4, burst_interval=0.1)
        
        # Send MAVLink cancel command
        if self.__mav_proxy is not None:
            msg = leafMAV.MAVLink_leaf_control_cmd_message(
                                target_system=self.__mav_proxy.target_system,
                                cmd=2
                            )
            self.__mav_proxy.send(key='mav', msg=msg, burst_count=4, burst_interval=0.1)

        return True

    def is_cancelled(self):
        """Check if the mission has been cancelled."""
        return self.__is_cancelled

    def add_subplan(self, subplan, prefix: str, connect_from: str=None, condition=None):
        if connect_from is None:
            connect_from = self.__last_added_node
        renamed_nodes = {}
        for name, data in subplan.__graph.nodes(data=True):
            new_name = f"{prefix}_{name}"
            self.__graph.add_node(new_name, **data)
            renamed_nodes[name] = new_name

        for u, v, edata in subplan.__graph.edges(data=True):
            self.__graph.add_edge(renamed_nodes[u], renamed_nodes[v], **edata)

        self.add_transition(connect_from, renamed_nodes[subplan.__head_node])
    
    def save(self, filepath: str):
        self.__validate()
        data = {
            "id": self.name,
            "nodes": [
                {
                    "name": name,
                    "type": step.__class__.__name__,
                    "params": step.to_dict()
                }
                for name, step in self.__get_steps()
            ],
            "edges": [
                {"from": u, "to": v, "condition": self.__graph.edges[u, v, k].get("condition")}
                for u, v, k in self.__graph.edges
            ]
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ MissionPlan file exported to: {filepath}")

    def reset(self):
        """Reset the mission plan to its initial state."""
        self.__graph.clear()
        self.__current_step = None
        self.__current_node = None
        self.__head_node = None
        self.__last_added_node = None
        self.__is_paused = False
        self.__is_cancelled = False
        self.status = {
            "completed_mission_step_id": None,
            "completed_mission_step_description": None,
            "next_mission_step_id": None,
            "next_mission_step_description": None,
            "step_completed": False,
            "is_paused": False,
            "is_cancelled": False,
        }
        logger.info("✅ MissionPlan has been reset.")

    def load_from_dict(self, mission_graph: dict):
        self.reset()
        self.name = mission_graph.get("id", "UnnamedMission")
        for i, node in enumerate(mission_graph["nodes"]):
            step = step_from_dict(node["type"], node["params"], mav_proxy=self.__mav_proxy, redis_proxy=self.__redis_proxy)
            self.add_step(node["name"], step)
            if i == 0:
                self.set_start(node["name"])

        for edge in mission_graph["edges"]:
            self.add_transition(edge["from"], edge["to"], edge.get("condition"))
        
        logger.info(f"✅ MissionPlan is loaded.")

    def load_from_json(self, filepath: str):
        with open(filepath, "r") as f:
            data = json.load(f)

        self.__graph.clear()
        self.name = data.get("id", "UnnamedMission")
        for i, node in enumerate(data["nodes"]):
            step = step_from_dict(node["type"], node["params"], mav_proxy=self.__mav_proxy)
            self.add_step(node["name"], step)
            if i == 0:
                self.set_start(node["name"])

        for edge in data["edges"]:
            self.add_transition(edge["from"], edge["to"], edge.get("condition"))
        
        logger.info(f"✅ MissionPlan file loaded from: {filepath}")

    def export_dot(self, filepath: str):
        try:
            from networkx.drawing.nx_pydot import write_dot
        except ImportError:
            logger.error("❌ pydot or pygraphviz is required to export DOT files. Please install via pip.")

        # Add 'label' attributes to edges using the 'condition' attribute
        for u, v, data in self.__graph.edges(data=True):
            if 'condition' in data:
                condition = data['condition']
                data['label'] = str(condition) if condition is not None else ''

        write_dot(self.__graph, filepath)
        logger.info(f"✅ DOT file exported to: {filepath}")

    def prepare(self):
        self.__validate()

    def __get_steps(self):
        for name, data in self.__graph.nodes(data=True):
            yield name, data['step']

    def __validate(self):
        errors = []
        for node in self.__graph.nodes:
            successors = list(self.__graph.successors(node))
            if len(successors) > 1:
                seen_conditions = set()
                for succ in successors:
                    edge_data = self.__graph.get_edge_data(node, succ)
                    condition = edge_data[0].get("condition")
                    if condition is None:
                        errors.append(f"Missing condition for edge {node} → {succ}")
                    elif condition in seen_conditions:
                        errors.append(f"Duplicate condition '{condition}' for branching at {node}")
                    else:
                        seen_conditions.add(condition)

        if errors:
            for e in errors:
                logger.error(f"❌ [prepare] {e}")
            raise ValueError("Mission plan validation failed. See errors above.")
        else:
            self.__validated = True
            logger.info("✅ Mission plan has been validated.")