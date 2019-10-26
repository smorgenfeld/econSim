# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 14:02:26 2019

@author: Spencer Morgenfeld
"""
import actor, good, random as r, matplotlib.pyplot as plt, numpy as np;

def main():
    actors = [];
    for i in range(45):
        actors.append(actor.actor(5));
    for i in range(5):
        actors.append(actor.actor(15));
    
    lastPrices = [1,1,1];
    curPrices = [1,1,1];
    allPrices = [[],[],[]]
    for i in range(100):
        for a in actors:
            a.beforeTrades();
        
        # Run auctions for food, tools and luxery goods, in that order
        prodCosts = [];
        buyerValues = [];
        
        for j in range(3):
            prodCosts.clear();
            buyerValues.clear();
            # Determine production costs and buyer values
            for a in actors:
                # food auction
                if (j == 0):
                    if (a.type == 0):
                        # base food cost roughly on last round's food cost, plus some random variation
                        # (farmers should never starve)
                        prodCosts.extend([[max(lastPrices[0] + r.randint(-2, 2), 1), a]] * max(a.inv[0] - 1, 1));
                    else:
                        buyerValues.append([a.getValue(j, lastPrices), a]);
                # tool auction
                elif (j == 1):
                    if (a.type == 1):
                        # Set tool production cost to be based on last round food price, plus 
                        # some random markup/down based on previous sell price
                        numToSell = max(a.inv[1] - 1, 1);
                        if (numToSell != 0):
                            prodCost = max((lastPrices[0]) / numToSell, 0);
                            prodCosts.extend([[randint(prodCost, lastPrices[1] + 5), a]] * numToSell);
                    else:
                        buyerValues.append([a.getValue(j, lastPrices), a]);
                # luxery auction
                else: # j == 2
                    if (a.type == 2):
                        # Set luxery production cost to be based on last round food and tool price,
                        # plus some random markup/down based on last sell price
                        numToSell = max(a.inv[2] - 1, 0);
                        if (numToSell != 0):
                            prodCost = max((lastPrices[0] + lastPrices[1]) / numToSell, 1);
                            prodCosts.extend([[randint(prodCost, lastPrices[2] + 5), a]] * numToSell);
                    else:
                        buyerValues.append([a.getValue(j, lastPrices), a]);
            if (len(buyerValues) == 0 or len(prodCosts) == 0):
                break;
            # Arrange production costs from low to high
            bubble_sort(prodCosts);
            bubble_sort(buyerValues);
            #print(prodCosts);
            # equate costs & values list lengths by removing lowest buyer bids
            # or highest seller bids
            print(str(len(buyerValues)) + " " + str(len(prodCosts)))
            if (len(prodCosts) < len(buyerValues)):
                buyerValues = buyerValues[len(buyerValues) - len(prodCosts):];
            elif (len(prodCosts) > len(buyerValues)):
                prodCosts = prodCosts[:len(buyerValues)];
            #print(prodCosts);
            # Arrange buyer bids from high to low
            buyerValues.reverse();
            
            printl(buyerValues);
            printl(prodCosts);
            
            # Get price for good j (use buyervalues to set price for both buyers
            # and sellers, to prevent incentives from adding/removing gold from economy)
            k = 0;
            for k in range(len(prodCosts) - 1):
                if (prodCosts[k][0] <= buyerValues[k][0] and prodCosts[k + 1][0] > buyerValues[k + 1][0]):
                    break;
            curPrices[j] = buyerValues[k][0];
            allPrices[j].append(curPrices[j]);
            
            # Complete trades
            for b in range(len(buyerValues)):
                if (buyerValues[b][0] >= curPrices[j] and prodCosts[b][0] <= curPrices[j]):
                    buyerValues[b][1].gold -= curPrices[j];
                    buyerValues[b][1].inv[j] += 1;
                    assert(buyerValues[b][1].gold >= 0);
                    
                    prodCosts[b][1].gold += curPrices[j];
                    prodCosts[b][1].inv[j] -= 1;
                    assert(prodCosts[b][1].inv[j] >= 0);
        
        for a in actors:
            a.afterTrades();
            if (a.dead):
                actors.remove(a);
                print("d");
                del a;
        lastPrices = curPrices;
        
        print(lastPrices);
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
        print(tGold);
        print(pop);
        print("Farmer gold: " + str(fGold));
        print("Smith gold: " + str(sGold));
        print("Jeweler gold: " + str(jGold));
        print("Noble gold: " + str(nGold));
        print()
    plt.plot(allPrices[0]);
    plt.plot(allPrices[1])
    plt.plot(allPrices[2])
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
        