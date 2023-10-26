import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
	pkg_name = 'pibot_rviz'
	urdf_name = 'robot.urdf'
	
	pkg_share = get_package_share_directory(pkg_name)
	ld = LaunchDescription()
	
	urdf_path = os.path.join(pkg_share, 'urdf/'+urdf_name)
	
	robot_state_publisher_node = Node(
		package = 'robot_state_publisher',
		executable = 'robot_state_publisher',
		arguments = [urdf_path]
	)
	
	joint_state_publisher_node = Node(
		package = 'joint_state_publisher',
		executable = 'joint_state_publisher',
		name = 'joint_state_publisher',
		arguments = [urdf_path]
	)
	
	odom_publisher_node = Node(
		package = pkg_name,
		executable = 'odom_footprint_tf'
	)
	
	ld.add_action(robot_state_publisher_node)
	ld.add_action(joint_state_publisher_node)
	ld.add_action(odom_publisher_node)
	
	rviz_config_path = os.path.join(pkg_share, 'rviz/default.rviz')
		
	rviz_node = Node(
		package = 'rviz2',
		executable = 'rviz2',
		name = 'rviz2',
		arguments = f'-d {rviz_config_path}'.split(' '),
		output = 'screen'
	)
	
	ld.add_action(rviz_node)
	
	return ld
