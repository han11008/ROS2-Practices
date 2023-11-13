import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from geometry_msgs.msg import PoseWithCovarianceStamped
from rosgraph_msgs.msg import Clock

class PoseInitializer(Node):
	def __init__(self):
		super().__init__('pose_initializer')
		qos_profile = QoSProfile(depth=1, reliability=QoSReliabilityPolicy.BEST_EFFORT)
		self.clock_listener = self.create_subscription(Clock, 'clock', self.getClock, qos_profile)
		self.publisher = self.create_publisher(PoseWithCovarianceStamped, 'initialpose', 10)
		
	def getClock(self, msg):
		pose_msg = PoseWithCovarianceStamped()
		pose_msg.header.stamp = msg.clock
		pose_msg.header.frame_id = 'map'
		pose_msg.pose.covariance[0] = 0.25
		pose_msg.pose.covariance[7] = 0.25
		pose_msg.pose.covariance[35] = 0.06853891909122467
		self.publisher.publish(pose_msg)
		raise SystemExit

def main(args=None):
	rclpy.init(args=args)
	node = PoseInitializer()
	try:
		rclpy.spin(node)
	except SystemExit:
		node.destroy_node()
		rclpy.shutdown()

if __name__ == '__main__':
	main()
