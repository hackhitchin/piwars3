
import math
import colorsys
import random


class Effect(object):
	def __init__(self):
		self.frame = 0
		self.nextobj = None
		self.okfunc = None
		self.changenow = False
		self.reset()

	def reset(self):
		self.frame = 0

	def values(self):
		return [(0,0,0)] * 60

	def _nextobj(self, change = True):
		if self.nextobj and (change or self.changenow):
			if self.okfunc:
				try:
					self.okfunc()
				except IOError as e:
					print 'okfunc() error:', e
			return self.nextobj
		else:
			return None

	def nextframe(self):
		return self._nextobj()

	def setnext(self, object):
		self.nextobj = object

	def setok(self, function):
		self.okfunc = function

	def setnow(self):
		self.changenow = True

	def setdata(self, data):
		'''Ignore the data'''

	def _getint(self, data):
		'''Return the first int in the list, or 0 if none'''
		try:
			val = int(data.pop(0))
		except:
			val = 0
		return val

	def _getfloat(self, data):
		'''Return the first float in the list, or 0 if none'''
		try:
			val = float(data.pop(0))
		except:
			val = 0.0
		return val


class Pulse(Effect):
	def __init__(self, r,g,b):
		super(Pulse,self).__init__()	
		self.r = r
		self.g = g
		self.b = b

	def reset(self):
		super(Pulse, self).reset()
		self.speed = 100
		self.targetspeed = 100

	def values(self):
		multiple = (1-math.cos(2*math.pi*self.frame/self.speed))/2
		return [(int(self.r*multiple), int(self.g*multiple), int(self.b*multiple))] * 60

	def nextframe(self):
		if self.speed != self.targetspeed:
			# Recalculate frame number for new speed so there's no sudden jump in light level
			self.frame = int(self.frame*float(self.targetspeed)/float(self.speed))
			self.speed = self.targetspeed
		self.frame += 1
		return self._nextobj((self.frame % self.speed) == 0)

	def setdata(self, data):
		'''Set data
		1 value = speed
		3 values = r,g,b
		4 values = r,g,b,speed'''
		if len(data) == 1:
			self.targetspeed = self._getint(data)
			if self.targetspeed == 0:
				self.targetspeed = 100	# Avoid /0 error on bad data
		elif len(data) >= 3:
			self.r = self._getint(data)
			self.g = self._getint(data)
			self.b = self._getint(data)
			if len(data):
				# If more data, assume it's a speed
				self.setdata(data)




class Hue(Effect):
	def values(self):
		self.frame += 1
		hue = (self.frame%100)/100.0
		(r,g,b) = colorsys.hsv_to_rgb(hue,1,1)
		return [(int(r*255), int(g*255), int(b*255))] * 60


class On(Effect):
	def __init__(self, r,g,b):
		super(On,self).__init__()	
		self.r = r
		self.g = g
		self.b = b

	def reset(self):
		super(On, self).reset()
		self.multiple = 1

	def values(self):
		return [(int(self.r*self.multiple), int(self.g*self.multiple), int(self.b*self.multiple))] * 60

	def setdata(self, data):
		self.multiple = self._getfloat(data)


class Twinkle(Effect):
	def reset(self):
		self.frame = 0
		self.rgb1 = [[0,0,0]] * 60
		self.rgb2 = [[0,0,0]] * 60
		self.startframe = [0] * 60
		self.endframe = [1] * 60

	def values(self):
		self.frame += 1
		for i in range(60):
			if(self.frame >= self.endframe[i]):
				self.startframe[i] = self.frame
				self.endframe[i] = self.frame + random.randint(25,50)
				self.rgb1[i] = self.rgb2[i]
				self.rgb2[i] = [random.random(), random.random(), random.random()]

		leds = []
		for led in range(60):
			cols1 = self.rgb1[led]
			cols2 = self.rgb2[led]
			avg = (0.0 + self.frame - self.startframe[led])/(self.endframe[led] - self.startframe[led])
			bright = (math.cos(2*math.pi*avg)+1)/2
			r = int(255*bright*(cols2[0]*avg + cols1[0]*(1-avg)))
			g = int(255*bright*(cols2[1]*avg + cols1[1]*(1-avg)))
			b = int(255*bright*(cols2[2]*avg + cols1[2]*(1-avg)))
			leds.append((r,g,b))
		return leds


class Police(Effect):
	'''Emergency vehicle effect. Blue strobes on top, plus flashing headlights'''

	LSEQ = [ 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 ]
	RSEQ = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1 ]

	def reset(self):
		self.frame = 0

	def values(self):
		self.frame = (self.frame + 1) % 16

		leds = [(0,0,0)] * 60

		if self.LSEQ[self.frame]:
			leds[10] = (0,0,255)
			leds[11] = (0,0,255)
		if self.RSEQ[self.frame]:
			leds[50] = (0,0,255)
			leds[49] = (0,0,255)

		headlight = self.frame / 8
		fade = self.frame % 8

		if(fade==7):
			light = (127,127, 100)
		else:
			light = (255,255,200)

		if headlight:
			leds[25] = light
		else:
			leds[35] = light

		return leds

class Strobe(Effect):
	'''Randomly strobe 1-10 LEDs'''

	def reset(self):
		self.leds = []
		self.colours = []
		self.frame = 0

	def values(self):
		self.frame += 1
		if self.frame >3:
			self.reset()
			for i in range(random.randint(1,10)):
				hue = random.random()
				(r,g,b) = colorsys.hsv_to_rgb(hue,1,1)
				self.colours.append((int(r*255), int(g*255), int(b*255)))
				self.leds.append(random.randint(0,59))

		vals = [(0,0,0)] * 60

		if self.frame % 2:
			for i, led in enumerate(self.leds):
				vals[led] = self.colours[i]

		return vals



class Off(Effect):
	'''Turns all the LEDs off'''

