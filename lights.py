
# Lights for the robot
#
# Interfaces with independent (low priority) daemon which controls the lights

import socket

socketfile = '/tmp/light_sock'

def send(command):
	try:
		sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		sock.connect(socketfile)
		sock.settimeout(2)	# 2-second timeout on operations
		sock.sendall(command)
		data = sock.recv(1024)
		sock.close()
	except IOError as e:
		print "Command failed", e

