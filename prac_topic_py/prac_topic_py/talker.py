import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Talker(Node):
	def __init__(self):
		super().__init__('talker_node_py')
		self.publisher = self.create_publisher(String, 'greet_topic', 10)
		timer_period = 0.8 # seconds
		self.timer = self.create_timer(timer_period, self.timerCallback)
		self.count = 0
	
	def timerCallback(self):
		msg = String()
		msg.data = f'{self.count}: Hello!'
		self.publisher.publish(msg)
		self.get_logger().info(f'Publishing: [{msg.data}]')
		self.count += 1

def main(args=None):
	rclpy.init(args=args)
	talker = Talker()
	rclpy.spin(talker)
	talker.destroy_node()
	rclpy.shutdown()	

if __name__ == '__main__':
	main()
