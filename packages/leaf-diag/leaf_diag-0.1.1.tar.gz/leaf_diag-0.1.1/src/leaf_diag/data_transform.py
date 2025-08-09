from typing import Tuple
from scipy.spatial.transform import Rotation as R
import numpy as np
import math

def px4_rpy_to_droneleaf_rpy(rpy_px4: np.ndarray, offset=90) -> np.ndarray:
    """
    convert RPY angles in PX4 frame to RPY angles in droneleaf frame
    roll -> roll
    pitch -> -pitch
    yaw -> -yaw
    """
    degrees_yaw = np.degrees(-rpy_px4[:,2] + math.radians(offset))
    wrapped_yaw = (degrees_yaw + 180) % 360 - 180
    rpy_dl = np.column_stack((rpy_px4[:,0], -rpy_px4[:,1], np.radians(wrapped_yaw)))
    return rpy_dl

def quat_to_euler(q: np.ndarray) -> np.ndarray:
    """
    Convert a quaternion [x, y, z, w] to Euler angles (roll, pitch, yaw) in radians.
    """
    r = R.from_quat(q)
    return r.as_euler('xyz', degrees=False)

def get_rotations_from_attitude(q0: float, q1: float, q2: float, q3: float) -> Tuple[R, R]:
    """
    Compute Rotation objects for (NED->body) and (body->NED).
    
    Returns:
        (rot_ned_to_body, rot_body_to_ned)
    """

    # 1) Build the rotation object from the *NED->body* quaternion
    #    SciPy's `from_quat` expects [x, y, z, w].
    rot_ned_to_body = R.from_quat([q1, q2, q3, q0])

    # 2) Invert it to get body->NED
    rot_body_to_ned = rot_ned_to_body.inv()

    return rot_ned_to_body, rot_body_to_ned

def compute_altitude_range(
    R_to_earth: np.ndarray,  # shape (3,3,n)
    state_pos: np.ndarray,   # shape (3,n) in NED
    terrain_vpos: np.ndarray = None,  
    ekf2_of_n_pos_x: float = 0.145,
    ekf2_of_n_pos_y: float = 0.0,
    ekf2_of_n_pos_z: float = -0.02,
    ekf2_imu_pos_x: float = 0.0,
    ekf2_imu_pos_y: float = 0.0,
    ekf2_imu_pos_z: float = 0.0,
    ekf2_rng_gnd_clear: float = 0.1
) -> np.ndarray:
    """
    Calculate the same 'range' used by PX4 EKF for an optical flow sensor,
    following the snippet:
        height_above_gnd_est = max(_terrain_vpos - _state.pos(2) - pos_offset_earth(2),
                                   max(_params.rng_gnd_clearance, 0.01f));
        range = height_above_gnd_est / _R_to_earth(2, 2);
    ...
    """
    n = R_to_earth.shape[2]
    range_to_ground = np.zeros(n)

    # Sensor vs. IMU offsets in body coords
    flow_pos_body = np.array([ekf2_of_n_pos_x, ekf2_of_n_pos_y, ekf2_of_n_pos_z])
    imu_pos_body  = np.array([ekf2_imu_pos_x,  ekf2_imu_pos_y,  ekf2_imu_pos_z])
    pos_offset_body = flow_pos_body - imu_pos_body

    if terrain_vpos is None:
        # trivial fallback: assume terrain is at z=0 + clearance
        terrain_vpos = state_pos[2, :] + ekf2_rng_gnd_clear

    for i in range(n):
        R = R_to_earth[:, :, i]      # 3x3 rotation
        z_ned = state_pos[2, i]      # vehicle z in NED

        pos_offset_earth = R.dot(pos_offset_body)

        raw_height = terrain_vpos[i] - z_ned - pos_offset_earth[2]
        height_above_gnd_est = max(raw_height, max(ekf2_rng_gnd_clear, 0.01))

        den = R[2, 2]
        if abs(den) < 1e-6:
            range_to_ground[i] = np.nan
        else:
            range_to_ground[i] = height_above_gnd_est / den

    return range_to_ground