import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
	pkg_name = 'robot_slam_toolbox'
	urdf_name = 'robot_descript.urdf'
	world_name = 'room.sdf'
	
	use_sim_time = LaunchConfiguration('use_sim_time', default='true')
	pkg_share = get_package_share_directory(pkg_name)
	ld = LaunchDescription()
	
	urdf_path = os.path.join(pkg_share, 'urdf/'+urdf_name)
	world_path = os.path.join(pkg_share, 'world/'+world_name)
	
	gazebo_node = ExecuteProcess(
		cmd = f'gazebo {world_path} -s libgazebo_ros_init.so -s libgazebo_ros_factory.so'.split(' '),
		output = 'screen'
	)
	
	spawn_entity_node = Node(
		package = 'gazebo_ros',
		executable = 'spawn_entity.py',
		arguments = ['-entity', 'robot', '-file', urdf_path],
	)
	
	robot_state_publisher_node = Node(
		package = 'robot_state_publisher',
		executable = 'robot_state_publisher',
		arguments = [urdf_path],
		parameters = [{'use_sim_time': use_sim_time}]
	)
		
	ld.add_action(gazebo_node)
	ld.add_action(spawn_entity_node)
	ld.add_action(robot_state_publisher_node)
	
	slam_toolbox_share = get_package_share_directory('slam_toolbox')
	slam_toolbox_launch_path = os.path.join(slam_toolbox_share, 'launch/online_async_launch.py')
	slam_config_path = os.path.join(pkg_share, 'config/slam_config.yaml')
	rviz_config_path = os.path.join(pkg_share, 'rviz/slam.rviz')
	
	slam_launch = IncludeLaunchDescription(
		PythonLaunchDescriptionSource([slam_toolbox_launch_path]),
		launch_arguments = {
			'use_sim_time': use_sim_time,
			'slam_params_file': slam_config_path
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
	
	ld.add_action(slam_launch)
	ld.add_action(rviz_node)
	
	return ld
