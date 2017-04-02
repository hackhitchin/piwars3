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
* **now ...**		Change lights immediately instead of waiting for sequence to finish
* **wait ...**	Don't return from lights.send() until previous sequence has finished
* **pulse r g b**	Lights pulse on and off in colour given
* **on r g b**	Steady light in colour given
* **twinkle**		Random twinkling
* **police**		Attempt to imitate an emergency vehicle's lights
* **hue**		Slowly move all LEDs through H element of HSV colour space
* **strobe**		Repeatedly strobe 1-10 LEDs (random) a random colour each
* **data x [y z ...]	Send data to the current light effect
* **off**		All lights off
* **die**		Kill the daemon

Data:
* **pulse** accepts either 1 integer, a new speed (default = 100, lower numbers are faster), 3 integers (a new RGB value) or 4 integers (R G B Speed)
* **on** accepts a float between 0.0 and 1.0, which modifies the brightness of the specified RGB value

Examples:
* **pulse 255 0 0**		Pulse red
* **pulse 0 255 0**		Switch to pulsing green when the red sequence finishes
* **now pulse 0 0 255**		Switch to pulsing blue immediately
* **data 50** 			Pulse faster
* **data 255 255 0 150**	Pulse slower and change to yellow
* **wait on 0 255 0**		Steady green when the blue sequence finishes. send() won't return until this happens
* **data 0.5**			Reduce brightness
* **off**			Lights off
