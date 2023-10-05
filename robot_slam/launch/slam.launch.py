import os
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
	pkg_name = 'robot_slam'
	
	pkg_share = FindPackageShare(package=pkg_name).find(pkg_name)
	
	use_sim_time = LaunchConfiguration('use_sim_time', default='true')
	resolution = LaunchConfiguration('resolution', default='0.05')
	publish_period_sec = LaunchConfiguration('publish_period_sec', default='1')
	configuration_directory = LaunchConfiguration('configuration_directory', default=os.path.join(pkg_share, 'config'))
	configuration_basename = LaunchConfiguration('configuration_basename', default='config.lua')
	rviz_config_dir = os.path.join(pkg_share, 'rviz/cartographer.rviz')

	cartographer_node = Node(
		package = 'cartographer_ros',
		executable = 'cartographer_node',
		name = 'cartographer_node',
		arguments = ['-configuration_directory', configuration_directory, '-configuration_basename', configuration_basename],
		parameters = [{'use_sim_time': use_sim_time}],
		remappings=[('/scan', '/ray_data')]
	)
	
	cartographer_occupancy_grid_node = Node(
		package = 'cartographer_ros',
		executable = 'cartographer_occupancy_grid_node',
		name = 'cartographer_occupancy_grid_node',
		arguments = ['-resolution', resolution, '-publish_period_sec', publish_period_sec],
		parameters = [{'use_sim_time': use_sim_time}]
	)
	
	rviz2_node = Node(
		package = 'rviz2',
		executable = 'rviz2',
		name = 'rviz2',
		arguments = ['-d', rviz_config_dir],
		parameters = [{'use_sim_time': use_sim_time}],
		output = 'screen'
	)
	
	ld = LaunchDescription()
	
	ld.add_action(cartographer_node)
	ld.add_action(cartographer_occupancy_grid_node)
	ld.add_action(rviz2_node)
	
	return ld
