import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import termios, tty, select, sys

CMDS = {'QUIT': 'q',
	'STOP': 's',
	'FORWARD': 'w',
	'BACKWARD': 'x',
	'TURN_LEFT': 'a',
	'TURN_RIGHT': 'd',
	'HALF_DC': 'j',
	'DOUBLE_DC': 'l',
	'HALF_FREQ': 'k',
	'DOUBLE_FREQ': 'i'}

class Controller(Node):
	def __init__(self):
		super().__init__('motor_controller_node')
		self.publisher = self.create_publisher(String, 'motor_cmd_topic', 10)
		direction = 'Reading from the keyboard and publish to control the motor.\n' +\
		'w/x: go forward/backward\n' +\
		'a/d: turn left/right\n' +\
		's: stop\n' +\
		'q: end motor controlling\n' +\
		'j/l: half/double duty cycle\n' +\
		'k/i: half/double frequency\n' +\
		'ctrl+c: stop teleop\n' +\
		'---------------------------------------------'
		print(direction)
		self.termios_set = termios.tcgetattr(sys.stdin)
		self.teleop()

	def getKey(self):
		tty.setraw(sys.stdin.fileno())
		select.select([sys.stdin], [], [], 0)
		key = sys.stdin.read(1)
		termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.termios_set)
		return key

	def teleop(self):
		try:
			while True:
				key = self.getKey()
				# self.get_logger().info(f'Key {key} pressed')
				if key in CMDS.values():
					self.get_logger().info(f'Key {key} pressed')
					cmd = String()
					cmd.data = key
					self.publisher.publish(cmd)
				elif key == '\x03':
					self.get_logger().info('Stop teleop')
					break
		except Exception as e:
			self.get_logger().info(e)
		finally:
			raise SystemExit

def main(args=None):
	rclpy.init(args=args)
	controller = Controller()
	try:
		rclpy.spin(controller)
	except SystemExit:
		controller.destroy_node()
		rclpy.shutdown()

if __name__ == '__main__':
	main()
