

from accessory import Accessory
from core import ServoEnum

class Golf(Accessory):
	'''Control the MLD GOLF club
	
	Up/down = move the club
	X/Y = open and close the arms
	A = strike the ball'''
        def up(self):
            '''The up button on the 4-way direction pad'''
            print("MLD GOLF 7,low")
            self.core.throttle(-1,0,ServoEnum.LEFT_FLINGER_SERVO,0)

        def down(self):
            '''The up button on the 4-way direction pad'''
            print("MLD GOLF 7,high")
            self.core.throttle(1,0,ServoEnum.LEFT_FLINGER_SERVO,0)
        def left(self):
            '''The up button on the 4-way direction pad'''

        def right(self):
            '''The up button on the 4-way direction pad'''

        def btn_a(self):
            '''The A button'''
            print("MLD GOLF 8, low")
            self.core.throttle(-1,0,ServoEnum.RIGHT_FLINGER_SERVO,0)

        def btn_b(self):
            '''The B button'''
            print("MLD GOLF 8,igh")
            self.core.throttle(1,0,ServoEnum.RIGHT_FLINGER_SERVO,0)

        def btn_x(self):
            '''The X button'''
            print("MLD GOLF 9,low")
            self.core.throttle(-1,0,ServoEnum.WINCH_SERVO,0)
        def btn_y(self):
            '''The Y button'''
            print("MLD GOLF 9,high")
            self.core.throttle(1,0,ServoEnum.WINCH_SERVO,0)