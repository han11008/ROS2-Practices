import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped, Pose, Twist

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
TF_PUB_PERIOD = 0.1 # second

class FAKE_MOTOR:
	def __init__(self):
		pass

	def stop(self):
		return 'stop'

	def quit(self):
		return 'quit'

	def forward(self):
		return 'go forward'

	def backward(self):
		return 'go backward'

	def turn_right(self):
		return 'turn right'

	def turn_left(self):
		return 'turn left'

class Listener(Node):
	def __init__(self):
		super().__init__('fake_motor_listener_node')
		self.initOdom()
		self.motor = FAKE_MOTOR()
		self.listener = self.create_subscription(String, 'motor_cmd_topic', self.getCmd, 10)
		self.get_logger().info('Start listening to commands...')

	def getCmd(self, msg):
		log = f'Receive "{msg.data}": '
		if msg.data == CMDS['QUIT']:
			log += self.motor.quit()
			self.get_logger().info(log)
			raise SystemExit

		elif msg.data == CMDS['STOP']:
			log += self.motor.stop()
			self.twist.linear.x = 0.0
			self.twist.angular.z = 0.0

		elif msg.data == CMDS['FORWARD']:
			log += self.motor.forward()
			self.twist.linear.x = LINEAR_SPEED
			self.twist.angular.z = 0.0

		elif msg.data == CMDS['BACKWARD']:
			log += self.motor.backward()
			self.twist.linear.x = -LINEAR_SPEED
			self.twist.angular.z = 0.0

		elif msg.data == CMDS['TURN_LEFT']:
			log += self.motor.turn_left()
			self.twist.linear.x = 0.0
			self.twist.angular.z = RADIAN

		elif msg.data == CMDS['TURN_RIGHT']:
			log += self.motor.turn_right()
			self.twist.linear.x = 0.0
			self.twist.angular.z = -RADIAN

		else:
			log += 'not defined'
		self.get_logger().info(log)

	def initOdom(self):
		self.pose = Pose()
		self.twist = Twist()
		self.prev_time = self.get_clock().now()
		self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
		self.timer = self.create_timer(TF_PUB_PERIOD, self.publishOdom)

	def publishOdom(self):
		odom_msg = Odometry()
		cur_time = self.get_clock().now()
		period = (cur_time - self.prev_time).nanoseconds/1000000000

		_, _, yaw = self.quaternionToEuler(self.pose.orientation.x, self.pose.orientation.y, self.pose.orientation.z, self.pose.orientation.w)
		z_sin = math.sin(yaw)
		z_cos = math.cos(yaw)
		self.pose.position.x += self.twist.linear.x * period * z_cos
		self.pose.position.y += self.twist.linear.x * period * z_sin
		qx, qy, qz, qw = self.eulerToQuaternion(self.twist.angular.x * period, self.twist.angular.y * period, self.twist.angular.z * period)
		qx, qy, qz, qw = self.rotationAccmulate(qx, qy, qz, qw, self.pose.orientation.x, self.pose.orientation.y, self.pose.orientation.z, self.pose.orientation.w)
		# While running on x-y plane, the quaternion values of x and y should not change.
		# self.pose.orientation.x = qx
		# self.pose.orientation.y = qy
		self.pose.orientation.z = qz
		self.pose.orientation.w = qw

		odom_msg.header.stamp = cur_time.to_msg()
		odom_msg.header.frame_id = 'odom'

		odom_msg.child_frame_id = 'base_footprint'

		odom_msg.pose.pose = self.pose
		odom_msg.twist.twist = self.twist

		self.odom_pub.publish(odom_msg)
		self.prev_time = cur_time

	def eulerToQuaternion(self, roll, pitch, yaw):
		qx = math.sin(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) - math.cos(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
		qy = math.cos(roll/2) * math.sin(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.cos(pitch/2) * math.sin(yaw/2)
		qz = math.cos(roll/2) * math.cos(pitch/2) * math.sin(yaw/2) - math.sin(roll/2) * math.sin(pitch/2) * math.cos(yaw/2)
		qw = math.cos(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
		return qx, qy, qz, qw

	def quaternionToEuler(self, qx, qy, qz, qw):
		t0 = 2.0 * (qw * qx + qy * qz)
		t1 = 1.0 - 2.0 * (qx * qx + qy * qy)
		roll = math.atan2(t0, t1)
		t2 = 2.0 * (qw * qy - qz * qx)
		t2 = 1.0 if t2 > 1.0 else t2
		t2 = -1.0 if t2 < -1.0 else t2
		pitch = math.asin(t2)
		t3 = 2.0 * (qw * qz + qx * qy)
		t4 = 1.0 - 2.0 * (qy * qy + qz * qz)
		yaw = math.atan2(t3, t4)
		return roll, pitch, yaw

	def rotationAccmulate(self, x1, y1, z1, w1, x2, y2, z2, w2):
		qx = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
		qy = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
		qz = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
		qw = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
		return qx, qy, qz, qw

def main(args=None):
	rclpy.init(args=args)
	listener = Listener()
	try:
		rclpy.spin(listener)
	except SystemExit:
		listener.destroy_node()
		rclpy.shutdown()
	except KeyboardInterrupt:
		pass

if __name__ == '__main__':
	main()

