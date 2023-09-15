import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Listener(Node):
	def __init__(self):
		super().__init__('listener_node_py')
		self.subscriber = self.create_subscription(String, 'greet_topic', self.callback, 10)
	
	def callback(self, msg):
		self.get_logger().info(f'Hearing: [{msg.data}]')

def main(args=None):
	rclpy.init(args=args)
	listener = Listener()
	rclpy.spin(listener)
	listener.destroy_node()
	rclpy.shutdown()	

if __name__ == '__main__':
	main()
