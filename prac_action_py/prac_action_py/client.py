import rclpy
from rclpy.node import Node
from rclpy.action.client import ActionClient
from custom_interfaces.action import Fibonacci
import sys

class FibonacciActionClient(Node):
	def __init__(self, order=1):
		super().__init__('client_action_node')
		self.action_client = ActionClient(self, Fibonacci, 'fibonacci_action')
		while not self.action_client.wait_for_server(timeout_sec=1):
			self.get_logger().info('Waiting for fibonacci server to be available...')
		self.send_goal(order)
	
	def send_goal(self, order):
		self.get_logger().info(f'Sending request: order={order}')
		goal_msg = Fibonacci.Goal()
		goal_msg.order = order
		self.send_future = self.action_client.send_goal_async(goal_msg)
		self.send_future.add_done_callback(self.goal_response_callback)
	
	def goal_response_callback(self, future):
		goal_handle = future.result()
		if not goal_handle.accepted:
			self.get_logger().info('Goal rejected')
			return
		else:
			self.get_logger().info('Goal accepted')
		self.result_future = goal_handle.get_result_async()
		self.result_future.add_done_callback(self.result_callback)
	
	def result_callback(self, future):
		self.get_logger().info(f'Getting result: {future.result().result.seq.tolist()}')
		self.destroy_node()
		rclpy.shutdown()

def main(args=None):
	rclpy.init(args=args)
	client = FibonacciActionClient(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
	rclpy.spin(client)	

if __name__ == '__main__':
	main()
