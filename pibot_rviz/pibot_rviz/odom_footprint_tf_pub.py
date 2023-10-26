import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from tf2_ros.transform_broadcaster import TransformBroadcaster
from geometry_msgs.msg import TransformStamped

class OdomTfPublisher(Node):
	def __init__(self, timer_period=0.01):
		super().__init__('odom_footprint_tf_node')
		self.odom_sub = self.create_subscription(Odometry, 'odom', self.updateOdom, 10)
		self.odom_msg = Odometry()
		self.tf_pub = TransformBroadcaster(self)
		self.timer = self.create_timer(timer_period, self.publishTf)

	def updateOdom(self, msg):
		self.odom_msg.pose.pose.position.x = msg.pose.pose.position.x
		self.odom_msg.pose.pose.position.y = msg.pose.pose.position.y
		self.odom_msg.pose.pose.position.z = msg.pose.pose.position.z
		self.odom_msg.pose.pose.orientation.w = msg.pose.pose.orientation.w
		self.odom_msg.pose.pose.orientation.x = msg.pose.pose.orientation.x
		self.odom_msg.pose.pose.orientation.y = msg.pose.pose.orientation.y
		self.odom_msg.pose.pose.orientation.z = msg.pose.pose.orientation.z		

	def publishTf(self):
		tf_msg = TransformStamped()

		tf_msg.header.stamp = self.get_clock().now().to_msg()
		tf_msg.header.frame_id = 'odom'

		tf_msg.child_frame_id = 'base_footprint'

		tf_msg.transform.translation.x = self.odom_msg.pose.pose.position.x
		tf_msg.transform.translation.y = self.odom_msg.pose.pose.position.y
		tf_msg.transform.translation.z = self.odom_msg.pose.pose.position.z
		tf_msg.transform.rotation.w = self.odom_msg.pose.pose.orientation.w
		tf_msg.transform.rotation.x = self.odom_msg.pose.pose.orientation.x
		tf_msg.transform.rotation.y = self.odom_msg.pose.pose.orientation.y
		tf_msg.transform.rotation.z = self.odom_msg.pose.pose.orientation.z

		self.tf_pub.sendTransform(tf_msg)

def main(args=None):
	rclpy.init()
	node = OdomTfPublisher()
	try:
		rclpy.spin(node)
		node.destroy_node()
		rclpy.shutdown()
	except:
		pass

if __name__ == '__main__':
	main()
