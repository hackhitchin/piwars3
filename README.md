# Piwars 3.0
This is the latest incarnation for Piwars 3.0, by Hitchin Hackspace.

## Install Instructions
'''
cd ~  
mkdir Projects  
cd Projects  
git clone https://github.com/hackhitchin/piwars3.git  
sudo apt-get install python-cwiid  
'''

## Pre-requisites
https://github.com/johnbryanmoore/VL53L0X_rasp_python

https://github.com/metachris/RPIO	('v2' branch)


Needs to be run as root and set PYTHONPATH to find the VL53L0X library, eg.

    sudo PYTHONPATH=/home/pi/VL53L0X_rasp_python/python ./lidar_test.py

## PID ##
PID class found at 
https://github.com/ivmech/ivPID

Linked from 
http://code.activestate.com/recipes/577231-discrete-pid-controller/
