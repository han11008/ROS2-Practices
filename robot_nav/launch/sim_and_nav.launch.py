import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
	pkg_name = 'robot_nav'
	pkg_share = get_package_share_directory(pkg_name)
	robot_name = 'robot_descript'
	world_name = 'room'
	map_name = 'room'
	
	use_sim_time = LaunchConfiguration('use_sim_time', default='true')
	ld = LaunchDescription()
	
	robot_path = os.path.join(pkg_share, f'urdf/{robot_name}.urdf')
	world_path = os.path.join(pkg_share, f'world/{world_name}.sdf')
	
	gazebo_node = ExecuteProcess(
		cmd = f'gazebo {world_path} -s libgazebo_ros_init.so -s libgazebo_ros_factory.so'.split(' '),
		output = 'screen'
	)
	
	spawn_entity_node = Node(
		package = 'gazebo_ros',
		executable = 'spawn_entity.py',
		arguments = f'-entity robot -file {robot_path}'.split(' ')
	)
	
	robot_state_publisher_node = Node(
		package = 'robot_state_publisher',
		executable = 'robot_state_publisher',
		arguments = [robot_path],
		parameters = [{'use_sim_time': use_sim_time}]
	)
	
	ld.add_action(gazebo_node)
	ld.add_action(spawn_entity_node)
	ld.add_action(robot_state_publisher_node)
	
	map_path = os.path.join(pkg_share, f'map/{map_name}.yaml')
	param_path = os.path.join(pkg_share, 'param/nav2_params.yaml')
	nav2_share_dir = get_package_share_directory('nav2_bringup')
	nav2_launch_path = os.path.join(nav2_share_dir, 'launch/bringup_launch.py')
	rviz_config_path = os.path.join(nav2_share_dir, 'rviz/nav2_default_view.rviz')
	
	nav2_bringup_launch = IncludeLaunchDescription(
		PythonLaunchDescriptionSource([nav2_launch_path]),
		launch_arguments = {
			'map': map_path,
			'use_sim_time': use_sim_time,
			'params_file': param_path
		}.items()
	)
	
	rviz_node = Node(
		package = 'rviz2',
		executable = 'rviz2',
		name = 'rviz2',
		arguments = f'-d {rviz_config_path}'.split(' '),
		parameters = [{'use_sim_time': use_sim_time}],
		output = 'screen'
	)
	
	ld.add_action(nav2_bringup_launch)
	ld.add_action(rviz_node)
	
	return ld
