# leafsdk/core/mission/trajectory.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.interpolate import CubicSpline
from leafsdk.core.utils.transform import gps_to_relative_3d, wrap_to_pi, deg2rad

import json
from typing import Sequence, List, Tuple, Dict, Any

from leafsdk import logger

_EPS = 1e-9                                     # length below which we treat path as static



class WaypointTrajectory:
    def __init__(self, waypoints=None, yaws_deg=None, speed: float=2.0, yaw_mode: str='lock', 
                 home=(0, 0, 0), home_yaw=0, dt: float=1/50, cartesian: bool=False):
        self.home = home
        self.home_yaw = home_yaw
        self.raw_waypoints = waypoints
        self.yaws_deg = yaws_deg
        self.speed = speed
        self.yaw_mode = yaw_mode
        self.dt = dt
        self.cartesian = cartesian
        self.relative_yaws = self._convert_yaw_to_relative()
        self.relative_points = self._convert_cartesian_to_relative() if cartesian else self._convert_gps_to_relative()
        self.ts, self.pos, self.vel, self.acc, self.yaw, self.yaw_rate, self.poly_coeff, self.time_scale, self.spatial_scale,self.rotation_axis, self.rotation_angle= self._generate_trajectory()

    def _build_polynomial_trajectory_json(self,
        poly_coeff: Sequence[Sequence[float]],
        time_scale: float,
        trajectory_id: str,
        base_time: float = 1.0,
        rotation_axis: Sequence[float] = (1, 0, 0),
        spatial_scale: Sequence[float] = (1, 1, 1),
        trajectory_type: str = "PolynomialTrajectory",
        rotation_angle: float = 0.0,
    ) -> Tuple[Dict[str, Any], str]:
        """
        Build a simplified polynomial trajectory JSON representation.

        Parameters
        ----------
        poly_coeff : Sequence[Sequence[float]]
            3×N (rows = x,y,z) polynomial coefficient matrix. Each inner sequence length must match.
            Format is whatever your consumer expects (e.g. packed reversed time-domain coefficients).
        time_scale : float
            External time scaling factor (dimensionless). Often 1.0 if unused.
        trajectory_id : str
            Identifier / path / filename key (e.g. "Polynomial/Line/BlueRov2/y_neg_1m_5s.json").
        base_time : float, default 1.0
            Base segment duration T in seconds used when mapping t∈[0,T].
        rotation_axis : Sequence[float], default (1,0,0)
            Axis about which `rotation_angle` applies (length 3).
        spatial_scale : Sequence[float], default (1,1,1)
            Spatial scaling factors (length 3). Does not alter poly_coeff; metadata only.
        trajectory_type : str, default "PolynomialTrajectory"
            Type tag.
        rotation_angle : float, default 0.0
            Rotation (radians) about `rotation_axis`.

        Returns
        -------
        data_dict : Dict[str, Any]
            Dictionary containing exactly these keys:
                base_time, rotation_axis, poly_coeff, spatial_scale,
                trajectory_id, trajectory_type, time_scale, rotation_angle
        json_pretty : str
            Pretty-formatted JSON (indent=4).

        Raises
        ------
        ValueError
            If shapes / lengths are inconsistent or numeric constraints violated.
        """
        # ---- Basic validation ----
        if base_time <= 0:
            raise ValueError(f"base_time must be > 0 (got {base_time}).")
        if time_scale <= 0:
            raise ValueError(f"time_scale should be > 0 (got {time_scale}).")

        rot = list(rotation_axis)
        if len(rot) != 3:
            raise ValueError(f"rotation_axis must have length 3 (got {len(rot)}).")

        scale = list(spatial_scale)
        if len(scale) != 3:
            raise ValueError(f"spatial_scale must have length 3 (got {len(scale)}).")
        
        # Reverse each row of poly_coeff to match expected format
        poly_matrix = [list(reversed(row)) for row in poly_coeff]
    
        if len(poly_coeff) != 3:
            raise ValueError(f"poly_coeff must have 3 rows (x,y,z); got {len(poly_coeff)}.")

        n_cols = len(poly_matrix[0])
        if n_cols == 0:
            raise ValueError("poly_coeff rows must have at least one coefficient.")
        for i, row in enumerate(poly_matrix[1:], start=1):
            if len(row) != n_cols:
                raise ValueError(
                    f"All poly_coeff rows must have equal length; row 0 has {n_cols}, row {i} has {len(row)}."
                )

        data = {
            "base_time": float(base_time),
            "rotation_axis": rot,
            "poly_coeff": poly_matrix,
            "spatial_scale": scale,
            "trajectory_id": trajectory_id,
            "trajectory_type": trajectory_type,
            "time_scale": float(time_scale),
            "rotation_angle": float(rotation_angle),
            "trajectory_type": "PolynomialTrajectory",
        }

        json_pretty = json.dumps(data, indent=4)
        return data, json_pretty

    def build_polynomial_trajectory_json(self,trajectory_id: str) -> Tuple[Dict[str, Any], str]:
        """
        PUBLIC: Build a polynomial trajectory JSON using fixed defaults, given only a trajectory_id.

        Parameters
        ----------
        trajectory_id : str
            Identifier / path used as the 'trajectory_id' field.

        Returns
        -------
        data_dict : Dict[str, Any]
        json_pretty : str
            Pretty-formatted JSON string.
        """

        return self._build_polynomial_trajectory_json(
            poly_coeff=self.poly_coeff,
            time_scale=self.time_scale,
            trajectory_id=trajectory_id,
            rotation_axis=self.rotation_axis,
            spatial_scale=self.spatial_scale,
            trajectory_type="PolynomialTrajectory",
            rotation_angle=self.rotation_angle,
        )

    def _convert_gps_to_relative(self):
        if not self.raw_waypoints:
            return None
        # Convert GPS coordinates to relative coordinates using the home position
        return np.asarray([
            gps_to_relative_3d(*self.home, lat, lon, alt)
            for lat, lon, alt in self.raw_waypoints
        ])

    def _convert_cartesian_to_relative(self):
        if not self.raw_waypoints:
            return None
        # Convert the waypoints to relative coordinates
        relative_points = np.asarray(self.raw_waypoints) - np.asarray(self.home)
        relative_points = np.vstack((np.zeros((1, 3)), relative_points))
        return relative_points

    def _convert_yaw_to_relative(self):
        if not self.yaws_deg:
            return None
        # Ensure home_yaw is in radians and wrapped to [-pi, pi]
        self.home_yaw = wrap_to_pi(self.home_yaw)
        # Convert yaw angles to relative angles based on the home yaw
        relative_yaws = wrap_to_pi(wrap_to_pi(deg2rad(np.asarray(self.yaws_deg))) - np.asarray(self.home_yaw))
        relative_yaws = np.append(0, relative_yaws)
        return relative_yaws

    def _canonical_timescale_coeffs(self, m: int) -> np.ndarray:
        """
        Generate canonical time-scaling coefficients for polynomial s(u) on [0,1]
        with derivatives s^{(r)}(0)=s^{(r)}(1)=0 for r=1..m, s(0)=0, s(1)=1.
        Minimal degree: n = 2*m + 1.

        Parameters
        ----------
        m : int
            Highest derivative order (>=1) made zero at both endpoints.

        Returns
        -------
        coeffs : np.ndarray
            Array of length n+1 containing coefficients a_0..a_n for s(u)=Σ a_i u^i.
        """
        if m < 1:
            raise ValueError("m must be >= 1")
        n = 2 * m + 1
        coeffs = np.zeros((3, n+1), dtype=float)
        # Closed-form coefficients
        from math import comb
        for k in range(m + 1):
            coeffs[0, m + 1 + k] = ((-1) ** k) * comb(m + k, k) * comb(2 * m + 1, m - k)
        return coeffs


    def _generate_trajectory(self):
        """
        Generate trajectory.

        Returns
        -------
        ts : np.ndarray | None
        pos, vel, acc : np.ndarray | None
        yaw, yaw_rate : np.ndarray | None
        poly_coeffs : np.ndarray | None
            Canonical coefficients used (m=4 → degree 9) in 2-point case.
        time_scale : float
            Segment total time (0.0 if degenerate / no movement).
        """
        ts = pos = vel = acc = yaw = yaw_rate = None
        poly_coeffs = None
        time_scale = 0.0

        if self.relative_points is None:
            return ts, pos, vel, acc, yaw, yaw_rate, poly_coeffs, time_scale

        pts = np.asarray(self.relative_points, dtype=float)

        # Enforce first point = origin
        if not np.allclose(pts[0], np.zeros(3)):
            logger.warning(
                "First waypoint is not (0,0,0); inserting origin at the start of the path."
            )
            pts = np.vstack(([0.0, 0.0, 0.0], pts))

        # -----------------------------------------------
        # TWO POINTS → single segment with m=4 canonical
        # -----------------------------------------------
        if len(pts) == 2:
            logger.info(f"pts[0]: {pts[0]}")
            logger.info(f"pts[1]: {pts[1]}")
            dp = pts[1] - pts[0]
            seg_len_scalar = np.linalg.norm(dp)

            # Convert seg_len to a 3-element sequence by repeating the scalar value
            seg_len = [seg_len_scalar, seg_len_scalar, seg_len_scalar]

            # m=4 gives degree 9
            poly_coeffs = self._canonical_timescale_coeffs(m=4)  # length 10

            # Zero displacement - no meaningful rotation
            rotation_axis = [0.0, 0.0, 1.0]  # arbitrary axis
            rotation_angle = 0.0

            # if seg_len_scalar < _EPS:
            #     logger.warning(
            #         "Trajectory start and end coincide; returning static zero trajectory."
            #     )
            #     ts = np.array([0.0])
            #     pos = np.zeros((1, 3))
            #     vel = np.zeros_like(pos)
            #     acc = np.zeros_like(pos)
            #     time_scale = 0.0
            #     t_vals = np.array([0.0, 0.0])
            #     # Keep default rotation_axis and rotation_angle for zero displacement
            if seg_len_scalar < _EPS:
                logger.warning("Trajectory start and end coincide; returning static zero trajectory.")
                # Fix: Use different time values to avoid CubicSpline error
                t_vals = np.array([0.0, 0.01])  # Small non-zero difference instead of [0.0, 0.0]
                ts = np.array([0.0])
                pos = np.zeros((1, 3))
                vel = np.zeros_like(pos)
                acc = np.zeros_like(pos)
                yaw = np.zeros(1)
                yaw_rate = np.zeros_like(yaw)
                time_scale = 0.01
                return ts, pos, vel, acc, yaw, yaw_rate, poly_coeffs, time_scale, seg_len, rotation_axis, rotation_angle
            else:
                # Calculate the time scale
                T = seg_len_scalar / self.speed
                time_scale = T
                ts = np.arange(0.0, T + 1e-12, self.dt)
                u = ts / T
                t_vals = np.array([0.0, T])

                # Use positive X-axis as reference direction (you can change this)
                reference_dir = np.array([1.0, 0.0, 0.0])
                
                # Normalize dp to get unit direction vector
                dp_normalized = dp / seg_len_scalar
                
                # Compute rotation axis using cross product
                rotation_axis_vec = np.cross(reference_dir, dp_normalized)
                axis_magnitude = np.linalg.norm(rotation_axis_vec)
                
                if axis_magnitude > _EPS:
                    # Normalize the rotation axis and convert to list
                    rotation_axis = (rotation_axis_vec / axis_magnitude).tolist()
                    
                    # Compute rotation angle using dot product
                    cos_angle = np.clip(np.dot(reference_dir, dp_normalized), -1.0, 1.0)
                    rotation_angle = np.arccos(cos_angle)
                else:
                    # Vectors are parallel or anti-parallel
                    if np.dot(reference_dir, dp_normalized) > 0:
                        # Same direction - no rotation needed
                        rotation_axis = [0.0, 0.0, 1.0]  # arbitrary axis
                        rotation_angle = 0.0
                    else:
                        # Opposite direction - 180° rotation around any perpendicular axis
                        # Choose Z-axis if reference is along X-axis
                        rotation_axis = [0.0, 0.0, 1.0]
                        rotation_angle = np.pi


            # Yaw handling
            if self.relative_yaws is not None:
                yaw_spline = CubicSpline(t_vals, self.relative_yaws, bc_type="clamped")
                yaw_interp = yaw_spline(ts)
                if self.yaw_mode == "lock":
                    yaw = yaw_interp
                elif self.yaw_mode == "follow":
                    vx, vy = vel[:, 0], vel[:, 1]
                    follow_yaw = np.arctan2(vy, vx)
                    yaw = follow_yaw + yaw_interp
                else:
                    raise ValueError("yaw_mode must be 'follow' or 'lock'")
                yaw_rate = np.gradient(yaw, self.dt)

        # ------------------------------------------------------
        # THREE OR MORE POINTS → cubic splines (then raise error)
        # ------------------------------------------------------
        else:
            seg_lengths = np.linalg.norm(np.diff(pts, axis=0), axis=1)
            t_vals = np.concatenate(([0.0], np.cumsum(seg_lengths))) / self.speed
            T = t_vals[-1]
            time_scale = T

            if T < _EPS:
                t_vals[:] = 0.0
                logger.warning(
                    "Total path length is zero; returning static zero trajectory."
                )
                ts = np.array([0.0])
                pos = np.zeros((1, 3))
                vel = np.zeros_like(pos)
                acc = np.zeros_like(pos)
            else:
                ts = np.arange(0.0, T + 1e-12, self.dt)
                logger.warning(
                    "Using CubicSpline (multi-waypoint). This feature is currently marked as NOT IMPLEMENTED."
                )
                cs_x = CubicSpline(t_vals, pts[:, 0], bc_type="clamped")
                cs_y = CubicSpline(t_vals, pts[:, 1], bc_type="clamped")
                cs_z = CubicSpline(t_vals, pts[:, 2], bc_type="clamped")

                pos = np.column_stack([cs_x(ts), cs_y(ts), cs_z(ts)])
                vel = np.column_stack([cs_x(ts, 1), cs_y(ts, 1), cs_z(ts, 1)])
                acc = np.column_stack([cs_x(ts, 2), cs_y(ts, 2), cs_z(ts, 2)])

                if self.relative_yaws is not None:
                    yaw_spline = CubicSpline(t_vals, self.relative_yaws, bc_type="clamped")
                    yaw = yaw_spline(ts)
                    yaw_rate = np.gradient(yaw, self.dt)

            # Explicitly raise after computing (per your request).
            raise NotImplementedError(
                "Multi-waypoint (>=3) cubic spline trajectory is computed but flagged as not implemented."
            )
        # Print poly_coeffs and time_scale for debugging
        print(f"Generated polynomial coefficients: {poly_coeffs}")
        print(f"Time scale for trajectory: {time_scale}")
        print(f"Segment length (3-element): {seg_len}")
        print(f"Rotation axis (3-element): {rotation_axis}")
        return ts, pos, vel, acc, yaw, yaw_rate, poly_coeffs, time_scale, seg_len, rotation_axis, rotation_angle


    def get_setpoints(self):
        return self.ts, self.pos, self.vel, self.acc, self.yaw, self.yaw_rate
    
    def get_relative_coordinates(self):
        return self.relative_points
    
    def get_waypoints(self):
        return self.raw_waypoints
    
    def animate_projections_with_velocity(self):
        xs, ys, zs = self.pos[:, 0], self.pos[:, 1], self.pos[:, 2]
        vxs, vys, vzs = self.vel[:, 0], self.vel[:, 1], self.vel[:, 2]
        fig = plt.figure(figsize=(15, 10))
        grid = plt.GridSpec(2, 3, hspace=0.4, wspace=0.3)
        # Projection subplots
        axes_proj = [fig.add_subplot(grid[0, i]) for i in range(3)]
        views = [("XY View", xs, ys, "X [m]", "Y [m]"),
                ("XZ View", xs, zs, "X [m]", "Z [m]"),
                ("YZ View", ys, zs, "Y [m]", "Z [m]")]
        # Velocity subplots
        axes_vel = [fig.add_subplot(grid[1, i]) for i in range(3)]
        vlabels = [("vx", vxs), ("vy", vys), ("vz", vzs)]
        # Plot trajectory projections
        lines_proj, dots_proj = [], []
        for ax, (title, x_data, y_data, xlabel, ylabel) in zip(axes_proj, views):
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.plot(x_data, y_data, 'gray', lw=0.5, label='Trajectory')
            # Add waypoint scatter
            if self.relative_points is not None:
                wp_x, wp_y, wp_z = self.relative_points[:, 0], self.relative_points[:, 1], self.relative_points[:, 2]
                if xlabel == "X [m]" and ylabel == "Y [m]":
                    ax.scatter(wp_x, wp_y, c='k', marker='x', s=60, label='Waypoints')
                elif xlabel == "X [m]" and ylabel == "Z [m]":
                    ax.scatter(wp_x, wp_z, c='k', marker='x', s=60, label='Waypoints')
                elif xlabel == "Y [m]" and ylabel == "Z [m]":
                    ax.scatter(wp_y, wp_z, c='k', marker='x', s=60, label='Waypoints')
            line, = ax.plot([], [], 'b-', lw=2)
            dot, = ax.plot([], [], 'ro')
            ax.grid(True)
            ax.axis('equal')
            ax.legend()
            lines_proj.append(line)
            dots_proj.append(dot)
        # Plot velocity components
        lines_vel, dots_vel = [], []
        for ax, (label, v_data) in zip(axes_vel, vlabels):
            ax.set_title(f"{label.upper()} Velocity")
            ax.set_xlabel("Time [s]")
            ax.set_ylabel("Velocity [m/s]")
            ax.plot(self.ts, v_data, 'gray', lw=0.5, label=f'{label}(t)')
            line, = ax.plot([], [], 'b-', lw=2)
            dot, = ax.plot([], [], 'ro')
            ax.set_xlim([self.ts[0], self.ts[-1]])
            ax.set_ylim([1.1 * np.min(v_data), 1.1 * np.max(v_data)])
            ax.grid(True)
            ax.legend()
            lines_vel.append(line)
            dots_vel.append(dot)
        # --- Animation update function ---
        def update(frame):
            # Update trajectory plots
            for i, (line, dot, (title, x_data, y_data, _, _)) in enumerate(zip(lines_proj, dots_proj, views)):
                line.set_data(x_data[:frame+1], y_data[:frame+1])
                dot.set_data([x_data[frame]], [y_data[frame]])
            # Update velocity plots
            for i, (line, dot, (_, v_data)) in enumerate(zip(lines_vel, dots_vel, vlabels)):
                line.set_data(self.ts[:frame+1], v_data[:frame+1])
                dot.set_data([self.ts[frame]], [v_data[frame]])
            return lines_proj + dots_proj + lines_vel + dots_vel
        ani = FuncAnimation(fig, update, frames=len(self.ts), interval=100, blit=True)
        plt.show()


