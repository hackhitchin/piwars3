Light daemon for PiWars
=======================

Separates out the flashy blinky lights from everything else, so it can run
at a lower priority

Includes code from Adafruit's DotStar module for Python on Raspberry Pi

Run 'make' to build the dotstar.so library

To use:

Run lightd.py

include lights.py

lights.send(<command>)


Commands:
	now ...		Change lights immediately instead of waiting for sequence to finish
	wait ...	Don't return from lights.send() until previous sequence has finished
	pulse r g b	Lights pulse on and off in colour given
	on r g b	Steady light in colour given
	twinkle		Random twinkling
	police		Attempt to imitate an emergency vehicle's lights
	off		All lights off


Examples:
	pulse 255 0 0		Pulse red
	pulse 0 255 0		Switch to pulsing green when the red sequence finishes
	now pulse 0 0 255	Switch to pulsing blue immediately
	wait on	0 255 0		Steady green when the blue sequence finishes.
				send() won't return until this happens
	off			Lights off
