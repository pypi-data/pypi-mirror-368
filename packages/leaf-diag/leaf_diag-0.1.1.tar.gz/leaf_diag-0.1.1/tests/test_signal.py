from math import sin
import os
import pytest
import numpy as np
from leaf_diag.data_sync import SignalSynchronizer
from leaf_diag.data_loader import OrientationSignal, load_rosbag, load_ulg
from leaf_diag.data_transform import px4_rpy_to_droneleaf_rpy
from leaf_diag.data_loader import (
    OrientationSignal,
    UlogOrientationSignal,
    CartesianSignal,
    UlogPositionSignal,
    BaseSignal
)
from leaf_diag.ulog_export import UlogExporterOutdoor, UlogExporterIndoor
import pandas as pd

import matplotlib.pyplot as plt


@pytest.fixture
def bag_data():
    data_dir = "data_test"
    filename = "2025-03-06-16-39-55.bag"
    path = os.path.join(data_dir, filename)
    topic_name = "/dynamo_db/actu_sys/arm_commander/io_cmds_to_px4"
    return {
        "path": path,
        "topic_name": topic_name
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

def test_base_signal():
    # Test BaseSignal functionality
    data = np.array([[1, 2], [3, 4], [5, 6]])
    timestamps = np.array([0.0, 0.5, 1.0])
    signal = BaseSignal(data, timestamps)
    
    # Test sampling frequency calculation
    assert np.isclose(signal.sampling_freq, 2.0)
    
    # Test time reset
    signal.reset_time()
    assert np.isclose(signal.timestamps[0], 0.0)
    
    # Test setting start time
    signal.set_start_time(0.5)
    assert np.isclose(signal.timestamps[0], -0.5)
    
    # Test signal slice
    np.testing.assert_array_equal(signal.get_signal_slice(1), np.array([2, 4, 6]))

def test_ros_orientation_signal(bag_data):
    with load_rosbag(bag_data["path"]) as bag:
        ori_signal = OrientationSignal(bag, "/dynamo_db/estimator/ori")
        assert ori_signal.dimension == 3
        assert ori_signal.data_keys == ["roll", "pitch", "yaw"]
        assert ori_signal.data.shape[1] == 3

def test_ulog_orientation_signal(ulg_data):
    with load_ulg(ulg_data["path"]) as ulog:
        ori_signal = UlogOrientationSignal(ulog, "t_vehicle_attitude_0")
        assert ori_signal.dimension == 3
        assert ori_signal.data_keys == ["roll", "pitch", "yaw"]
        assert ori_signal.data.shape[1] == 3

def test_ulog_position_signal(ulg_data):
    with load_ulg(ulg_data["path"]) as ulog:
        pos_signal = UlogPositionSignal(ulog, "t_vehicle_local_position_0")
        assert pos_signal.dimension == 3
        assert pos_signal.data.shape[1] == 3
        
        # Test that PX4 coordinates were transformed to droneleaf coordinates
        # In the transform, x_px4 becomes y_droneleaf, y_px4 becomes x_droneleaf, and z_px4 becomes -z_droneleaf
        
        # Extract original PX4 coordinates from ulog (this is a simplified test)
        orig_x = ulog["t_vehicle_local_position_0"]["f_x"].to_numpy()
        orig_y = ulog["t_vehicle_local_position_0"]["f_y"].to_numpy()
        orig_z = ulog["t_vehicle_local_position_0"]["f_z"].to_numpy()
        
        # Check transformation: y_droneleaf should be x_px4, etc.
        assert np.allclose(pos_signal.data[:, 0], orig_y[:len(pos_signal.data)])
        assert np.allclose(pos_signal.data[:, 1], orig_x[:len(pos_signal.data)])
        assert np.allclose(pos_signal.data[:, 2], -orig_z[:len(pos_signal.data)])

@pytest.mark.parametrize("flight_type,data,single_instance,write_csv,sync_key", [
    (
        "outdoor", 
        {
            "bag_data": "data_test/2025-03-06-16-39-55.bag", 
            "ulg_data": "data_test/log_264_2025-3-5-12-17-16.ulg", 
            "sensor_config" : {"gps" : True, "optical_flow" : True}
        }, 
        False, 
        False,
        "acceleration"
    ),
    (
        "outdoor", 
        {
            "bag_data": None, 
            "ulg_data": "data_test/log_264_2025-3-5-12-17-16.ulg", 
            "sensor_config" : {"gps" : True, "optical_flow" : True}
        }, 
        False, 
        False,
        "acceleration_raw"
    ),
    (
        "outdoor", 
        {
            "bag_data": None, 
            "ulg_data": "data_test/log_264_2025-3-5-12-17-16.ulg", 
            "sensor_config" : {"gps" : False, "optical_flow" : False}
        }, 
        False, 
        False,
        "acceleration_raw"
    ),
    (
        "indoor", 
        {
            "bag_data": "data_test/full_flight.bag", 
            "ulg_data": "data_test/log_137_2025-7-20-14-05-32.ulg"
        }, 
        True, 
        False,
       "acceleration"
    ),
    (
        "indoor", 
        {
            "bag_data": None, 
            "ulg_data": "data_test/log_137_2025-7-20-14-05-32.ulg"
        }, 
        True, 
        False,
       "acceleration"
    ),
    (
        "indoor", 
        {
            "bag_data": "data_test/start_to_midflight.bag", 
            "ulg_data": "data_test/log_139_2025-7-20-14-08-00.ulg"
        }, 
        True, 
        False,
       "acceleration"
    ),
    (
        "indoor", 
        {
            "bag_data": "data_test/midflight_to_land.bag", 
            "ulg_data": "data_test/log_140_2025-7-20-14-08-40.ulg"
        }, 
        True, 
        False,
       "acceleration"
    ),
    (
        "indoor", 
        {
            "bag_data": "data_test/midflight_only.bag", 
            "ulg_data": "data_test/log_141_2025-7-20-14-09-24.ulg"
        }, 
        True, 
        False,
       "acceleration"
    ),
    (
        "outdoor", 
        {
            "bag_data": "data_test/log_25_full-flight.bag", 
            "ulg_data": "data_test/log_25_2025-7-13-16-03-18.ulg", 
            "sensor_config" : {"gps" : True, "optical_flow" : False}
        }, 
        True, 
        False,
        "acceleration_raw"
    ),
    (
        "outdoor", 
        {
            "bag_data": "data_test/log_26_start-to-mid-flight.bag", 
            "ulg_data": "data_test/log_26_2025-7-13-16-04-34.ulg", 
            "sensor_config" : {"gps" : True, "optical_flow" : False}
        }, 
        True, 
        False,
        "acceleration_raw"
    ),
    (
        "outdoor", 
        {
            "bag_data": "data_test/log_27_mid-flight-to-land.bag", 
            "ulg_data": "data_test/log_27_2025-7-13-16-06-36.ulg", 
            "sensor_config" : {"gps" : True, "optical_flow" : False}
        }, 
        True, 
        False,
        "acceleration_raw"
    ),
    (
        "outdoor", 
        {
            "bag_data": "data_test/log_28_mid-flight-only.bag", 
            "ulg_data": "data_test/log_28_2025-7-13-16-07-54.ulg", 
            "sensor_config" : {"gps" : True, "optical_flow" : False}
        }, 
        True, 
        False,
        "acceleration_raw"
    ),
    (
        "outdoor", 
        {
            "bag_data": "data_test/log_29_mid-flight-to-land.bag", 
            "ulg_data": "data_test/log_29_2025-7-13-16-11-20.ulg", 
            "sensor_config" : {"gps" : True, "optical_flow" : False}
        }, 
        True, 
        False,
        "acceleration_raw"
    ),
    (
        "outdoor", 
        {
            "bag_data": "data_test/log_30_mid-flight-only.bag", 
            "ulg_data": "data_test/log_30_2025-7-13-16-14-22.ulg", 
            "sensor_config" : {"gps" : True, "optical_flow" : False}
        }, 
        True, 
        False,
        "acceleration_raw"
    ),
    (
        "outdoor", 
        {
            "bag_data": "data_test/log_31_full-flight.bag", 
            "ulg_data": "data_test/log_31_2025-7-13-16-23-18.ulg", 
            "sensor_config" : {"gps" : True, "optical_flow" : False}
        }, 
        True, 
        False,
        "acceleration_raw"
    ),
    (
        "outdoor", 
        {
            "bag_data": "data_test/log_32_mid-flight-to-land.bag", 
            "ulg_data": "data_test/log_32_2025-7-13-16-24-14.ulg", 
            "sensor_config" : {"gps" : True, "optical_flow" : False}
        }, 
        True, 
        False,
        "acceleration_raw"
    ),
    (
        "outdoor", 
        {
            "bag_data": "data_test/log_32_start-to-mid-flight.bag", 
            "ulg_data": "data_test/log_32_2025-7-13-16-24-14.ulg", 
            "sensor_config" : {"gps" : True, "optical_flow" : False}
        }, 
        True, 
        False,
        "acceleration_raw"
    ),
    (
        "outdoor", 
        {
            "bag_data": "data_test/log_33_mid-flight-to-land.bag", 
            "ulg_data": "data_test/log_33_2025-7-13-16-26-52.ulg", 
            "sensor_config" : {"gps" : True, "optical_flow" : False}
        }, 
        True, 
        False,
        "acceleration_raw"
    ),
], ids=[
    "outdoor_multi", 
    "outdoor_multi_no_rosbag", 
    "outdoor_multi_no_rosbag_no_sensor", 
    "indoor_flight_01", 
    "indoor_flight_01_no_rosbag",
    "indoor_flight_02", 
    "indoor_flight_03",
    "indoor_flight_04", 
    "outdoor_flight_03",
    "outdoor_flight_04",
    "outdoor_flight_05",
    "outdoor_flight_06",
    "outdoor_flight_07",
    "outdoor_flight_08",
    "outdoor_flight_09",
    "outdoor_flight_10a",
    "outdoor_flight_10b",
    "outdoor_flight_11",
])
def test_ulog_exporter(flight_type, data, single_instance, write_csv, sync_key, request):
    bag_data = data["bag_data"]
    ulg_data = data["ulg_data"]
    # get test id
    test_id = request.node.name
    # extract the test id between brackets 'test_ulog_exporter[outdoor_flight_03]'
    test_output_str = test_id.split("[")[1].split("]")[0]
    print(f"Running test: {test_output_str}")

    # Create a temporary output directory
    output_dir = os.path.join("data_test", f"export_test_{test_output_str}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the exporter based on flight type
    output_bag_name = "test_combined.bag"
    if flight_type == "outdoor":
        exporter = UlogExporterOutdoor(
            rosbag_path=bag_data,
            ulog_path=ulg_data,
            output_dir=output_dir,
            filename=output_bag_name,
            single_instance=single_instance,
            sensor_config=data.get("sensor_config", None)
        )
    else:  # indoor
        exporter = UlogExporterIndoor(
            rosbag_path=bag_data,
            ulog_path=ulg_data,
            output_dir=output_dir,
            filename=output_bag_name,
            single_instance=single_instance
        )
    
    # Test data extraction
    exporter.extract_all_data(sync_key=sync_key, plot_correlation=True)
    
    # verify overlap in synchronizers > 20%
    for topic_name, synchronizer in exporter.synchronizers.items():
        if synchronizer.best_overlap is not None:
            assert synchronizer.best_overlap > 0.5, f"Overlap for {topic_name} is below threshold: {synchronizer.best_overlap}"

    # Verify signals were loaded
    assert exporter.ulog_signals["position"]["signal"] is not None
    assert exporter.ulog_derived_signals["orientation"]["signal"] is not None
    if bag_data:
        assert exporter.ros_signals["position"]["signal"] is not None
        assert exporter.ros_signals["orientation"]["signal"] is not None
        
        # Test CSV export
    csv_output_dir = os.path.join(output_dir, "csv")
    df_dict = exporter.export_df(csv_output_dir, write_csv=write_csv)
    
    # Check if files were created
    assert "px4_position" in df_dict
    assert "px4_orientation" in df_dict
    if write_csv:
        assert os.path.exists(os.path.join(csv_output_dir, "px4_position.csv"))
        assert os.path.exists(os.path.join(csv_output_dir, "px4_orientation.csv"))

    if bag_data:
        assert "ros_position" in df_dict
        assert "ros_orientation" in df_dict
        if write_csv:
            assert os.path.exists(os.path.join(csv_output_dir, "ros_position.csv"))
            assert os.path.exists(os.path.join(csv_output_dir, "ros_orientation.csv"))
            
    # Test orientation angles equivalence after transformation
    px4_ori = exporter.ulog_derived_signals["orientation"]["signal"]
    ros_ori = exporter.ros_signals["orientation"]["signal"] if bag_data else None
    
    # Plot to visually verify the synchronization
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for i, label in enumerate(["Roll", "Pitch", "Yaw"]):
        axes[i].plot(px4_ori.timestamps, px4_ori.data[:, i], 'r-', label=f"PX4 {label}")
        if ros_ori is not None:
            axes[i].plot(ros_ori.timestamps, ros_ori.data[:, i], 'b-', label=f"ROS {label}")
        axes[i].set_ylabel(f"{label} (rad)")
        axes[i].legend()
    
    axes[2].set_xlabel("Time (s)")
    plt.savefig(os.path.join(output_dir, "orientation_comparison.png"))
    plt.close()
    
    # Test position comparison
    px4_pos = exporter.ulog_signals["position"]["signal"]
    ros_pos = exporter.ros_signals["position"]["signal"] if bag_data else None
    
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for i, label in enumerate(["X", "Y", "Z"]):
        axes[i].plot(px4_pos.timestamps, px4_pos.data[:, i], 'r-', label=f"PX4 {label}")
        if ros_pos is not None:
            axes[i].plot(ros_pos.timestamps, ros_pos.data[:, i], 'b-', label=f"ROS {label}")
        axes[i].set_ylabel(f"{label} (m)")
        axes[i].legend()
    
    axes[2].set_xlabel("Time (s)")
    plt.savefig(os.path.join(output_dir, "position_comparison.png"))
    plt.close()
    
    # Check error between ROS and PX4 signals (already synchronized in UlogExporter)
    px4_ori = exporter.ulog_derived_signals["orientation"]["signal"]
    ros_ori = exporter.ros_signals["orientation"]["signal"] if bag_data else None
    px4_pos = exporter.ulog_signals["position"]["signal"]
    ros_pos = exporter.ros_signals["position"]["signal"] if bag_data else None
    
    # Interpolate to compare at exactly the same timestamps
    # For orientation
    if ros_ori is not None:
        highest_frequency = max(px4_ori.sampling_freq, ros_ori.sampling_freq)
        common_ori_timestamps = np.arange(max(px4_ori.timestamps[0], ros_ori.timestamps[0]),
                                        min(px4_ori.timestamps[-1], ros_ori.timestamps[-1]), 1.0 / highest_frequency)
        px4_ori_interp = np.array([np.interp(common_ori_timestamps, px4_ori.timestamps, px4_ori.data[:, i]) for i in range(3)]).T
        ros_ori_interp = np.array([np.interp(common_ori_timestamps, ros_ori.timestamps, ros_ori.data[:, i]) for i in range(3)]).T
        
        # For position
        highest_frequency = max(px4_pos.sampling_freq, ros_pos.sampling_freq)
        common_pos_timestamps = np.arange(max(px4_pos.timestamps[0], ros_pos.timestamps[0]),
                                        min(px4_pos.timestamps[-1], ros_pos.timestamps[-1]), 1.0 / highest_frequency)
        px4_pos_interp = np.array([np.interp(common_pos_timestamps, px4_pos.timestamps, px4_pos.data[:, i]) for i in range(3)]).T
        ros_pos_interp = np.array([np.interp(common_pos_timestamps, ros_pos.timestamps, ros_pos.data[:, i]) for i in range(3)]).T
        
        # Calculate RMSE for orientation (in radians)
        ori_rmse = np.nanmean(np.sqrt(np.square(px4_ori_interp - ros_ori_interp)), axis=0)
        # Calculate RMSE for position (in meters)
        pos_rmse = np.nanmean(np.sqrt(np.square(px4_pos_interp - ros_pos_interp)), axis=0)
        
        # Define acceptable thresholds
        ORI_THRESHOLD = 0.6  # radians (approximately 34 degrees)
        POS_THRESHOLD = 0.5   # meters
        
        # Assert that errors are within acceptable thresholds
        for i, label in enumerate(["Roll", "Pitch", "Yaw"]):
            assert ori_rmse[i] < ORI_THRESHOLD, f"{label} RMSE ({ori_rmse[i]}) exceeds threshold ({ORI_THRESHOLD})"
        
        for i, label in enumerate(["X", "Y", "Z"]):
            assert pos_rmse[i] < POS_THRESHOLD, f"{label} RMSE ({pos_rmse[i]}) exceeds threshold ({POS_THRESHOLD})"
    
    # Test the combined bag creation
    bag_bytes = exporter.create_combined_ulog(output_dir)
    assert os.path.exists(os.path.join(output_dir, output_bag_name))

    # check that the bag contains the following signals
    with load_rosbag(os.path.join(output_dir, output_bag_name)) as output_bag:
        if bag_data:
            ros_messages = [
                "/ros/acceleration",
                "/ros/position",
                "/ros/velocity",
                "/ros/orientation",
                "/ros/orientation_rate"
            ]
            for message in ros_messages:
                df_data = output_bag.message_by_topic_memory(message)
                assert len(df_data) > 0     

        px4_messages = ["/px4/" + value["path"] for value in exporter.ulog_signals.values() if value["signal"] is not None] + \
            ["/px4/" + value["path"] for value in exporter.ulog_derived_signals.values() if value["signal"] is not None] + \
            ["/px4/" + value["path"] + "/" + str(instance_id) for value in exporter.ulog_derived_signals_multi.values() for instance_id in range(value["num_instances"])]

        for message in px4_messages:
            df_data = output_bag.message_by_topic_memory(message)
            assert len(df_data) > 0

    # Test the plotting facility
    plot_dir = "plots"
    exporter.create_charts(plot_dir)
    
