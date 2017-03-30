#!/usr/bin/python

# Run as ./camtest
# Outputs a view of the line the camera can see, along with the distance
# from the centre of the line to the middle of the frame, and the
# "straightness" of the line ahead

import picamera
import sys
from collections import Counter

class Camdata(object):
	'''A class to receive the binary data from the camera module and
	process it into data about a line'''
	def __init__(self, x, y):
		self.data = []
		self.x = x
		self.y = y

	def __weighted(self, l):
		'''Weighted average of list'''
		count = 0
		sum = 0
		for (val, num) in l:
			count += num
			sum += val*num
		return sum/count

	def write(self, data):
		'''Accept data from picamera in binary format'''
		# Get all data (YUV)
		ydata = [ ord(byte) for byte in data ]

		# Throw away UV, leaving just Y (luminance)
		self.data = ydata[:self.x*self.y]

	def process(self):
		'''Turn the data into something useful'''
		counts = Counter(self.data)
		ci = list(counts.iteritems())
		low = ci[:6]
		high = ci[-6:]
		self.lower = self.__weighted(low)
		self.higher = self.__weighted(high)
		self.mid = (self.lower + self.higher) / 2

		# 0 = black, 1 = white
		self.binary = map(lambda x: int(x>self.mid), self.data)

		self.midwidth = []

		# Data starts at top left, moving right then down
		for y in range(self.y):
			linestart = y*self.x
			linedata = self.binary[linestart:linestart+self.x]
			linedata.extend([2,2])	# Simplifies things

			start = -1
			longeststart = -1
			longest = 0

			for pos, val in enumerate(linedata):
				if pos>self.x:
					continue
				# 0 = black, 1 = white, 2 = run-out (treat as white)
				if val:		# White
					# Ignore a single-pixel break in the line data
					if linedata[pos+1]:
						# Next pixel is white
						if start>=0:
							len = pos-start
							if len>longest:
								longest = len
								longeststart = start
							start = -1
				else:		# Black
					if start<0:
						start = pos

			midpoint = longeststart + longest/2

			self.midwidth.append((midpoint,longest))

		self.straightness = 0
		self.midpoint = -1
		self.distfromcentre = 0

		# What if last row of data doesn't have anything on it?
		for y in range(self.y-1, 0, -1):
			(mid,width) = self.midwidth[y]
			if mid >= 0:
				break
		else:
			# Nothing has anything on it, bail out
			return

		if y < (self.y-1):
			for i in range(y, self.y):
				self.midwidth[i] = self.midwidth[y]

		(midpoint,width) = self.midwidth[self.y - 1]
		self.midpoint = midpoint
		if midpoint >= 0:
			self.distfromcentre = self.x/2 - midpoint

		for mid, width in reversed(self.midwidth):
			# Iterate backwards through midpoints from bottom
			if mid-2 <= midpoint <= mid+2:
				self.straightness+=1
			else:
				break


	def out(self):
		'''Display the data'''
		y = 0
		x = 0
		print "Image data"

		for v in self.binary:
			if v:
				# White
				sys.stdout.write(' ')
			else:
				sys.stdout.write('#')
			x += 1
			if x>=self.x:
				sys.stdout.write('| ')
				print self.midwidth[y]
				y += 1
				if y>=self.y:
					print x,y
					break
				x = 0

		print "Distance from centre:", self.distfromcentre
		print "Straightness: ", self.straightness



cam = picamera.PiCamera()
cam.resolution = (64,64)
cam.framerate = 6

while True:
	output = Camdata(64,64)
	# cam.capture('out.jpg', 'jpeg')
	cam.capture(output, 'yuv')

	output.process()
	output.out()
