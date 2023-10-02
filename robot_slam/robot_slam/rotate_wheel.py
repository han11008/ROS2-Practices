import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from threading import Thread

class RotateWheelNode(Node):
	def __init__(self, name):
		super().__init__(name)
		self.pub = self.create_publisher(JointState, 'joint_states', 10)
		self.init_joint_states()
		self.pub_rate = self.create_rate(5) # 5Hz
		self.thread = Thread(target=self.pub_thread)
		self.thread.start()
		self.get_logger().info(f'Node "{name}" initialized')
	
	def init_joint_states(self):
		self.joint_speeds = [5.0, 5.0]
		self.joint_states_msg = JointState()
		self.joint_states_msg.header.stamp = self.get_clock().now().to_msg()
		self.joint_states_msg.header.frame_id = ""
		self.joint_states_msg.name = ['right_wheel_joint', 'left_wheel_joint']
		self.joint_states_msg.position = [0.0, 0.0]
		self.joint_states_msg.velocity = self.joint_speeds
		self.joint_states_msg.effort = []
	
	def pub_thread(self):
		self.get_logger().info(f'Start publishing thread')
		while rclpy.ok():
			try:
				self.joint_states_msg.position[0] += self.joint_states_msg.velocity[0] * 0.2
				self.joint_states_msg.position[1] += self.joint_states_msg.velocity[1] * 0.2
				self.joint_states_msg.header.stamp = self.get_clock().now().to_msg()
				self.pub.publish(self.joint_states_msg)				
				self.pub_rate.sleep()
			except KeyboardInterrupt:
				self.thread.join()
				self.destroy_node()
				rclpy.shutdown()

def main(args=None):
	rclpy.init(args=args)
	node = RotateWheelNode('rotate_wheel_node')
	rclpy.spin(node)

if __name__ == '__main__':
	main()
