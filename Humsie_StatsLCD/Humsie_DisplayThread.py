#!/usr/bin/python

import threading;
from Adafruit_CharLCD import Adafruit_CharLCD
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
from time import sleep


class Humsie_DisplayThread (threading.Thread):

    intCurIndex = -1;
    arrPages = { };
    bRunning = False;
    LCD = False;
    intTimePerPage = 3;
    bUpdatingDisplay = False;
    intColor = -1;
    arrColors = [];

    def __init__(self, threadID, name, counter, GPIO=False):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        if GPIO == False:
            self.LCD = Adafruit_CharLCDPlate();
            self.arrColors = [self.LCD.RED,self.LCD.GREEN,self.LCD.BLUE,self.LCD.YELLOW,self.LCD.TEAL,self.LCD.VIOLET,self.LCD.WHITE,self.LCD.ON ]
            self.intColor = 0;
        else:
            self.LCD = Adafruit_CharLCD(25, 24, [23, 17, 27, 22], GPIO);

    def start(self):
        self.bRunning = True;
        threading.Thread.start(self)

    def run(self):
        while self.bRunning == True:
            self.intCurIndex += 1;
            if self.arrPages.has_key(self.intCurIndex) == False:
                self.intCurIndex = 0;
            
            self.displayPage(self.intCurIndex);
            sleep(self.intTimePerPage);
            if self.intColor >= 0:
               self.intColor += 1;
               if self.intColor >= len(self.arrColors):
                 self.intColor = 0;
               self.LCD.backlight(self.arrColors[self.intColor]);

        return

    def gotoPage(self, index):
        self.intCurIndex = index;
        if self.arrPages.has_key(self.intCurIndex) == False:
            self.intCurIndex = 0;
        
        self.displayPage(index)

    def displayPage(self, index):
	if self.bUpdatingDisplay == False:
	    if self.arrPages.has_key(index) != False:
                self.bUpdatingDisplay = True
                self.LCD.clear()
                self.LCD.message(self.arrPages[index])
                self.bUpdatingDisplay = False
       	return;       

    def setTimePerPage(self, seconds=3):
        self.intTimePerPage = seconds
        return self.intTimePerPage

    def stop(self):
        self.LCD.clear();
        self.bRunning = False
        return

    def stopped(self):
        return self.bRunning
        
    def setPage(self, index, line):
        if self.arrPages[index] != line:
            self.arrPages[index] = line;
            if self.intCurIndex == index:
                self.displayPage(self.intCurIndex);
        return;

    def registerPage(self, content = ''):
        length = len(self.arrPages);
        self.arrPages[length] = content;
        return length;
