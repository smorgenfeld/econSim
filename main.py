# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 14:02:26 2019

@author: Spencer Morgenfeld
"""
import actor, good, random as r, matplotlib.pyplot as plt, numpy as np;
from tqdm import tqdm

def main():
    actors = [];
    for i in range(100):
        actors.append(actor.actor(100));
    totGold = 0;
    totPop = 0;
    for a in actors:
        totGold += a.gold;
        totPop += 1;
    
    lastPrices = [1,2,3];
    curPrices = [1,1,1];
    allPrices = [[],[],[]]
    allPops = [[],[],[],[]]
    allSold = [[],[],[]]
    allProduced = [[],[],[]]
    allWanted = [[],[],[]]
    movements = [[],[],[],[],[]]
    taxRevs = []
    totGoldarray = [[],[],[],[],[]]
    tax = [0.1, 0.1, 0.1];
    for i in tqdm(range(1000)):
        for a in actors:
            a.beforeTrades(i);
        
        # Run auctions for food, tools and luxury goods, in that order
        prodCosts = [];
        buyerValues = [];
        taxRevs.append(0);
        for j in range(3):
            prodCosts.clear();
            buyerValues.clear();
            # Determine production costs and buyer values
            for a in actors:
                # food auction
                if (j == 0):
                    if (a.type == 0 and a.inv[0] > 0):
                        # base food cost roughly on last round's food cost, plus some random variation
                        # (farmers should never starve)
                        numSelling = max(a.inv[0], 0);
                        prodCost = max((lastPrices[0] + r.randint(-2,2) / numSelling * (1 + tax[0])), 1)
                        if (a.lastUsedTool):
                            prodCost = max(int(lastPrices[1] / numSelling * (1 + tax[0])), 1);
                        prodCosts.extend([[prodCost, a]] * numSelling);
                    else:
                        buyerValues.append([a.getValue(j, lastPrices), a]);
                # tool auction
                elif (j == 1):
                    if (a.type == 1):
                        # Set tool production cost to be based on last round food price, plus 
                        # some random markup/down based on previous sell price
                        numToSell = max(a.inv[1] - 1, 1);
                        if (numToSell != 0):
                            prodCost = int(max((lastPrices[0] + r.randint(-2,2)) / numToSell * (1 + tax[1]), 1));
                            prodCosts.extend([[randint(prodCost, lastPrices[1] + 5), a]] * numToSell);
                    else:
                        buyerValues.append([a.getValue(j, lastPrices), a]);
                # luxury auction
                else: # j == 2
                    if (a.type == 2):
                        # Set luxury production cost to be based on last round food and tool price,
                        # plus some random markup/down based on last sell price
                        numToSell = max(a.inv[2], 0);
                        if (numToSell != 0):
                            prodCost = int(max((lastPrices[0] + lastPrices[1] + r.randint(-2,2)) / numToSell * (1 + tax[2]), 1));
                            prodCosts.extend([[randint(prodCost, lastPrices[2] + 5), a]] * numToSell);
                    else:
                        buyerValues.append([a.getValue(j, lastPrices), a]);
            allProduced[j].append(len(prodCosts));
            allWanted[j].append(len(buyerValues));
            if (len(buyerValues) == 0 or len(prodCosts) == 0):
                
                if (len(prodCosts) > len(buyerValues)):
                    allPrices[j].append(curPrices[j] - 1);
                    curPrices[j] -= 1;
                else:
                    allPrices[j].append(curPrices[j] + 1)
                    curPrices[j] += 1;
                allSold[j].append(0);
            else:
                # Arrange production costs from low to high
                bubble_sort(prodCosts);
                bubble_sort(buyerValues);
                #print(prodCosts);
                # equate costs & values list lengths by removing lowest buyer bids
                # or highest seller bids
                #print(str(len(buyerValues)) + " " + str(len(prodCosts)))
                if (len(prodCosts) < len(buyerValues)):
                    buyerValues = buyerValues[len(buyerValues) - len(prodCosts):];
                elif (len(prodCosts) > len(buyerValues)):
                    prodCosts = prodCosts[:len(buyerValues)];
                #print(prodCosts);
                # Arrange buyer bids from high to low
                buyerValues.reverse();
                
                #printl(buyerValues);
                #printl(prodCosts);
                
                # Get price for good j (use buyervalues to set price for both buyers
                # and sellers, to prevent incentives from adding/removing gold from economy)
                k = 0;
                for k in range(len(prodCosts) - 1):
                    if (prodCosts[k][0] <= buyerValues[k][0] and prodCosts[k + 1][0] > buyerValues[k + 1][0]):
                        break;
                curPrices[j] = prodCosts[k][0];
                allPrices[j].append(curPrices[j]);
                
                # Complete trades
                totSold = 0;
                for b in range(len(buyerValues)):
                    if (buyerValues[b][0] >= curPrices[j] and prodCosts[b][0] <= curPrices[j]):
                        buyerValues[b][1].gold -= curPrices[j];
                        buyerValues[b][1].inv[j] += 1;
                        assert(buyerValues[b][1].gold >= 0);
                        
                        prodCosts[b][1].gold += curPrices[j] / (1 + tax[j]);
                        taxRevs[-1] += curPrices[j] - curPrices[j] / (1 + tax[j]);
                        prodCosts[b][1].inv[j] -= 1;
                        assert(prodCosts[b][1].inv[j] >= 0);
                        totSold += 1;
                allSold[j].append(totSold);
        for n in range(5):
            movements[n].append(0);
            
        # Distribute tax revenue (split equally among economy if no nobles)
        noblecount = 0;
        for a in actors:
            if (a.type == 3):
                noblecount += 1;
        if (noblecount == 0):
            for a in actors:
                a.gold += taxRevs[-1]/totPop;
        else:
            for a in actors:
                if (a.type == 3):
                    a.gold += taxRevs[-1]/noblecount;
                    
        for a in actors:  
            a.afterTrades(lastPrices, movements, totGold, totPop);
            if (a.dead):
                actors.remove(a);
                print("d");
                del a;
        lastPrices = curPrices;
        
        #print(lastPrices);
        tGold = 0;
        fGold = 0;
        sGold = 0;
        jGold = 0;
        nGold = 0;
        pop = [0,0,0,0]
        for kek in actors:
            tGold += kek.gold;
            pop[kek.type] += 1;
            if (kek.type == 0):
                fGold += kek.gold;
            elif (kek.type == 1):
                sGold += kek.gold;
            elif (kek.type == 2):
                jGold += kek.gold;
            elif (kek.type == 3):
                nGold += kek.gold;
        totGoldarray[0].append(tGold);
        totGoldarray[1].append(fGold);
        totGoldarray[2].append(sGold);
        totGoldarray[3].append(jGold);
        totGoldarray[4].append(nGold);
        #print(tGold);
        #print(pop);
        for n in range(4):
            allPops[n].append(pop[n])
        #print("Farmer gold: " + str(fGold));
        #print("Smith gold: " + str(sGold));
        #print("Jeweler gold: " + str(jGold));
        #print("Noble gold: " + str(nGold));
        #print()
    plt.figure(1);
    lbs = ["Food", "Tools", "Luxury"];
    for i in range(3):
        plt.plot(allPrices[i], label = ("Price of " + lbs[i]));
    plt.legend();
    plt.show();
    plt.figure(2);
    lbs = ["Food", "Tools", "Luxury"];
    for i in range(3):
        plt.plot(allSold[i], label = ("Units sold: " + lbs[i]));
    plt.legend();
    plt.show();
    plt.figure(3);
    lbs = ["Farmers", "Smiths", "Jewelers", "Nobles"];
    for i in range(4):
        plt.plot(allPops[i],label = lbs[i]);
    plt.legend();
    plt.show();
    
    plt.figure(4);
    plt.plot(allProduced[0], label = "Food Supply")
    plt.plot(allWanted[0], label = "Food Demand")
    plt.legend();
    plt.show();
    
    plt.figure(5);
    plt.plot(allProduced[1], label = "Tool Supply")
    plt.plot(allWanted[1], label = "Tool Demand")
    plt.legend();
    plt.show();
    
    plt.figure(6);
    plt.plot(allProduced[2], label = "Luxury Supply")
    plt.plot(allWanted[2], label = "Luxury Demand")
    plt.legend();
    plt.show();
    
    plt.figure(7);
    lbs = ["Starved", "NEL", "F->S", "S->J", "J->N"];
    for i in range(5):
        plt.plot(movements[i],label = lbs[i]);
    plt.legend();
    plt.show();
    
    plt.figure(8);
    plt.plot(taxRevs, label = "Tax Revenue")
    plt.legend();
    plt.show();
    
    plt.figure(9);
    lbs = ["Total Gold", "Farmer Gold", "Smith Gold", "Jeweler Gold", "Noble Gold"];
    for i in range(5):
        plt.plot(totGoldarray[i],label = lbs[i]);
    plt.legend();
    plt.show();
    
    plt.figure(10);
    lbs = ["Avg. Farmer Gold", "Avg. Smith Gold", "Avg. Jeweler Gold", "Avg. Noble Gold"];
    for i in range(3):
        plt.plot([totGoldarray[i+1][j]/max(1, allPops[i][j]) for j in range(len(allPops[i]))],label = lbs[i]);
    plt.legend();
    plt.show();
        

def bubble_sort(nums):
    # We set swapped to True so the loop looks runs at least once
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(nums) - 1):
            if nums[i][0] > nums[i + 1][0]:
                # Swap the elements
                nums[i], nums[i + 1] = nums[i + 1], nums[i]
                # Set the flag to True so we'll loop again
                swapped = True
def randint(a, b):
    if (a > b):
        return r.randint(b, a);
    return r.randint(a, b);

def printl(p):
    out = [];
    for g in p:
        out.append(g[0]);
    print(out);

                
main();
        