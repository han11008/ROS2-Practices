import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
	pkg_name = 'slam_and_nav'
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
	
	slam_launch = IncludeLaunchDescription(
		PythonLaunchDescriptionSource([slam_toolbox_launch_path]),
		launch_arguments = {
			'use_sim_time': use_sim_time,
			'slam_params_file': slam_config_path
		}.items()
	)
	
	ld.add_action(slam_launch)
	
	nav2_param_path = os.path.join(pkg_share, 'param/nav2_params.yaml')
	nav2_share_dir = get_package_share_directory('nav2_bringup')
	nav2_launch_path = os.path.join(nav2_share_dir, 'launch/navigation_launch.py')
	rviz_config_path = os.path.join(nav2_share_dir, 'rviz/nav2_default_view.rviz')
	
	nav2_bringup_launch = IncludeLaunchDescription(
		PythonLaunchDescriptionSource([nav2_launch_path]),
		launch_arguments = {
			'use_sim_time': use_sim_time,
			'params_file': nav2_param_path
		}.items()
	)
	
	pub_map_node = ExecuteProcess(
		cmd = ['ros2', 'topic', 'pub --once', '/goal_pose', 'geometry_msgs/PoseStamped', "{header: {stamp: {sec: 0}, frame_id: 'map'}, pose: {position: {x: 0.2, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}"]
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
	ld.add_action(pub_map_node)
	ld.add_action(rviz_node)
	
	return ld
