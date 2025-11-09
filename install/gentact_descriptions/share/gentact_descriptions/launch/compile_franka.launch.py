from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare

import os
import yaml
import xacro

def load_config(config_file_name, context):
    package_share = FindPackageShare('gentact_descriptions').perform(context)
    config_file = os.path.join(package_share, 'config', config_file_name)
    
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    
    return config


def _to_xacro_string(value, default=''):
    if value is None:
        return default
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value)


def _sensor_active(sensor_config):
    active_value = sensor_config.get('active', False)
    if isinstance(active_value, str):
        return active_value.lower() == 'true'
    return bool(active_value)


def build_robot_description(config, context):
    robot_config = config.get('robot', {})
    sensors_config = config.get('sensors', {})

    gentact_descriptions_share = FindPackageShare('gentact_descriptions').perform(context)
    urdf_relative_path = robot_config.get('urdf_file', '')
    if not urdf_relative_path:
        raise ValueError('Robot configuration must define "urdf_file".')

    urdf_path = os.path.join(gentact_descriptions_share, 'robots', urdf_relative_path)

    mappings = {
        'ros2_control': 'true',
        'arm_id': _to_xacro_string(robot_config.get('arm_id', '')),
        'arm_prefix': _to_xacro_string(robot_config.get('arm_prefix', '')),
        'robot_ip': _to_xacro_string(robot_config.get('robot_ip', '')),
        'hand': _to_xacro_string(robot_config.get('load_gripper', 'false'), 'false'),
        'use_fake_hardware': _to_xacro_string(robot_config.get('use_fake_hardware', 'false'), 'false'),
        'fake_sensor_commands': _to_xacro_string(robot_config.get('fake_sensor_commands', 'false'), 'false'),
    }

    skin_arguments = {f'link{i}_skin': '' for i in range(1, 7)}
    for sensor_key, sensor_config in sensors_config.items():
        if sensor_key in skin_arguments and isinstance(sensor_config, dict):
            if _sensor_active(sensor_config):
                xacro_path = sensor_config.get('xacro', '')
                if xacro_path:
                    skin_arguments[sensor_key] = str(xacro_path)

    mappings.update(skin_arguments)

    robot_description = xacro.process_file(urdf_path, mappings=mappings).toprettyxml(indent='  ')

    return robot_description

def launch_setup(context, *args, **kwargs):
    # Get the config file name from launch configuration
    config_file_name = LaunchConfiguration('config').perform(context)
    config = load_config(config_file_name, context)

    robot_description = build_robot_description(config, context)

    # Resolve paths in context
    package_share = FindPackageShare('gentact_descriptions').perform(context)

    # Use source directory instead of install directory
    # Get the source directory by going up from package_share: install/gentact_descriptions/share/gentact_descriptions -> src/gentact_descriptions
    install_dir = os.path.dirname(os.path.dirname(os.path.dirname(package_share)))  # Remove share/gentact_descriptions
    workspace_root = os.path.dirname(install_dir)  # Go up one more level to get workspace root
    src_dir = os.path.join(workspace_root, 'src')
    source_package_dir = os.path.join(src_dir, 'gentact_descriptions')

    output_dir_resolved = os.path.join(source_package_dir, 'urdf', 'compiled')
    output_file_resolved = os.path.join(output_dir_resolved, 'robot.urdf')

    os.makedirs(output_dir_resolved, exist_ok=True)

    with open(output_file_resolved, 'w') as output_file:
        output_file.write(robot_description)

    print(f"Saved compiled URDF to {output_file_resolved}")

    return []

def generate_launch_description():

    # Declare launch argument for config file
    config_file_arg = DeclareLaunchArgument(
        'config',
        default_value='simulation.yaml',
        description='Configuration file to load'
    )
    
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )

    return LaunchDescription([
        config_file_arg,
        use_sim_time_arg,
        OpaqueFunction(function=launch_setup)
    ])
