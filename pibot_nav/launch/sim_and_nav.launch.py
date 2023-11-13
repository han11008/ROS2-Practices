import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml

def generate_launch_description():
	pkg_name = 'pibot_nav'
	pkg_share = get_package_share_directory(pkg_name)
	robot_name = 'tutorial_bot'
	world_name = 'room'
	
	# only one or none of the following could be True
	use_keepout_filter = False
	use_smoother = True
	use_collision_monitor = False
	use_denoise = False
	
	map_name = 'stb'
	
	use_sim_time = LaunchConfiguration('use_sim_time', default='true')
	ld = LaunchDescription()
	
	########## Gazebo simulation ##########
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
	
	########## Nav2 ##########
	nav2_param_name = 'nav2_params'
	param_path = os.path.join(pkg_share, f'param/{nav2_param_name}.yaml')
	nav2_bringup_share = get_package_share_directory('nav2_bringup')
	nav2_launch_path = os.path.join(nav2_bringup_share, 'launch/bringup_launch.py')
	map_path = os.path.join(pkg_share, f'map/{map_name}.yaml')
	
	if use_keepout_filter:
		nav2_param_name = 'nav2_params_with_keepout'
		param_path = os.path.join(pkg_share, f'param/{nav2_param_name}.yaml')
	elif use_smoother:
		nav2_param_name = 'nav2_params_with_smoother'
		param_path = os.path.join(pkg_share, f'param/{nav2_param_name}.yaml')
		bt_path = os.path.join(pkg_share, 'bt/navigate_to_pose_with_smoother.xml')
		param_path = RewrittenYaml(
			source_file = param_path,
			param_rewrites = {'use_sim_time': use_sim_time, 'default_nav_to_pose_bt_xml': bt_path}
		)
	elif use_collision_monitor:
		nav2_launch_path = os.path.join(pkg_share, 'launch/nav2_bringup.launch.py')
	elif use_denoise:
		nav2_param_name = 'nav2_params_with_denoise'
		param_path = os.path.join(pkg_share, f'param/{nav2_param_name}.yaml')
	
	nav2_launch = IncludeLaunchDescription(
		PythonLaunchDescriptionSource([nav2_launch_path]),
		launch_arguments = {
			'map': map_path,
			'use_sim_time': use_sim_time,
			'params_file': param_path
		}.items()
	)
	
	ld.add_action(nav2_launch)
	
	########## Nav2 keepout filtering ##########
	if use_keepout_filter:
		filter_param_path = os.path.join(pkg_share, 'param/keepout_params.yaml')
		filter_map_path = os.path.join(pkg_share, 'map/keepout.yaml')
		filter_configured_params = RewrittenYaml(
			source_file = filter_param_path,
			param_rewrites = {'use_sim_time': use_sim_time, 'yaml_filename': filter_map_path}
		)
		map_server_name = 'filter_mask_server'
		filter_server_name = 'costmap_filter_info_server'
		keepout_lifecycle_nodes = [map_server_name, filter_server_name]
		autostart = LaunchConfiguration('autostart', default='true')
		
		keepout_lifecycle_manager = Node(
			package = 'nav2_lifecycle_manager',
			executable = 'lifecycle_manager',
			name = 'lifecycle_manager_costmap_filters',
			emulate_tty = True,
			parameters = [{'use_sim_time': use_sim_time},
				{'autostart': autostart},
				{'node_names': keepout_lifecycle_nodes}]
		)
		
		keepout_map_server = Node(
			package = 'nav2_map_server',
			executable = 'map_server',
			name = map_server_name,
			emulate_tty = True,
			parameters = [filter_configured_params]
		)
		
		keepout_costmap_filter_info_server = Node(
			package = 'nav2_map_server',
			executable = 'costmap_filter_info_server',
			name = filter_server_name,
			emulate_tty = True,
			parameters = [filter_configured_params]
		)
		
		ld.add_action(keepout_lifecycle_manager)
		ld.add_action(keepout_map_server)
		ld.add_action(keepout_costmap_filter_info_server)
		
	########## Nav2 collision monitor ##########
	if use_collision_monitor:
		collision_param_path = os.path.join(pkg_share, 'param/collision_monitor_params.yaml')
		collision_configured_params = RewrittenYaml(
			source_file = collision_param_path,
			param_rewrites = {'use_sim_time': use_sim_time}
		)
		autostart = LaunchConfiguration('autostart', default='true')
		
		collision_lifecycle_manager = Node(
			package = 'nav2_lifecycle_manager',
			executable = 'lifecycle_manager',
			name = 'lifecycle_manager_collision_monitor',
			emulate_tty = True,
			parameters = [{'use_sim_time': use_sim_time},
				{'autostart': autostart},
				{'node_names': ['collision_monitor']}]
		)
		
		collision_monitor = Node(
			package = 'nav2_collision_monitor',
			executable = 'collision_monitor',
			name = 'collision_monitor',
			emulate_tty = True,
			parameters = [collision_configured_params]
		)
		
		ld.add_action(collision_lifecycle_manager)
		ld.add_action(collision_monitor)
	
	########## RViz navigation process visualization ##########
	rviz_config_path = os.path.join(pkg_share, 'rviz/nav2_default_view.rviz')
	if use_collision_monitor:
		rviz_config_path = os.path.join(pkg_share, 'rviz/collision_monitor.rviz')
		
	rviz_node = Node(
		package = 'rviz2',
		executable = 'rviz2',
		name = 'rviz2',
		arguments = f'-d {rviz_config_path}'.split(' '),
		parameters = [{'use_sim_time': use_sim_time}],
		output = 'screen'
	)
	
	pose_init_node = Node(
		package = pkg_name,
		executable = 'initial_pose',
	)
	
	ld.add_action(rviz_node)
	ld.add_action(pose_init_node)
	
	return ld
