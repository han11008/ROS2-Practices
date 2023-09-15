import rclpy
from rclpy.node import Node
from custom_interfaces.srv import AddThreeInts
from random import randint
from time import sleep

class Client(Node):
	def __init__(self):
		super().__init__('client_node_py')
		self.srv_client = self.create_client(AddThreeInts, 'add_three_ints')
		try:
			while rclpy.ok():
				while not self.srv_client.wait_for_service(timeout_sec=1.0):
					self.get_logger().info('Waiting for service to be available...')
				self.request = AddThreeInts.Request()
				self.send_request()
				sleep(3)
		except KeyboardInterrupt:
			pass
	
	def send_request(self):
		self.request.a = randint(0, 100)
		self.request.b = randint(0, 100)
		self.request.c = randint(0, 100)
		self.get_logger().info(f'Sending request of summing: a={self.request.a}, b={self.request.b}, c={self.request.c}')
		self.future = self.srv_client.call_async(self.request)
		rclpy.spin_until_future_complete(self, self.future)
		if (self.future.done()):
			self.get_logger().info(f'Getting result: sum={self.future.result().sum}')
		else:
			self.get_logger().info('Failed getting result')
			

def main(args=None):
	rclpy.init(args=args)
	client = Client()
	rclpy.spin(client)
	client.destroy_node()
	rclpy.shutdown()

if __name__ == '__main__':
	main()
