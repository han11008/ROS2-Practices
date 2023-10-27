import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from geometry_msgs.msg import Twist
import termios, tty, select, sys, math

CMDS = {
	'QUIT': 'q',
	'STOP': 's',
	'FORWARD': 'w',
	'BACKWARD': 'x',
	'TURN_LEFT': 'a',
	'TURN_RIGHT': 'd',
}

LINEAR_SPEED = 0.4 # m/s
DEGREE = 60 # per second
RADIAN = DEGREE * math.pi / 180

MSGS = {
	CMDS['STOP']: [0.0, 0.0],
	CMDS['FORWARD']: [LINEAR_SPEED * 1.0, 0.0],
	CMDS['BACKWARD']: [-LINEAR_SPEED * 1.0, 0.0],
	CMDS['TURN_LEFT']: [0.0, RADIAN * 1.0],
	CMDS['TURN_RIGHT']: [0.0, -RADIAN * 1.0],
}

class Controller(Node):
	def __init__(self):
		super().__init__('motor_controller_node')
		self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
		self.end_publisher = self.create_publisher(Bool, 'kill_remote', 1)
		guide = 'Reading from the keyboard and publish to control the motor.\n' +\
		'w/x: go forward/backward\n' +\
		'a/d: turn left/right\n' +\
		's: stop\n' +\
		'q: end motor controlling\n' +\
		'ctrl+c: stop teleop\n' +\
		'---------------------------------------------'
		print(guide)
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
					if key == 'q':
						end_cmd = Bool()
						end_cmd.data = True
						self.end_publisher.publish(end_cmd)
					else:
						cmd = Twist()
						cmd.linear.x = MSGS[key][0]
						cmd.angular.z = MSGS[key][1]
						self.publisher.publish(cmd)
					self.get_logger().info(f'Key {key} pressed')
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