# class TrajectorySampler:
#     def __init__(self, trajectory: WaypointTrajectory):
#         self.trajectory = trajectory
#         self.ts, self.pos, self.vel, self.acc, self.yaw, self.yaw_rate = trajectory.get_setpoints()
#         self.current_index_pos = 0
#         self.current_index_yaw = 0
#         # Spike checks
#         self.prev_pos = None                     # last position we served
#         self.step_norm_max = 0.1                # metres; change to suit

        
#     def sample_pos(self):
#         pos = 0
#         vel = 0
#         acc = 0
#         if self.current_index_pos < len(self.ts):
#             t = self.ts[self.current_index_pos]
#             if self.trajectory.relative_points is not None:
#                 pos = self.pos[self.current_index_pos]
#                 vel = self.vel[self.current_index_pos]
#                 acc = self.acc[self.current_index_pos]
#                 # ── spike / jump check ──────────────────────────
#                 if self.prev_pos is not None:
#                     step = np.linalg.norm(pos - self.prev_pos)
#                     if step > self.step_norm_max:
#                         logger.warning(
#                             "Large position jump detected: %.3f m (limit %.3f m) at index %d",
#                             step, self.step_norm_max, self.current_index_pos
#                         )
#                 self.prev_pos = pos  # update for next iteration
#                 # ──────────────────────────────────────────────────────

#             self.current_index_pos += 1
#             return t, pos, vel, acc
#         else:
#             raise StopIteration("End of trajectory reached for position.")
        
#     def sample_yaw(self):
#         yaw = 0
#         yaw_rate = 0
#         if self.current_index_yaw < len(self.ts):
#             t = self.ts[self.current_index_yaw]
#             if self.trajectory.relative_yaws is not None:
#                 yaw = self.yaw[self.current_index_yaw]
#                 yaw_rate = self.yaw_rate[self.current_index_yaw]
#             self.current_index_yaw += 1
#             return t, yaw, yaw_rate
#         else:
#             raise StopIteration("End of trajectory reached for yaw.")