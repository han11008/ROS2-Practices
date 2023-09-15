import rclpy
from rclpy.node import Node
from custom_interfaces.srv import AddThreeInts

class Server(Node):
	def __init__(self):
		super().__init__('server_node_py')
		self.srv_server = self.create_service(AddThreeInts, 'add_three_ints', self.callback)
	
	def callback(self, request, response):
		self.get_logger().info(f'Request of summing: a={request.a}, b={request.b}, c={request.c}')
		response.sum = request.a + request.b + request.c
		return response

def main(args=None):
	rclpy.init(args=args)
	server = Server()
	rclpy.spin(server)
	server.destroy_node()
	rclpy.shutdown()

if __name__ == '__main__':
	main()
