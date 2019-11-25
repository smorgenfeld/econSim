# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 14:11:48 2019

@author: Spencer Morgenfeld
"""
import random as r;
class actor:
    
    def __init__(self, g, t = 0):
        self.gold = g;
        self.inv = [0, 0, 0];
        self.type = t;
        self.dead = False;
        
        # Production values without tools
        self.nTP = [2, 1, 0, 0];
        # Production values while consuming one tool
        self.yTP = [6, 3, 1, 0];
        
        self.lastUsedTool = False;
        
        self.lastIncome = 0;
        self.lastTax = 0;
        
    def beforeTrades(self, step):
        # farmer
        if (self.type == 0):
            if (self.inv[1] > 0):
                self.inv[1] -= 1;
                self.inv[0] += self.yTP[0];
                self.lastUsedTool = True;
            else:
                self.inv[0] += int(self.nTP[0])# / r.randint(1, 2));
                self.lastUsedTool = False;
        # toolmaker
        elif (self.type == 1):
            if (self.inv[1] > 0):
                self.inv[1] = min(self.yTP[1] + self.inv[1], self.yTP[1]);
                self.inv[1] -= 1;
                self.lastUsedTool = True;
            else:
                self.inv[1] = self.nTP[1];
                self.lastUsedTool = False;
        
        # jeweler
        elif (self.type == 2):
            if (self.inv[1] > 0):
                self.inv[2] = min(self.yTP[2] + self.inv[2], 3);
                self.inv[1] -= 1;    
                self.lastUsedTool = True;
            else:
                self.inv[1] = self.nTP[2];
                self.lastUsedTool = False;
        
        # sink
        elif (self.type == 3):
            self.inv[2] -= 1;
            self.lastUsedTool = False;
        self.inv[0] -= 1;
       
            
    def afterTrades(self, lastPrice, movements, totGold, totPop):
        mod = lastPrice[0] * self.nTP[0];
        if (self.lastUsedTool):
            mod = lastPrice[0] * self.yTP[0];
        if (self.inv[0] < 0):
            #starve
            #self.dead = True;
            if (self.type != 0 and self.type != 3):
                self.type -= 1;
                movements[0][-1] += 1;
        #elif (self.inv[2] < 0 and self.type == 3):
            #movements[1][-1] += 1;
            #self.type = 0;
        elif (self.type == 0 and self.gold > lastPrice[0] * 3 and (lastPrice[1] * (self.yTP[1] - 1) >= mod) and r.randint(0,5) == 1):
            movements[2][-1] += 1;
            self.type = 1;
        elif (self.type == 1 and self.gold > lastPrice[0] * 2 and lastPrice[2] * self.yTP[2] >= lastPrice[1] * (self.yTP[1] - 1) and r.randint(0,5)==1):
            movements[3][-1] += 1;
            self.type = 2;
        #elif (self.type != 3 and self.gold > lastPrice[0] * 3 + lastPrice[2] * 3 and self.gold > totGold/totPop * 10 and r.randint(0,0)==0):
        #    movements[4][-1] += 1;
        #    self.type = 3;
        
        #elif (self.type == 3 and self.gold < totGold/totPop * 5):
         #   self.type = 2;
        
        # make farmers lose all their unsold/eaten crops each round
        if (self.type == 0):
            self.inv[0] = 0;
        # people consume all luxery goods each round
        self.inv[2] = 0;
            
    def getValue(self, t, lastPrices, incomeTax):
        toSpend = self.gold;
        if (incomeTax):
            toSpend = max(0, toSpend - self.lastTax)
        # Always buy food if you're going to starve
        if (t == 0 and self.inv[0] < 1):
            return toSpend;
        # Always buy tools if it's worth it, based on last price of produced good
        if (t == 1 and self.inv[1] < 1 and self.type != 3):
            return min(toSpend, (self.yTP[self.type] - self.nTP[self.type]) * lastPrices[self.type]);
        # Always buy luxury goods if you're a sink
        if (t == 2 and self.inv[2] < 1):
            return toSpend;
        # Otherwise, try to buy luxery goods if you can afford food for the next couple rounds
        elif (t != 2 and toSpend > 3 * lastPrices[0]):
            return int(min(toSpend, lastPrices[2]));
        #print("Shouldn't get here (t value of " + str(t) + ")");
        return 0;
    
    def pay(self, amount):
        self.gold += amount;
        self.lastIncome += amount;