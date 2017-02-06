import csv
import numpy
import math

#This script to translate the out.csv file to a
#combination of things that should have been consolidated.

#Step 1. Translate it into a dictionary of waybill numbers that
#make sense to be grouped together

csv.field_size_limit(1000000000000)
csvfile = open("out.csv", 'r')
reader = csv.reader(csvfile)
header = reader.next()
dict = {}



#Reading the file to calculate the Transportation Cost and Transit time
costFile = open("TransportationData.csv", 'rU')
costReader = csv.reader(costFile)
costDict = {}
for row in costReader:
    costDict[row[0]] = row

parcel_rates = [5.95, 6.12, 6.31, 6.78, 7.46, 7.55, 7.63, 7.92, 8.42, 8.69, 9.00, 9.22, 9.44, 9.60, 9.73, 10.26, 10.34, 10.46, 10.58, 10.77, 11.76, 13.26, 14.76, 16.26, 17.76, 18.77, 19.31, 19.90, 20.50, 21.13, 21.71, 21.96, 22.30, 22.50, 22.77, 23.05, 23.29, 23.50, 23.75, 23.99, 24.25, 24.43, 24.71, 24.87, 25.04, 25.25, 25.46, 25.66, 25.85, 25.96, 26.34, 26.75, 27.23, 27.63, 28.06, 28.45, 28.90, 29.33, 29.76, 30.14, 30.61, 30.99, 31.54, 31.83, 32.29, 32.72, 33.20, 33.59, 34.06, 34.41]


#[ 0 - "WaybillNum", 1 - "Number of things", 2 - "Shipvia_code", 3 -  "Ip Date", 4 - "Zip Code", 5 - "Weight", 6 - "Processing Time", 7 - "CustomerID",8 - "Vendor Site ID",9 - "Sales Order ID",10 - "Parcel Type",11 - "Transportation Cost",12 - "Transit Time"]

for row in reader:
    defstr = row[3] + "%" + row[4] + "%" + row[7]

    try:
        tempData = dict[defstr]
        tempData.append(row)
    except:
        dict[defstr] = [row]

# for k, v in dict.iteritems():
#     c += len(v)
#     if len(v) == 1:
#         e+=1
#     d += 1
#     print k, len(v)
#
# print c,d,e

shipData = [["New Shipment ID", "Ship via code", "IP Date",  "3 digit Zip Code", "Customer ID", "Current Cost", "Current Total Weight", "Number of consolidated shipments", "Cumulative Weight*Time", "consolidated cost", "Parcel Type"]]

shipMap = [["New Shipment ID", "Old Shipment ID", "Original Parcel Type"]]

