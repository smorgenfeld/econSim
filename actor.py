# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 14:11:48 2019

@author: Spencer Morgenfeld
"""

class actor:
    
    def __init__(self, g):
        self.gold = g;
        self.inv = [0, 0, 0];
        self.type = 0;
        self.dead = False;
        
        # Production values without tools
        self.nTP = [2, 1, 0, 0];
        # Production values while consuming one tool
        self.yTP = [4, 2, 1, 0];
        
    def beforeTrades(self):
        self.inv[0] -= 1;
        # farmer
        if (self.type == 0):
            if (self.inv[1] > 0):
                self.inv[1] -= 1;
                self.inv[0] += self.yTP[0];
            else:
                self.inv[0] += self.nTP[0];
        # toolmaker
        elif (self.type == 1):
            if (self.inv[1] > 0):
                self.inv[1] += self.yTP[1];
                self.inv[1] -= 1;
            else:
                self.inv[1] += self.nTP[1];
        
        # jeweler
        elif (self.type == 2):
            if (self.inv[1] > 0):
                self.inv[2] += self.yTP[2];
                self.inv[1] -= 1;      
            else:
                self.inv[2] += self.nTP[2];
        
        # sink
        elif (self.type == 3):
            self.inv[2] -= 1;
            
    def afterTrades(self):
        if (self.inv[0] < 0):
            #starve
            self.dead = True;
        elif (self.inv[2] < 0 and self.type == 3):
            self.type = 0;
        elif (self.type == 0 and self.gold > 10):
            self.type = 1;
        elif (self.type == 1 and self.gold > 20):
            self.type = 2;
        elif (self.gold > 30):
            self.type = 3;
            
    def getValue(self, t, lastPrices):
        # Always buy food if you're going to starve
        if (t == 0 and self.inv[0] < 1):
            return self.gold;
        # Always buy tools if it's worth it, based on last price of produced good
        if (t == 1 and self.inv[1] < 1 and self.type != 3):
            return min(self.gold, (self.yTP[self.type] - self.nTP[self.type]) * lastPrices[self.type]);
        # Always buy luxery goods if you're a sink
        if (t == 2 and self.inv[2] < 1):
            return self.gold;
        #print("Shouldn't get here (t value of " + str(t) + ")");
        return 0;