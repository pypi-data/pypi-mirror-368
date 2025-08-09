import os
import pytest
import numpy as np
from leaf_diag.data_sync import SignalSynchronizer, SignalSynchronizerSingle, SignalSynchronizerMulti
from leaf_diag.data_loader import MotorCommandSignal, OrientationSignal, UlogMotorCommandSignal, load_rosbag, load_ulg
from leaf_diag.data_transform import px4_rpy_to_droneleaf_rpy
from leaf_diag.data_loader import (
    OrientationSignal,
    UlogOrientationSignal,
    CartesianSignal,
    UlogPositionSignal
)
import matplotlib.pyplot as plt


@pytest.fixture
def bag_data():
    data_dir = "data_test"
    filename = "2025-03-06-16-39-55.bag"
    path = os.path.join(data_dir, filename)
    topic_name = "/dynamo_db/actu_sys/arm_commander/io_cmds_to_px4"
    return {
        "path": path,
        "topic_name": topic_name,
        "motor_id": 3
    }

@pytest.fixture
def ulg_data():
    data_dir = "data_test"
    filename = "log_264_2025-3-5-12-17-16.ulg"
    path = os.path.join(data_dir, filename)
    ulog_name = "t_actuator_motors_0"
    motor_id = 3
    expected_offset = 5.796
    return {
        "path": path,
        "ulog_name": ulog_name,
        "motor_id": motor_id,
        "expected_offset": expected_offset
    }

def test_load_rosbag(bag_data):
    bag = load_rosbag(bag_data["path"])
    assert bag is not None

def test_load_ulg(ulg_data):
    ulg = load_ulg(ulg_data["path"])
    assert ulg is not None

def test_compute_best_offset(bag_data, ulg_data):
    sync = SignalSynchronizerSingle(bag_data["path"], ulg_data["path"])
    sync.compute_best_offset(
        ros_signal_class=MotorCommandSignal,
        ulog_signal_class=UlogMotorCommandSignal,
        ros_topic_name=bag_data["topic_name"],
        ulog_msg_key=ulg_data["ulog_name"],
        ros_signal_idx=bag_data["motor_id"],
        ulog_signal_idx=ulg_data["motor_id"]
    )
    assert np.isclose(sync.best_offset, ulg_data["expected_offset"], atol=0.1)

def test_compute_best_offset_all(bag_data, ulg_data):
    sync = SignalSynchronizerSingle(bag_data["path"], ulg_data["path"])
    sync.compute_best_offset(
        ros_signal_class=MotorCommandSignal,
        ulog_signal_class=UlogMotorCommandSignal,
        ros_topic_name=bag_data["topic_name"],
        ulog_msg_key=ulg_data["ulog_name"],
        ros_signal_idx=None,
        ulog_signal_idx=None
    )
    assert np.isclose(sync.best_offset, ulg_data["expected_offset"], atol=0.1)


def test_plot_correlation(bag_data, ulg_data):
    sync = SignalSynchronizerSingle(bag_data["path"], ulg_data["path"])
    sync.compute_best_offset(
        ros_signal_class=MotorCommandSignal,
        ulog_signal_class=UlogMotorCommandSignal,
        ros_topic_name=bag_data["topic_name"],
        ulog_msg_key=ulg_data["ulog_name"],
        ros_signal_idx=bag_data["motor_id"],
        ulog_signal_idx=ulg_data["motor_id"]
    )
    try:
        sync.plot_correlation(filename=os.path.join("data_test", "correlation.png"))
    except Exception as e:
        pytest.fail(f"plot_correlation raised an error: {e}")

def test_plot_signals(bag_data, ulg_data):
    sync = SignalSynchronizerSingle(bag_data["path"], ulg_data["path"])
    sync.compute_best_offset(
        ros_signal_class=MotorCommandSignal,
        ulog_signal_class=UlogMotorCommandSignal,
        ros_topic_name=bag_data["topic_name"],
        ulog_msg_key=ulg_data["ulog_name"],
        ros_signal_idx=bag_data["motor_id"],
        ulog_signal_idx=ulg_data["motor_id"]
    )
    try:
        sync.plot_signals(filename=os.path.join("data_test", "signals.png"))
    except Exception as e:
        pytest.fail(f"plot_signals raised an error: {e}")

def test_get_euler_angles(bag_data, ulg_data):
    sync = SignalSynchronizerSingle(bag_data["path"], ulg_data["path"])
    sync.compute_best_offset(
        ros_signal_class=MotorCommandSignal,
        ulog_signal_class=UlogMotorCommandSignal,
        ros_topic_name=bag_data["topic_name"],
        ulog_msg_key=ulg_data["ulog_name"],
        ros_signal_idx=bag_data["motor_id"],
        ulog_signal_idx=ulg_data["motor_id"]
    )

    with load_rosbag(bag_data["path"]) as bag:
        ros_ori_signal = OrientationSignal(bag, "/dynamo_db/estimator/ori")
        ros_times = ros_ori_signal.timestamps - np.min(ros_ori_signal.timestamps)
        ori = ros_ori_signal.data

    with load_ulg(ulg_data["path"]) as ulog:
        ulog_ori_signal = UlogOrientationSignal(ulog, "t_vehicle_attitude_0")
        ulog_times = ulog_ori_signal.timestamps - np.min(ulog_ori_signal.timestamps)
        RPY_px4 = ulog_ori_signal.data

    assert RPY_px4 is not None
    assert RPY_px4.shape[1] == 3

    # plot the Euler angles
    fig, ax = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
    ax[0].plot(ulog_times + sync.best_offset, RPY_px4[:,0], label="Roll (PX4)")
    ax[0].plot(ros_times, ori[:,0], label="Roll (rosbag)")
    ax[0].set_ylabel("Roll (rad)")
    ax[0].legend()

    ax[1].plot(ulog_times + sync.best_offset, RPY_px4[:,1], label="Pitch (PX4)")
    ax[1].plot(ros_times, ori[:,1], label="Pitch (rosbag)")
    ax[1].set_ylabel("Pitch (rad)")
    ax[1].legend()

    ax[2].plot(ulog_times + sync.best_offset, RPY_px4[:,2], label="Yaw (PX4)")
    ax[2].plot(ros_times, ori[:,2], label="Yaw (rosbag)")
    ax[2].set_ylabel("Yaw (rad)")
    ax[2].legend()

    ax[2].set_xlabel("Time (s)")
    plt.tight_layout()
    fig.savefig(os.path.join("data_test", "angles.png"))