shipNumber = 0
for k, v in dict.iteritems():
    lenv = len(v)
    if lenv > 1:
        #THIS CODE AIMS TO GET THE CONSOLIDABLE WINDOWS
        # typ1 = [0.0, 0.05]
        # typ2 = [0.0, 0.0]
        #
        # num1 = [0]
        # num2 = [0]
        #
        # indx1 = [[]]
        # indx2 = [[]]
        #
        # total_num1 = 0
        # total_num2 = 0
        # i = 0
        # while (total_num2 != lenv) and (total_num1 != lenv):
        #     for z_indx in range(lenv):
        #         z  = v[z_indx]
        #         processingTime = z[6]
        #         if processingTime > typ1[i] and processingTime < typ1[i + 1]:
        #             num1[i] = num1[i] + 1
        #             indx1[i].append(z_indx)
        #             total_num1 += 1
        #         if processingTime > typ2[i] and processingTime < typ2[i + 1]:
        #             num2[i] = num2[i] + 1
        #             indx2[i].append(z_indx)
        #             total_num2 += 1
        #     num1.append(0)
        #     num2.append(0)
        #     indx1.append([])
        #     indx2.append([])
        #     typ1.append(typ1[-1] + 0.1)
        #     typ2.append(typ2[-1] + 0.1)
        typ1 = []
        typ2 = []

        num1 = []
        num2 = []

        indx1 = []
        indx2 = []
        for row_indx in range(len(v)):
            if v[row_indx][6]:
                processingTime = float(v[row_indx][6])
                one_time  = int(math.ceil(processingTime * 10))
                two_time  = int(math.ceil(processingTime * 10 + 0.5))

                if one_time in typ1:
                    temp = typ1.index(one_time)
                    num1[temp] = num1[temp] + 1
                    indx1[temp].append(row_indx)
                else:
                    typ1.append(one_time)
                    num1.append(1)
                    indx1.append([row_indx])

                if two_time in typ2:
                    temp = typ2.index(two_time)
                    num2[temp] = num2[temp] + 1
                    indx2[temp].append(row_indx)
                else:
                    typ2.append(two_time)
                    num2.append(1)
                    indx2.append([row_indx])
        indices_to_use = None
        values_at_each_state = None
        bounds = None
        #print typ1, typ2, num1, num2, indx1, indx2
        if(numpy.std(num1) > numpy.std(num2)):
            indices_to_use = indx1
            values_at_each_state = num1
            bounds = typ1
        else:
            indices_to_use = indx2
            values_at_each_state = num2
            bounds = typ2

        #["New Shipment ID", "IP Date",  "3 digit Zip Code", "Customer ID", "Current Cost", "Current Total Weight", "Number of consolidated shipments", "Cumulative Weight*Time", "consolidated cost", "Parcel Type"]
        ipdate, zipcode, customer = k.split("%")

        for alpha in range(len(values_at_each_state)):
            shipDataTemp = [shipNumber, v[0][2], ipdate, zipcode, customer]
            #Here there will be the consolidated shipment
            total_original_cost = 0
            total_weight = 0
            additional_weight_time = 0
            number_of_shipments_consolidated = 0
            for beta in indices_to_use[alpha]:
                current_row = v[beta]

                #Look at each individual shipment here.
                relative_shiptime = bounds[alpha]
                total_original_cost += float(current_row[11])
                total_weight += float(current_row[5])
                additional_weight_time += float(current_row[5]) * (relative_shiptime - float(current_row[6]))
                number_of_shipments_consolidated += 1
                shipMap.append([shipNumber, current_row[0], current_row[10]])


            #Add current cost, current number of shipments, current total weight,
            shipDataTemp.append(total_original_cost)
            shipDataTemp.append(total_weight)
            shipDataTemp.append(number_of_shipments_consolidated)
            shipDataTemp.append(additional_weight_time)

            #This is to analyze what the best shipment mechanism would be
            try:
                current_row = costDict[zipcode]
            except:
                current_row = costDict['010']
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
            if total_weight < 70:
                parcel_cost = parcel_rates[int(math.floor(total_weight))]
            else:
                parcel_cost = 34.41 + 0.7 * (int(math.floor(total_weight)) - 70)

            if (ltl_cost >= parcel_cost):
                shipDataTemp.append(parcel_cost)
                shipDataTemp.append("Parcel")
            else:
                shipDataTemp.append(ltl_cost)
                shipDataTemp.append("LTL")

            shipData.append(shipDataTemp)
            shipNumber += 1

    else:
        ipdate, zipcode, customer = k.split("%")
        row = v[0]

        #["New Shipment ID", "IP Date",  "3 digit Zip Code", "Customer ID", "Current Cost", "Current Total Weight", "Number of consolidated shipments", "Cumulative Weight*Time", "consolidated cost", "Parcel Type"]

        shipData.append([shipNumber, row[2], ipdate, zipcode, customer, row[11], row[5], 1, 0, row[11], row[10]])
        shipMap.append([shipNumber, row[0], row[10]])
        shipNumber += 1

with open("out_shipData.csv", 'w') as outfile:
    writer = csv.writer(outfile, delimiter = ',')
    writer.writerows(shipData)

with open("out_shipMap.csv", 'w') as outfile:
    writer = csv.writer(outfile, delimiter = ',')
    writer.writerows(shipMap)
