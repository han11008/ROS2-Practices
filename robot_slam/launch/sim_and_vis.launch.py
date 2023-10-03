import os
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
	pkg_name = 'robot_slam'
	robot_name = 'robot'
	urdf_name = 'robot_descript.urdf'
	world_name = 'fish_world.sdf'
	
	use_sim_time = LaunchConfiguration('use_sim_time', default='true')
	pkg_share = FindPackageShare(package=pkg_name).find(pkg_name)
	urdf_model_path = os.path.join(pkg_share, 'urdf/'+urdf_name)
	world_path = os.path.join(pkg_share, 'world/'+world_name)
	
	gazebo_node = ExecuteProcess(
		cmd = f'gazebo {world_path} -s libgazebo_ros_init.so -s libgazebo_ros_factory.so'.split(' '),
		output = 'screen'
	)
	
	spawn_entity_node = Node(
		package = 'gazebo_ros',
		executable = 'spawn_entity.py',
		arguments = ['-entity', robot_name, '-file', urdf_model_path, '-z', '0.076'],
	)
	
	robot_state_publisher_node = Node(
		package = 'robot_state_publisher',
		executable = 'robot_state_publisher',
		arguments = [urdf_model_path],
		parameters = [{'use_sim_time': use_sim_time}]
	)
	
	joint_state_publisher_node = Node(
		package = 'joint_state_publisher_gui',
		executable = 'joint_state_publisher_gui',
		name = 'joint_state_publisher_gui',
		arguments = [urdf_model_path]
	)
		
	rviz2_node = Node(
		package = 'rviz2',
		executable = 'rviz2',
		name = 'rviz2',
		output = 'screen'
	)
	
	ld = LaunchDescription()
	
	ld.add_action(gazebo_node)
	ld.add_action(spawn_entity_node)
	ld.add_action(robot_state_publisher_node)
	# ld.add_action(joint_state_publisher_node)
	# ld.add_action(rviz2_node)
	
	return ld
