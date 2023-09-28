import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterEvent
from rclpy.parameter import Parameter
from rclpy import qos
import sys
from typing import List

class ParamMonitor(Node):
	def __init__(self, monitor_nodes: List):
		super().__init__('param_monitor_node')
		if monitor_nodes == []:
			self.sub = self.create_subscription(ParameterEvent, '/parameter_events', self.changed_param_info, qos_profile=qos.qos_profile_parameter_events)
			self.get_logger().info('Start monitoring...')
		else:
			self.sub = self.create_subscription(ParameterEvent, '/parameter_events', self.spec_node_callback, qos_profile=qos.qos_profile_parameter_events)
			self.monitor_nodes = monitor_nodes
			self.get_logger().info(f'Node(s) to be monitored: {self.monitor_nodes}. Start monitoring...')

	def changed_param_info(self, msg: ParameterEvent):
		param: Parameter
		any_changed = False
		output_info = f'Changed parameter(s) of node {msg.node}:\n'
		for param in msg.changed_parameters:
			any_changed = True
			output_info += f'{param.name}: {param.value}\n'
		if any_changed:
			self.get_logger().info(output_info)

	def spec_node_callback(self, msg: ParameterEvent):
		if msg.node in self.monitor_nodes:
			self.changed_param_info(msg)

def main(args=None):
	rclpy.init(args=args)
	if len(sys.argv) > 1:
		arr = sys.argv[1:]
	else:
		arr = []
	node = ParamMonitor(arr)
	try:
		rclpy.spin(node)
	except KeyboardInterrupt:
		node.destroy_node()
	if rclpy.ok():
		rclpy.shutdown()

if __name__ == '__main__':
	main()
