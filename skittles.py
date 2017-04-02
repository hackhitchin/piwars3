

from accessory import Accessory
from core import ServoEnum

class Skittles(Accessory):
	def __init__(self, core):
		self.core = core
		self.left_claw_pos = 0
		self.right_claw_pos = 0
		self.winch_servo_pos = 0
		self.claw_increment = 0.05
		self.winch_increment = 0.02
		self.spinner_increment = 0.1

		self.left_motor_speed = -1.0
		self.right_motor_speed = -1.0
	'''Control the skittles launcher
	
	Up/down = raise/lower the launcher
	A = launch! (start motors and push ball into them)
	B = stop (stop motors and retract pusher)'''
	def left(self):
		self.winch_servo_pos -= (self.winch_increment)
		self.winch_servo_pos = self.gate_winch(self.winch_servo_pos)
		print("SERVO %f" % self.winch_servo_pos)
		self.core.throttle(self.winch_servo_pos, 0,
							ServoEnum.WINCH_SERVO, ServoEnum.SERVO_NONE)

	def right(self):
		self.winch_servo_pos += (self.winch_increment)
		self.winch_servo_pos = self.gate_winch(self.winch_servo_pos)
		print("SERVO %f" % self.winch_servo_pos)
		self.core.throttle(self.winch_servo_pos, 0,
							ServoEnum.WINCH_SERVO, ServoEnum.SERVO_NONE)

	def down(self):
		self.left_claw_pos += self.claw_increment
		self.right_claw_pos += self.claw_increment
		self.left_claw_pos = self.gate_claws(self.left_claw_pos)
		self.right_claw_pos = self.gate_claws(self.right_claw_pos)
		self.core.throttle(self.left_claw_pos, self.right_claw_pos,
							ServoEnum.LEFT_FLINGER_SERVO, ServoEnum.RIGHT_FLINGER_SERVO)

	def up(self):
		self.left_claw_pos -= self.claw_increment
		self.right_claw_pos -= self.claw_increment
		self.left_claw_pos = self.gate_claws(self.left_claw_pos)
		self.right_claw_pos = self.gate_claws(self.right_claw_pos)
		self.core.throttle(self.left_claw_pos, self.right_claw_pos,
							ServoEnum.LEFT_FLINGER_SERVO, ServoEnum.RIGHT_FLINGER_SERVO)

	def btn_x(self):
		self.left_motor_speed += self.spinner_increment
		self.right_motor_speed += self.spinner_increment
		self.left_motor_speed = self.gate_esc(self.left_motor_speed)
		self.right_motor_speed = self.gate_esc(self.right_motor_speed)
		self.core.throttle(self.left_motor_speed, self.right_motor_speed,
							ServoEnum.LEFT_FLINGER_ESC, ServoEnum.RIGHT_FLINGER_ESC)

	def btn_b(self):
		self.left_motor_speed -= self.spinner_increment
		self.right_motor_speed -= self.spinner_increment
		print("SPINNERS %f, %f" % (self.left_motor_speed, self.right_motor_speed))
		self.left_motor_speed = self.gate_esc(self.left_motor_speed)
		self.right_motor_speed = self.gate_esc(self.right_motor_speed)

		self.core.throttle(self.left_motor_speed, self.right_motor_speed,
							ServoEnum.LEFT_FLINGER_ESC, ServoEnum.RIGHT_FLINGER_ESC)		

	def btn_y(self):
		self.left_claw_pos -= self.claw_increment * 20
		self.right_claw_pos -= self.claw_increment * 20
		self.left_claw_pos = self.gate_claws(self.left_claw_pos)
		self.right_claw_pos = self.gate_claws(self.right_claw_pos)
		self.core.throttle(self.left_claw_pos, self.right_claw_pos,
							ServoEnum.LEFT_FLINGER_SERVO, ServoEnum.RIGHT_FLINGER_SERVO)

	def gate_esc(self, pos):
		return min(1, max(-1, pos))

	def gate_claws(self, pos):
		return min(0, max(-1, pos))

	def gate_winch(self, pos):
		return min(0, max(-0.2, pos))		
