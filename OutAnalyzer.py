import csv
import numpy
import math
import datetime
import random

#This script to translate the out.csv file to a
#combination of things that should have been consolidated.

#Step 1. Translate it into a dictionary of waybill numbers that
#make sense to be grouped together


#This following section reads the data that are on the shipment level.
#Ignores the header
csvfile = open("shipmentLevelData.csv", 'r')
reader = csv.reader(csvfile, dialect=csv.excel_tab, delimiter=',')
next(reader, None)

dict = {}

#Reading the data for Parcel Rates
#This file is in the form of wt, zone
#This dictionary created is based on the string (wt-zone)
ParcelRatesFile = open("Parcel_Rates.csv", 'rU')
rateReader = csv.reader(ParcelRatesFile)
parcelRatesDict = {}
for row in rateReader:
    parcelRatesDict[row[0] + "-" + row[1]] = row[2]

#The following section reads the data corresponding to different parcel zones
#The file is in the format 3DZ, Zone from El Paso (799), Zone from ..
ParcelZonesFile = open("ParcelZones.csv", 'rU')
zoneReader = csv.reader(ParcelZonesFile)
zoneDict = {}
for row in zoneReader:
    zoneDict[row[0]] = row[1]

#The following section reads the data corresponding to the transportation data costs
#This file is in the format 3DZ ,State , Minimum Cost ,500,1000,2000,5000,10000, 10001+ lb,Transit Time
#Creates dictionary based on 3DZ
costFile = open("TransportationData.csv", 'rU')
costReader = csv.reader(costFile)
costDict = {}
for row in costReader:
    costDict[row[0]] = row

productsFile = open("products.csv", 'rU')
productReader = csv.reader(productsFile)
productList = next(productReader)


#This is the list to be written with the different distribution of numbers for different holding windows
#The first list contains the numbers that will be put in the file
analysisList = [["Holding Window", "Total Cost", "Consolidated Cost", "Savings", "Extra Weight * Time"]]

#This is the list (with indices) of different attributes that are currently present in out.py file

#[[0 - "WaybillNum", 1 - "Number of things", 2-  "Shipvia_code", 3 - "ship Date", 4 - "Zip Code", 5 - "Weight", 6 - "Processing Time", 7 - "CustomerID", 8 -  "Vendor Site ID", 9 - "Sales Order ID", 10 - "Time from ShipDate", 11 - "Work Center",12 -  "Parcel Type",13 -  "Transportation Cost", 14  -"Transit Time"]]

#VARIABLES
startTime = 6
endTime = 20
numberOfSimulations = 2
holdingWindowList = []
#This code produces random holding windows.
#Note that holding windows are randomly created and only take windows between 6 - 18.
def eligibleForParcel(v, indices):
    for i in indices:
        if v[i][11] in productList:
            return False
    return True
for i in range(numberOfSimulations):
    tempList = [startTime]
    while(True):
        currentLastHour = tempList[-1]
        newInt = random.randint(1,3)
        if (newInt + currentLastHour > endTime):
            tempList.append(24)
            break
        elif (newInt + currentLastHour == endTime):
            tempList.append(endTime)
            tempList.append(24)
            break
        else:
            tempList.append(newInt + currentLastHour)

    holdingWindowList.append(tempList)



