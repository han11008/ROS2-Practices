import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from rclpy.action.client import ActionClient
from rosgraph_msgs.msg import Clock
from nav2_msgs.action import NavigateToPose
import sys

class GoalSender(Node):
	def __init__(self, x=0.0, y=0.0):
		super().__init__('navigate_to_pose_requester')
		self.x = x
		self.y = y
		self.goal_sent = False
		qos_profile = QoSProfile(depth=1, reliability=QoSReliabilityPolicy.BEST_EFFORT)
		self.clock_listener = self.create_subscription(Clock, 'clock', self.getClock, qos_profile)
		self.action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')
		
	def getClock(self, msg):
		if not self.goal_sent and self.action_client.wait_for_server(timeout_sec=1):
			pose_msg = NavigateToPose.Goal()
			pose_msg.pose.header.stamp = msg.clock
			pose_msg.pose.header.frame_id = 'map'
			
			pose_msg.pose.pose.position.x = self.x
			pose_msg.pose.pose.position.y = self.y
			
			self.get_logger().info(f'sending goal: x={self.x}, y={self.y}')
			self.goal_sent = True
			self.send_future = self.action_client.send_goal_async(pose_msg)
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
		self.get_logger().info(f'Getting result: {future.result().result}')
		raise SystemExit

def main(args=None):
	rclpy.init(args=args)
	x = y = 0.0
	try:
		x = float(sys.argv[1])
		y = float(sys.argv[2])
	except:
		pass
	node = GoalSender(x, y)
	try:
		rclpy.spin(node)
	except SystemExit:
		node.destroy_node()
		rclpy.shutdown()

if __name__ == '__main__':
	main()
