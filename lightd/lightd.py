#!/usr/bin/python

import socket
import os
import sys

import time
from dotstar import Adafruit_DotStar
import atexit
import thread

import effect

# Low priority
os.nice(10)

# Define pixel strip
numpixels = 60 # Number of LEDs in strip
strip   = Adafruit_DotStar(numpixels)           # Use SPI (pins 10=MOSI, 11=SCLK)

strip.begin()           # Initialize pins for output
strip.setBrightness(255) # FULL POWER!!!

# Kill the lights on exit
def lightsout():
	strip.setBrightness(0)
	strip.show()

atexit.register(lightsout)



obj = effect.Off()

def ledthread():
	global obj

	while True:
		leds = obj.values()
		for led, (r,g,b) in enumerate(leds):
			strip.setPixelColor(led, g,r,b)

		strip.show()
		time.sleep(0.02)	# 50fps
		nextobj = obj.nextframe()
		if nextobj:
			obj = nextobj
			obj.reset()


thread.start_new_thread(ledthread,())


listen_addr = '/tmp/light_sock'

try:
	os.unlink(listen_addr)
except OSError:
	if os.path.exists(listen_addr):
		raise

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

sock.bind(listen_addr)

sock.listen(1)

while True:
	try:
		(connection, client_addr) = sock.accept()
	
		okfunc = lambda : connection.sendall('OK')
	
		while True:
			data = connection.recv(1024)
			wait = False
			now = False
			if data:
				print data
				try:
					vals = data.split()
					cmd = vals.pop(0).lower()
					if cmd == 'ping':
						connection.sendall('OK')
						continue
	
					if cmd == 'wait':
						wait = True
						cmd = vals.pop(0)
					if cmd == 'now':
						wait = False		# "wait now" doesn't make sense
						cmd = vals.pop(0)
						now = True
					if cmd == 'pulse':
						pulse = effect.Pulse(int(vals.pop(0)), int(vals.pop(0)), int(vals.pop(0)))
						if(wait):
							obj.setok(okfunc)
						obj.setnext(pulse)
					if cmd == 'on':
						wait = False		# No delay on this finishing
						obj.setnext(effect.On(int(vals.pop(0)), int(vals.pop(0)), int(vals.pop(0))))
					if cmd == 'twinkle':
						wait = False		# No delay on this finishing
						obj.setnext(effect.Twinkle())		
					if cmd == 'police':
						wait = False		# No delay on this finishing
						obj.setnext(effect.Police())		
					if cmd == 'off':
						wait = False		# No delay on this finishing
						obj.setnext(effect.Off())		
	
					if now:
						obj.setnow()

					if not wait:
						okfunc()
				except IndexError:
					connection.sendall('Error')
					print 'Wrong number of arguments'
				except ValueError as e:
					connection.sendall('Error')
					print 'Bad argument', e
			else:
				connection.close()
				break
	except IOError as e:
		print 'Error: e'
		try:
			connection.close()
		except IOError as e:
			print 'e'	