for bounds in holdingWindowList:

    #These are the two new files that will be created as part of output for each holdingwindow
    #The first file contains information on how it should be shipped, based on the consildation at the end of holding windows
    #The second file contains information on how each of the original shipment corresponds to the new shipment data corresponds to the new one.

    shipData = [["New Shipment ID", "Ship via code", "IP Date",  "3 digit Zip Code", "Customer ID", "Current Cost", "Current Total Weight", "Number of consolidated shipments", "Cumulative Weight * Time", "consolidated cost", "Parcel Type", "Max Ship Time", "Min Ship Time"]]

    shipMap = [["New Shipment ID", "Old Shipment ID", "Original Parcel Type", "Sales Order ID"]]

    #List of new shipments
    shipNumber = 0


    #These are the parameters that will be calculated for each combination of holding windows
    analysisTotalCost = 0.0
    analysisConsolidatedCost = 0.0
    analysisWeightTime = 0.0


    #Reads out.csv file, and separates it to a dictionary with k,v pairs, key = shipdate + zipcode + customerID
    #value = list of all data that falls under this category
    for row in reader:
        defstr = row[3] + "%" + row[4][:3] + "%" + row[7]
        try:
            tempData = dict[defstr]
            tempData.append(row)
        except:
            dict[defstr] = [row]



    #Iterate over each of the key-value pair as mentioned above.
    for k, v in dict.items():
        lenv = len(v)

        #If the length = 1, there is no fancy analysis to be done, so just move on.
        if lenv > 1:

            #These bounds correspond to the end of the holding hours.
            # #For example, x = 1 gives [1,2,3.. 24]
            # bounds = range(0 + x, 24 + x, x)

            #Creates an empty list to store the relevant indices for each "holding window"
            indices_to_use = [[] for p in range(len(bounds))]

            #Now look at the data for all the candidates eligible for consolidation
            for row_indx in range(len(v)):

                #Reads the ship TIME and converts it to a machine readable format
                time_str =  v[row_indx][10]
                time_obj = datetime.datetime.strptime(time_str, "%I:%M:%S %p")
                hour = time_obj.hour
                mint = time_obj.minute
                time = hour * 1.0 + mint / 100.0

                #Adds it to the correct position in the indices_to_use to use
                #Which means that it adds to the correct window

                #For example something shipped at 3:45 PM will be put in the 4:00 PM window here
                indx = -1
                for alp in bounds:
                    indx += 1
                    if hour < alp:
                        break
                indices_to_use[indx].append(row_indx)

            #Note loop ends

            #Gathers information from key, can also be done from the value but whatever
            shipDate, zipcode, customer = k.split("%")

            #For each holding window ->
            for alpha in range(len(bounds)):

                #If that holding window actually contains anything
                if indices_to_use[alpha]:

                    #TODO for now, we have one shipment for all of this. Maybe later, what we need to do is decide what how to break down the shipments.
                    #For example, this would have to be done in case of large LTL and parcel and such things, I am not sure what the best way to handle that is

                    #[shipNum, Shipvia_code, ..]
                    shipDataTemp = [shipNumber, v[0][2], shipDate, zipcode, customer]

                    #Here there will be the consolidated shipment
                    total_original_cost = 0
                    total_weight = 0
                    additional_weight_time = 0
                    number_of_shipments_consolidated = 0
                    shipTimesList = []

                    #For each item in the holding window, make the following computation. Note that this for one holding window.


                    for beta in indices_to_use[alpha]:
                        current_row = v[beta]
                        #Look at each individual shipment here.
                        time_str1 =  current_row[10]
                        time_obj1 = datetime.datetime.strptime(time_str1, "%I:%M:%S %p")
                        hour1 = time_obj1.hour
                        mint1 = time_obj1.minute
                        #time one is the correct representation like 12:20 - 12.20, time2 is the number of hours 12:20 - 12.33333 hours.

                        time1 = round(hour1 * 1.0 + mint1 / 100, 2)
                        time2 = hour1 * 1.0 + mint1 / 60.0

                        #For each order, this contains all the shiptimes, for further analysis, seeing when they are gonna be shipped out, and the other stuff.
                        shipTimesList.append(time1)

                        #End of holding window
                        relative_shiptime = bounds[alpha]

                        #Make the relevant calculations for the weight, costs, etc.
                        total_original_cost += float(current_row[13])
                        total_weight += float(current_row[5])

                        #Measure for holding time Maybe?
                        additional_weight_time += float(current_row[5]) * ((relative_shiptime) - float(time2))

                        #Number of shipments consolidated for one order.
                        number_of_shipments_consolidated += 1

                        #shipMap = [["New Shipment ID", "Old Shipment ID", "Original Parcel Type", "Sales Order ID"]]
                        shipMap.append([shipNumber, current_row[0], current_row[13], current_row[9]])


                    shipTimesList.sort()
                    #Add current cost, current number of shipments, current total weight, etc to the correct row in the thing.
                    shipDataTemp.append(total_original_cost)
                    shipDataTemp.append(total_weight)
                    shipDataTemp.append(number_of_shipments_consolidated)
                    shipDataTemp.append(additional_weight_time)

                    analysisTotalCost += total_original_cost
                    analysisWeightTime += additional_weight_time




                    #This is used a little later to calculate parcel cost.
                    zone = zoneDict[str(int(zipcode))]

                    #This is to analyze what the best shipment mechanism would be
                    if len(zipcode) == 2:
                        zipcode = '0' + zipcode
                    if int(zipcode) > 915:
                        zipcode = '915'

                    #TODO everything with more than 915 zip is treated as 915, change this.

                    current_row = costDict[zipcode]
                    cost_row = []
                    for z in current_row[2:9]:
                        cost_row.append(float(z[1:]))
                    #LTL Rates
                    if total_weight <= 500:
                        ltl_cost = max(cost_row[0], min(total_weight * cost_row[1], 501 * cost_row[2]))
                    elif total_weight <= 1000:
                        ltl_cost = max(cost_row[0], min(total_weight * cost_row[2], 1001 * cost_row[3]))
                    elif total_weight <= 2000:
                        ltl_cost = max(cost_row[0], min(total_weight * cost_row[3], 2001 * cost_row[4]))
                    elif total_weight <= 5000:
                        ltl_cost = max(cost_row[0], min(total_weight * cost_row[4], 5001 * cost_row[5]))
                    elif total_weight <= 10000:
                        ltl_cost = max(cost_row[0], min(total_weight * cost_row[5], 10001 * cost_row[6]))
                    else:
                        ltl_cost = max(cost_row[0], total_weight * cost_row[6])



                    #Parcel Rate

                    wt_ind = int(math.ceil(min(150, total_weight)))
                    parcel_cost = parcelRatesDict[str(wt_ind) + "-" + zone]
                    parcel_cost = float(parcel_cost)

                    #TODO everything with a parcel rate of more than 150 is treated as an extra cost for the weight above 150.
                    if total_weight > 150:
                        parcel_cost += (total_weight - 150)*0.3


                    #Just pick the cheapest of the lot.
                    if (ltl_cost >= parcel_cost and parcel_cost <= total_original_cost and eligibleForParcel(v, indices_to_use[alpha])):
                        shipDataTemp.append(parcel_cost)
                        shipDataTemp.append("Parcel")
                        analysisConsolidatedCost += parcel_cost


                    elif (ltl_cost >= parcel_cost and parcel_cost <= total_original_cost):
                        shipDataTemp.append(ltl_cost)
                        shipDataTemp.append("LTL")
                        analysisConsolidatedCost += ltl_cost


                    elif (ltl_cost < parcel_cost and parcel_cost <= total_original_cost):
                        shipDataTemp.append(ltl_cost)
                        shipDataTemp.append("LTL")
                        analysisConsolidatedCost += ltl_cost

                    else:
                        shipDataTemp.append(total_original_cost)
                        shipDataTemp.append("Don't change, other things are more expensive")
                        analysisConsolidatedCost += total_original_cost
                    shipData.append(shipDataTemp)


                    #Takes into account what the first and the last shiptimes are, for each and adds it to the data.

                    tempDateObj= datetime.datetime.strptime(str(shipTimesList[0]), "%H.%M")
                    shipDataTemp.append(tempDateObj.strftime("%I:%M %p"))
                    tempDateObj= datetime.datetime.strptime(str(shipTimesList[-1]), "%H.%M")
                    shipDataTemp.append(tempDateObj.strftime("%I:%M %p"))

                    shipNumber += 1

        else:

            #In case there is only one, thing for a specific key. Don't do detailed analysis, just add it accordingly.
            shipDate, zipcode, customer = k.split("%")
            row = v[0]

            #["New Shipment ID", "Ship Date",  "3 digit Zip Code", "Customer ID", "Current Cost", "Current Total Weight", "Number of consolidated shipments", "Cumulative Weight*Time", "consolidated cost", "Parcel Type"]


            #TODO Maybe look at what the cheapest way of shipping is and then ship it that way. This will address cases in which it might have been cheaper to ship it differently.
            shipData.append([shipNumber, row[2], shipDate, zipcode, customer, row[13], row[5], 1, 0, row[13], row[12], row[10], row[10]])
            shipMap.append([shipNumber, row[0], row[12], row[9]])

            analysisTotalCost += float(row[13])
            analysisConsolidatedCost += float(row[13])

            shipNumber += 1

    #This list containts the details for the total costs, etc. depending on the different holding windows.
    analysisList.append([str(bounds), analysisTotalCost, analysisConsolidatedCost, analysisTotalCost - analysisConsolidatedCost, analysisWeightTime])

    #Write the adequate files, note that this currently this prints for each holding window.
    with open("output/out_shipData_" + str(bounds) +  ".csv", 'w') as outfile:
        writer = csv.writer(outfile, delimiter = ',')
        writer.writerows(shipData)

    with open("output/out_shipMap_" + str(bounds) +  ".csv", 'w') as outfile:
        writer = csv.writer(outfile, delimiter = ',')
        writer.writerows(shipMap)

#Print some of the details across different holding windows.
with open("output/analysis.csv", 'w') as outfile:
    writer = csv.writer(outfile, delimiter = ',')
    writer.writerows(analysisList)
