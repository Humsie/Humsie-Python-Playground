#!/usr/bin/python

import RPi.GPIO as GPIO
import threading
from Humsie_CharLCD import Humsie_CharLCD
from Humsie_DisplayThread import Humsie_DisplayThread
from subprocess import * 
from time import sleep, strftime
from datetime import datetime
import signal
import traceback

#4  input 1
#18 input 2

def stopThreads():
    for thread in threading.enumerate():
        print thread.getName();
        if (thread.getName() != 'MainThread'):
            thread.stop();
    

def handler(signum, frame):
    print 'SigInt found, shutting down all threads'
    
    stopThreads();
    
    exit(0);

signal.signal(signal.SIGINT, handler)


#GPIO.setmode(GPIO.BCM);
#GPIO.setup(4, GPIO.IN, GPIO.PUD_UP);
#GPIO.setup(18, GPIO.IN, GPIO.PUD_UP);

Display = Humsie_DisplayThread(1, "RGBThread", 1)
#Display2 = Humsie_DisplayThread(1, "DisplayThread", 2, GPIO)

network_interfaces = { }

page_hostname = Display.registerPage('Hostname');
##Display2.registerPage('Hostname');
page_users = -1
page_loadavg = -1
page_mem = -1


def run_cmd(cmd):
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.communicate()[0]
        return output

def print_time_hostname():
        Display.setPage(page_hostname, "%s%s" % (datetime.now().strftime('%b %d  %H:%M:%S\n'), run_cmd("hostname") ) );
        #Display2.setPage(page_hostname, "%s%s" % (datetime.now().strftime('%b %d  %H:%M:%S\n'), run_cmd("hostname") ) );

def print_loadavg():
        global page_loadavg;
        if page_loadavg == -1: 
            page_loadavg = Display.registerPage();

        Display.setPage(page_loadavg, "Load avarages\n%s" % ( run_cmd("uptime | awk -F'load average: ' '{ print $2 }'") ) );
        #Display2.setPage(page_loadavg, "Load avarages\n%s" % ( run_cmd("uptime | awk -F'load average: ' '{ print $2 }'") ) );

def print_memory():
        global page_mem
        if page_mem == -1:
            page_mem = Display.registerPage();

        Display.setPage(page_mem, "Mem(MB) T U F S C B\n%s" % ( run_cmd("free -m | grep Mem | awk '{print $2,$3,$4,$5,$6,$7}'") ) );
        #Display2.setPage(page_mem, "Mem(MB) T U F S C B\n%s" % ( run_cmd("free -m | grep Mem | awk '{print $2,$3,$4,$5,$6,$7}'") ) );

def print_ip_lan_wlan():
        global network_interfaces;
	links = run_cmd("ip link show | grep 'state UP' | awk '{print $2}' | cut -d: -f1");
	links = links.splitlines();
	links.reverse();
	interface = links.pop();

	while interface:
                if (network_interfaces.has_key(interface) == False):
                    network_interfaces[interface] = Display.registerPage();
		cmd = "ip addr show %s | grep inet | awk '{print $2}' | cut -d/ -f1" % ( interface );
                Display.setPage(network_interfaces[interface], "interface: %s\n%s" % ( interface,  run_cmd("ip addr show %s | grep inet | awk '{print $2}' | cut -d/ -f1" % ( interface ) ) ) );
                #Display2.setPage(network_interfaces[interface], "interface: %s\n%s" % ( interface,  run_cmd("ip addr show %s | grep inet | awk '{print $2}' | cut -d/ -f1" % ( interface ) ) ) );
		if len(links) > 0:
			interface = links.pop();
		else:
			interface = 0;
        return ;


def print_users():
        global page_users;
        if page_users == -1: 
            page_users = Display.registerPage();
        
        users = run_cmd("who | awk '{print $1}'");
        users = users.splitlines();
        uusers = '';      
        for user in (list(set(users))):
            uusers += '%s(%d)' % (user, users.count(user) )
        
	Display.setPage(page_users, 'Online Users: %d\n%s' % ( len(users), uusers ));
	#Display2.setPage(page_users, 'Online Users: %d\n%s' % ( len(users), uusers ));


functions = {
 0 : print_time_hostname,
 1 : print_ip_lan_wlan,
 2 : print_users,
 3 : print_loadavg,
 4 : print_memory,
}

print_time_hostname();
print_ip_lan_wlan();

Display.start();
#Display2.start();
#Display2.gotoPage(2);
Display.LCD.backlight(Display.LCD.GREEN)

BackLightToggle = False;

try:
    while 1:
        for functionIndex in functions:
            functions[functionIndex]();

        if Display.LCD.buttonPressed(Display.LCD.SELECT):
            if BackLightToggle:
                BackLightToggle = False
            else:
                BackLightToggle = True

#        if BackLightToggle:
#            Display.LCD.backlight(Display.LCD.OFF)
#        else:
#            Display.LCD.backlight(Display.LCD.ON)

	sleep(1);
except Exception,e:
    stopThreads();
    print "Got exception while running functions"    
    print traceback.format_exc()
