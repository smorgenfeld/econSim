# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 14:02:26 2019

@author: Spencer Morgenfeld
"""
import actor, good, random as r;

def main():
    actors = [];
    for i in range(45):
        actors.append(actor.actor(5));
    for i in range(5):
        actors.append(actor.actor(15));
    
    lastPrices = [1,1,1];
    curPrices = [1,1,1];
    for i in range(10):
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
            # equate costs & values list lengths by removing lowest buyer bids
            # or highest seller bids
            if (len(prodCosts) < len(buyerValues)):
                buyerValues = buyerValues[len(buyerValues) - len(prodCosts) - 1:];
            elif (len(prodCosts) > len(buyerValues)):
                prodCosts = prodCosts[:len(buyerValues)];
            # Arrange buyer bids from high to low
            buyerValues.reverse();
            
            # Get price for good j (use buyervalues to set price for both buyers
            # and sellers, to prevent incentives from adding/removing gold from economy)
            k = 0;
            print(str(len(buyerValues)) + " " + str(len(prodCosts)))
            for k in range(len(prodCosts) - 1):
                if (prodCosts[k][0] <= buyerValues[k][0] and prodCosts[k + 1][0] > buyerValues[k + 1][0]):
                    break;
            curPrices[j] = buyerValues[k][0];
            
            # Complete trades
            for b in buyerValues:
                if (b[0] >= curPrices[j]):
                    b[1].gold -= curPrices[j];
                    assert(b[1].gold >= 0);
                    b[1].inv[j] += 1;
            for s in prodCosts:
                if (s[0] <= curPrices[j]):
                    s[1].gold += curPrices[j];
                    s[1].inv[j] -= 1;
                    assert(s[1].inv[j] >= 0);
        
        for a in actors:
            a.afterTrades();
            if (a.dead):
                actors.remove(a);
                print("d");
                del a;
        lastPrices = curPrices;
        print(lastPrices);
        tGold = 0;
        for kek in actors:
            tGold += kek.gold;
        print(tGold);

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

                
main();
        