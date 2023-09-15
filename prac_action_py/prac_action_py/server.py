import rclpy
from rclpy.node import Node
from rclpy.action.server import ActionServer
from custom_interfaces.action import Fibonacci
from time import sleep

class FibonacciActionServer(Node):
	def __init__(self):
		super().__init__('server_action_node')
		self.action_server = ActionServer(self, Fibonacci, 'fibonacci_action', self.callback)
	
	def callback(self, goal_handle):
		self.get_logger().info('Executing goal')
		feedback_msg = Fibonacci.Feedback()
		feedback_msg.part_seq = [0, 1]
		for i in range(1, goal_handle.request.order):
			feedback_msg.part_seq.append(feedback_msg.part_seq[i] + feedback_msg.part_seq[i-1])
			self.get_logger().info(f'Feedback: {feedback_msg.part_seq.tolist()}')
			goal_handle.publish_feedback(feedback_msg)
			sleep(1)
		goal_handle.succeed()
		result = Fibonacci.Result()
		result.seq = feedback_msg.part_seq
		self.get_logger().info(f'Result: {result.seq.tolist()}')
		return result

def main(args=None):
	rclpy.init(args=args)
	server = FibonacciActionServer()
	try:
		rclpy.spin(server)
	except:
		pass
	server.destroy_node()
	if rclpy.ok():
		rclpy.shutdown()

if __name__ == '__main__':
	main()
