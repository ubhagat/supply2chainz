import csv
import numpy

#This script to translate the out.csv file to a
#combination of things that should have been consolidated.

#Step 1. Translate it into a dictionary of waybill numbers that
#make sense to be grouped together

csv.field_size_limit(1000000000000)
csvfile = open("out.csv", 'r')
reader = csv.reader(csvfile)
header = reader.next()
dict = {}

#[ 0 - "WaybillNum", 1 - "Number of things", 2 - "Shipvia_code", 3 -  "Ip Date", 4 - "Zip Code", 5 - "Weight", 6 - "Processing Time", 7 - "CustomerID",8 - "Vendor Site ID",9 - "Sales Order ID",10 - "Parcel Type",11 - "Transportation Cost",12 - "Transit Time"]

for row in reader:
    defstr = row[3] + "-" + row[4] + "-" + row[7]

    try:
        tempData = dict[defstr]
        tempData.append(row)
    except:
        dict[defstr] = [row]

for k, v in dict.iteritems():
    c += len(v)
    if len(v) == 1:
        e+=1
    d += 1
    print k, len(v)

print c,d,e

#Final Lists Looks like
#IPDATE,  ZIP CODE, CUSTOMER ID, Current Cost, Current Number of Shipments, Current Total Weight, consolidated cost, Number of consolidated shipments, associated extra weight * time

#IPDATE, ZIP CODE, CUSTOMER ID, Shipment number per combination, cost of this shipment, Associated extra time*weight wait

#Original shipments
og_ships = [["IPDATE",  "ZIP CODE", "CUSTOMER ID", "Current Cost", "Current Number of Shipments", "Current Total Weight", "consolidated cost", "Number of consolidated shipments", "associated extra weight * time"]]
#New shipments
new_ships = [["IPDATE", "ZIP CODE", "CUSTOMER ID", "Shipment number per combination", "cost of this shipment", "Associated extra time*weight wait"]]

for k, v in dict.iteritems():
    lenv = len(v)
    if lenv > 1:
        #THIS CODE AIMS TO GET THE CONSOLIDABLE WINDOWS
        typ1 = [0.0, 0.05]
        typ2 = [0.0, 0.0]

        num1 = [0]
        num2 = [0]

        indx1 = [[]]
        indx2 = [[]]

        total_num1 = 0
        total_num2 = 0
        i = 0
        while (total_num2 != lenv) and (total_num1 != lenv):
            for z_indx in range(lenv):
                z  = v[z_indx]
                processingTime = z[6]
                if processingTime > typ1[i] and processingTime < typ1[i + 1]:
                    num1[i] = num1[i] + 1
                    indx1[i].append(z_indx)
                    total_num1 += 1
                if processingTime > typ2[i] and processingTime < typ2[i + 1]:
                    num2[i] = num2[i] + 1
                    indx2[i].append(z_indx)
                    total_num2 += 1
            num1.append(0)
            num2.append(0)
            indx1.append([])
            indx2.append([])
        indices_to_use = None
        values_at_each_state = None
        bounds = None
        if(numpy.std(num1) > numpy.std(num2)):
            indices_to_use = indx1
            values_at_each_state = num1
            bounds = typ1
        else:
            indices_to_use = indx2
            values_at_each_state = num2
            bounds = typ2

        total_savings




        for alpha in range(len(values_at_each_state)):
            if values_at_each_state[alpha]:
                for beta in indices_to_use[alpha]:
                    pass

    else:
