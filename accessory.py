
class Accessory(object):
        '''Class for remotely-controlled accessories; ie. the golf club or ball flinger'''
        def __init__(self, core):
            self.core = core

        # By default, all button presses do nothing

        def up(self):
            '''The up button on the 4-way direction pad'''
            print("7,low")
            self.core.throttle(0.1,0,7,0)

        def down(self):
            '''The up button on the 4-way direction pad'''
            print("7,high")
            self.core.throttle(0.7,0,7,0)
        def left(self):
            '''The up button on the 4-way direction pad'''

        def right(self):
            '''The up button on the 4-way direction pad'''

        def btn_a(self):
            '''The A button'''
            print("8, low")
            self.core.throttle(0.1,0,8,0)

        def btn_b(self):
            '''The B button'''
            print("8,igh")
            self.core.throttle(0.7,0,8,0)

        def btn_x(self):
            '''The X button'''
            print("9,low")
            self.core.throttle(0.1,0,9,0)
        def btn_y(self):
            '''The Y button'''
            print("9,high")
            self.core.throttle(0.7,0,9,0)
