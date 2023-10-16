import RPi.GPIO as GPIO
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

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

class KC_MOTOR:
	def __init__(self, out1pin1=18, out1pin2=17, out2pin1=23, out2pin2=22, en_pin=19):
		self.motor_right = [out1pin1, out1pin2]
		self.motor_left =  [out2pin1, out2pin2]

		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)

		GPIO.setup(self.motor_right[0], GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(self.motor_right[1], GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup( self.motor_left[0], GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup( self.motor_left[1], GPIO.OUT, initial=GPIO.LOW)

		GPIO.setup(en_pin, GPIO.OUT)
		self.duty_cycle = 100
		self.freq = 1000
		self.pwm = GPIO.PWM(en_pin, self.freq)
		self.pwm.start(self.duty_cycle)

	def stop(self):
		GPIO.output(self.motor_right[0], False)
		GPIO.output(self.motor_right[1], False)
		GPIO.output( self.motor_left[0], False)
		GPIO.output( self.motor_left[1], False)
		return 'stop'

	def quit(self):
		self.stop()
		return 'quit'

	def forward(self):
		GPIO.output(self.motor_right[0], True)
		GPIO.output(self.motor_right[1], False)
		GPIO.output( self.motor_left[0], True)
		GPIO.output( self.motor_left[1], False)
		return 'go forward'

	def backward(self):
		GPIO.output(self.motor_right[0], False)
		GPIO.output(self.motor_right[1], True)
		GPIO.output( self.motor_left[0], False)
		GPIO.output( self.motor_left[1], True)
		return 'go backward'

	def left_side_forward(self):
		GPIO.output(self.motor_right[0], True)
		GPIO.output(self.motor_right[1], False)
		GPIO.output( self.motor_left[0], False)
		GPIO.output( self.motor_left[1], False)
		return 'left-side go forward(turn right)'

	def right_side_forward(self):
		GPIO.output(self.motor_right[0], False)
		GPIO.output(self.motor_right[1], False)
		GPIO.output( self.motor_left[0], True)
		GPIO.output( self.motor_left[1], False)
		return 'right-side go forward(turn left)'

	def half_dc(self):
		self.duty_cycle //= 2
		self.pwm.ChangeDutyCycle(self.duty_cycle)
		return f'half duty cycle (current value: {self.duty_cycle})'

	def double_dc(self):
		self.duty_cycle = min(100, max(1, self.duty_cycle*2))
		self.pwm.ChangeDutyCycle(self.duty_cycle)
		return f'double duty cycle (current value: {self.duty_cycle})'

	def half_freq(self):
		self.freq = max(1, self.freq//2)
		self.pwm.ChangeFrequency(self.freq)
		return f'half frequency (current value: {self.freq})'

	def double_freq(self):
		self.freq *= 2
		self.pwm.ChangeFrequency(self.freq)
		return f'double frequency (current value: {self.freq})'

	def cleanup(self):
		self.quit()
		self.pwm.stop()
		GPIO.cleanup()

class Listener(Node):
	def __init__(self):
		super().__init__('motor_listener_node')
		self.motor = KC_MOTOR()
		self.listener = self.create_subscription(String, 'motor_cmd_topic', self.callback, 10)
		self.get_logger().info('Start listening to commands...')

	def callback(self, msg):
		log = f'Receive "{msg.data}": '
		if msg.data == CMDS['QUIT']:
			self.cleanMotor()
			self.get_logger().info(log + 'quit')
			raise SystemExit
		elif msg.data == CMDS['STOP']:
			log += self.motor.stop()
			self.get_logger().info(log)
		elif msg.data == CMDS['FORWARD']:
			log += self.motor.forward()
			self.get_logger().info(log)
		elif msg.data == CMDS['BACKWARD']:
			log += self.motor.backward()
			self.get_logger().info(log)
		elif msg.data == CMDS['TURN_LEFT']:
			log += self.motor.right_side_forward()
			self.get_logger().info(log)
		elif msg.data == CMDS['TURN_RIGHT']:
			log += self.motor.left_side_forward()
			self.get_logger().info(log)
		elif msg.data == CMDS['HALF_DC']:
			log += self.motor.half_dc()
			self.get_logger().info(log)
		elif msg.data == CMDS['DOUBLE_DC']:
			log += self.motor.double_dc()
			self.get_logger().info(log)
		elif msg.data == CMDS['HALF_FREQ']:
			log += self.motor.half_freq()
			self.get_logger().info(log)
		elif msg.data == CMDS['DOUBLE_FREQ']:
			log += self.motor.double_freq()
			self.get_logger().info(log)
		else:
			log += 'not defined'
			self.get_logger().info(log)

	def cleanMotor(self):
		self.motor.cleanup()

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

