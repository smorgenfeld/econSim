# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 14:02:26 2019

@author: Spencer Morgenfeld
"""
import actor, random as r, matplotlib.pyplot as plt, numpy as np;
from tqdm import tqdm

def main(incomeTax = True, toTax = [True, True, True], initITP = [0, 0.25, 0.9], incomeTaxThresholds = [0.33, 0.66], long = False, name = ""):
    actors = [];
    for i in range(95):
        actors.append(actor.actor(100));
    for i in range(5):
        actors.append(actor.actor(100, 3));
    totGold = 0;
    totPop = 0;
    for a in actors:
        totGold += a.gold;
        totPop += 1;
    
    # Init variables
    lastPrices = [1,2,3];
    curPrices = [1,2,3];
    allPrices = [[],[],[]]
    allPops = [[],[],[],[]]
    allSold = [[],[],[]]
    allProduced = [[],[],[]]
    allWanted = [[],[],[]]
    movements = [[],[],[],[],[]]
    taxRevs = []
    nobleSpending = []
    totGoldarray = [[],[],[],[],[]]
    gdp = [];
    ppp = []; # gdp/(# actors * price of food).  Guess it's kinda an adjusted gdp for 'inflation' (mostly adusts for actors eating money supply)
    cci = []; # consumer confidence index.  Measures proportion of actors willing to bid for luxury goods.
    tax = [0,0,0];
    
    # If incomeTax is true, then income taxes are used.  If false, then VAT tax is used.
    #incomeTax = True;
    
    # VAT tax variables
    #toTax = [False, False, True];
    taxes = [[],[],[]]
    
    # Income tax proportions (Income Tax Prop. - ITP)
    #initITP = [0, 0.25, 0.5];
    curITP = initITP.copy();
    #incomeTaxThresholds = [0.33, 0.66];
    
    actualTaxThresholds = [];
    for i in range(len(incomeTaxThresholds)):
        actualTaxThresholds.append([]);
    
    # Run loops (with fancy progress display)
    for i in tqdm(range(3000)):
        for a in actors:
            a.beforeTrades(i);
        
        # Run auctions for food, tools and luxury goods, in that order
        prodCosts = [];
        buyerValues = [];
        taxRevs.append(0);
        nobleSpending.append(0);
        gdp.append(0);
        cci.append(0);
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
                        buyerValues.append([a.getValue(j, lastPrices, incomeTax), a]);
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
                        buyerValues.append([a.getValue(j, lastPrices, incomeTax), a]);
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
                        numToBuy = 1;
                        if (a.type == 3):
                            numToBuy = int(max(1, a.gold/lastPrices[2] - 1));
                            buyerValues.extend([[a.getValue(j, lastPrices, incomeTax)/(numToBuy * r.randint(1, 2)), a]] * numToBuy);
                            cci[-1] += 1;
                        else:
                            luxVal = a.getValue(j, lastPrices, incomeTax);
                            if (luxVal > 0):
                                buyerValues.append([luxVal, a]);
                                cci[-1] += 1;
            cci[-1] = cci[-1]/totPop;
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
                # equate costs & values list lengths by removing lowest buyer bids
                # or highest seller bids
                if (len(prodCosts) < len(buyerValues)):
                    buyerValues = buyerValues[len(buyerValues) - len(prodCosts):];
                elif (len(prodCosts) > len(buyerValues)):
                    prodCosts = prodCosts[:len(buyerValues)];
                # Arrange buyer bids from high to low
                buyerValues.reverse();
                
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
                        # Only add food/luxury goods bought to GDP (as tools are always an intermediate product)
                        if (j != 1):
                            gdp[-1] += curPrices[j];
                        if (buyerValues[b][1].type == 3):
                            nobleSpending[-1] += curPrices[j];
                        buyerValues[b][1].inv[j] += 1;
                        assert(buyerValues[b][1].gold >= 0);
                        
                        prodCosts[b][1].pay(curPrices[j] / (1 + tax[j]));
                        taxRevs[-1] += curPrices[j] - curPrices[j] / (1 + tax[j]);
                        prodCosts[b][1].inv[j] -= 1;
                        assert(prodCosts[b][1].inv[j] >= 0);
                        totSold += 1;
                        #if (buyerValues[b][1].type != 3 and j == 2):
                        #    print(buyerValues[b][1].type)
                allSold[j].append(totSold);
        for n in range(5):
            movements[n].append(0);
        
        
        # Adjust tax rate to support noble spending
        if (not incomeTax):
            mod = 0.95;
            if (len(totGoldarray[0]) > 0 and totGoldarray[4][-1]/totGoldarray[0][-1] > 0.5):
                mod = 1.25;
            for taxType in range(len(tax)):
                if (taxRevs[-1] == 0 and toTax[taxType]):
                    tax[taxType] = 0.1;
                else:
                    tax[taxType] *= nobleSpending[-1]/max(mod * taxRevs[-1],1);
                tax[taxType] = min(tax[taxType], 1);
                taxes[taxType].append(tax[taxType]);
        else:
            # Calculate income thresholds
            incTax = [];
            for act in actors:
                incTax.append(act.lastIncome);
            incTax.sort();
            thresh = [incTax[int(len(incTax) * kek)] for kek in incomeTaxThresholds];
            for kekek in range(len(actualTaxThresholds)):
                actualTaxThresholds[kekek].append(thresh[kekek]);
            # Collect income tax
            for act in actors:
                taxBracket = 0;
                for th in thresh:
                    if (act.lastIncome > thresh[taxBracket]):
                        taxBracket += 1;
                    else:
                        break;
                newTax = min(int(act.lastIncome * curITP[taxBracket]), act.gold);
                taxRevs[-1] += newTax;
                act.gold -= newTax;
                act.lastTax = newTax
                act.lastIncome = 0;
            
            mod = 1 # as mod increases, nobles get less money from taxes
            if (len(totGoldarray[0]) > 0 and totGoldarray[4][-1]/totGoldarray[0][-1] > 0.5):
                mod = 1.25;
                #print("oh no")
            
            for taxType in range(len(curITP)):
                if (taxRevs[-1] == 0 and initITP[taxType] > 0 and nobleSpending[-1] != 0):
                    curITP[taxType] = initITP[taxType];
                else:
                    curITP[taxType] *= nobleSpending[-1]/max(mod * taxRevs[-1],1); #1.013 good for VAT
                if (taxType != 0):
                    taxes[taxType-1].append(curITP[taxType]);
        
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
        for n in range(4):
            allPops[n].append(pop[n])
        ppp.append(gdp[-1]/(totPop * max(1, lastPrices[0])))
    if (not long):
        plt.figure(1);
        lbs = ["Food", "Tools", "Luxury"];
        for i in range(3):
            plt.plot(ma(allPrices[i]), label = ("Price of " + lbs[i]));
        plt.legend();
        plt.ylim(ymin=0);
        plt.show();
        
        plt.figure(2);
        lbs = ["Food", "Tools", "Luxury"];
        for i in range(3):
            plt.plot(ma(allSold[i]), label = ("Units sold: " + lbs[i]));
        plt.legend();
        plt.ylim(ymin=0);
        plt.show();
        
        plt.figure(3);
        lbs = ["Farmers", "Smiths", "Jewelers", "Nobles"];
        for i in range(4):
            plt.plot(allPops[i],label = lbs[i]);
        plt.legend();
        plt.ylim(ymin=0);
        plt.show();
        
        plt.figure(4);
        plt.plot(ma(allProduced[0]), label = "Food Supply")
        plt.plot(ma(allWanted[0]), label = "Food Demand")
        plt.legend();
        plt.ylim(ymin=0);
        plt.show();
        
        plt.figure(5);
        plt.plot(ma(allProduced[1]), label = "Tool Supply")
        plt.plot(ma(allWanted[1]), label = "Tool Demand")
        plt.legend();
        plt.ylim(ymin=0);
        plt.show();
        
        plt.figure(6);
        plt.plot(allProduced[2], label = "Luxury Supply")
        plt.plot(allWanted[2], label = "Luxury Demand")
        plt.legend();
        plt.ylim(ymin=0);
        plt.show();
        
        
        
        plt.figure(8);
        plt.plot(ma(taxRevs), label = "Tax Revenue")
        plt.plot(ma(nobleSpending), label = "Noble Spending");
        plt.legend();
        plt.ylim(ymin=0);
        plt.show();
        
        plt.figure(9);
        lbs = ["Total Gold", "Farmer Gold", "Smith Gold", "Jeweler Gold", "Noble Gold"];
        for i in range(5):
            plt.plot(totGoldarray[i],label = lbs[i]);
        plt.legend();
        plt.ylim(ymin=0);
        plt.show();
        
        plt.figure(10);
        lbs = ["Avg. Farmer Gold", "Avg. Smith Gold", "Avg. Jeweler Gold", "Avg. Noble Gold"];
        for i in range(4):
            plt.plot(ma([totGoldarray[i+1][j]/max(1, allPops[i][j]) for j in range(len(allPops[i]))]),label = lbs[i]);
        plt.legend();
        plt.ylim(ymin=0);
        plt.show();
        
        plt.figure(13);
        if (not incomeTax):
            lbs = ["Food Tax", "Tool Tax", "Luxury Tax"];
            for i in range(3):
                plt.plot(ma(taxes[i]),label = lbs[i]);
        else:
            lbs = [str(kek) + "+ Tax" for kek in incomeTaxThresholds];
            for i in range(len(incomeTaxThresholds)):
                plt.plot(ma(taxes[i]),label = lbs[i]);
        plt.legend();
        plt.ylim(ymin=0);
        plt.show();
        
        if (incomeTax):
            plt.figure(14);
            lbs = [str(kek) + "+ Tax Threshold" for kek in incomeTaxThresholds];
            for i in range(len(actualTaxThresholds)):
                plt.plot(ma(actualTaxThresholds[i]),label = lbs[i]);
                plt.legend();
            plt.ylim(ymin=0);
            plt.show();
    
    plt.figure(11);
    if (not long):
        plt.plot(ma(gdp), label = "GDP")
    plt.plot(ma(gdp, 500), label = (name + " Very Smoothed GDP"))
    plt.legend();
    plt.ylim(ymin=0, ymax = 3000);
    plt.show();
    
    print(sum(gdp)/len(gdp))
    
    plt.figure(12);
    if (not long):
        plt.plot(ma(ppp), label = "PPP")
    plt.plot(ma(ppp, 500), label = (name + " Very Smoothed PPP"))
    plt.legend();
    plt.ylim(ymin=0, ymax = 2.25);
    plt.show();
    
    plt.figure(16);
    if (not long):
        plt.plot(ma(cci), label = "CCI")
    plt.plot(ma(cci, 500), label = (name + " Very Smoothed CCI"))
    plt.legend();
    plt.ylim(ymin=0, ymax = 1);
    plt.show();
    
    plt.figure(7);
    #lbs = ["Starved", "NEL", "F->S", "S->J", "J->N"];
    #for i in range(5):
    #    plt.plot(ma(movements[i]),label = lbs[i]);
    plt.plot(ma([movements[0][i] / (totPop - allPops[0][i]) for kek in range(len(movements[0]))], 500),label = (name + " Starvation Index"));
    plt.legend();
    plt.ylim(ymin=0, ymax=0.25);
    plt.show();
    
    plt.figure(15);
    plt.plot(ma([(allPops[1][i] + allPops[2][i] * 2) / totPop for i in range(len(allPops[1]))], 500), label = (name + " Job Quality Index"))
    plt.legend();
    plt.ylim(ymin=0, ymax = 1);
    plt.show();
    
    print(sum(ppp)/len(ppp))
    
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
    
def ma(a, n=25):
    # return moving average
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

#main();
main(long = True, incomeTax = True, initITP = [0, 0.95], incomeTaxThresholds=[0.8], name = "Just rich");
main(long = True, incomeTax = True, initITP = [0.1, 0.1, 0.1], name = "Equal");
main(long = True, incomeTax = True, initITP = [0, 0.2, 0.7], name = "Progressive");
main(long = True, incomeTax = True, initITP = [1, 0], incomeTaxThresholds=[0.5], name = "Tax the poor!");

main(long = True, incomeTax = False, toTax = [True, False, False], name = "Just Food");
main(long = True, incomeTax = False, toTax = [False, True, False], name = "Just Tools");
main(long = True, incomeTax = False, toTax = [False, False, True], name = "Just Lux")
    #main(long = True, incomeTax = True, initITP = [0.05, 0.15, 0.2], name = "Linear");
    #main(long = True, incomeTax = True, initITP = [0.05, 0.2, 0.5], name = "Exp");
    #main(long = True, incomeTax = True, initITP = [0, 0.25, 0.5], name = "Linear+");

        