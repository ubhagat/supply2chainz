import csv
import math

csv.field_size_limit(1000000000000)
csvfile = open("scriptData.csv", 'rU')
reader = csv.reader(csvfile, dialect=csv.excel_tab)
header = reader.next()


parcel_rates = [5.95, 6.12, 6.31, 6.78, 7.46, 7.55, 7.63, 7.92, 8.42, 8.69, 9.00, 9.22, 9.44, 9.60, 9.73, 10.26, 10.34, 10.46, 10.58, 10.77, 11.76, 13.26, 14.76, 16.26, 17.76, 18.77, 19.31, 19.90, 20.50, 21.13, 21.71, 21.96, 22.30, 22.50, 22.77, 23.05, 23.29, 23.50, 23.75, 23.99, 24.25, 24.43, 24.71, 24.87, 25.04, 25.25, 25.46, 25.66, 25.85, 25.96, 26.34, 26.75, 27.23, 27.63, 28.06, 28.45, 28.90, 29.33, 29.76, 30.14, 30.61, 30.99, 31.54, 31.83, 32.29, 32.72, 33.20, 33.59, 34.06, 34.41]
#['#NAME?', 'SHIP_DATE', 'BOX_VOL_WT', 'SHIPVIA_CODE', 'IP_DATE', 'ZIP CODE', 'Question Mark time (in Days)']
dict = {}

for row in reader:
    #print row
    #tempData = [WaybillNum, Number of things, Shipvia_code, Ip Date, Zip Code, Weight, Processing Time]

    row = row[0].split(',')
    if (row[13] == "ESJ"):
        try:

            tempData = dict[row[0]]
            tempData[1] = tempData[1] + 1
            tempData[5] = float(tempData[5]) + float(row[8])
            dict[row[0]] = tempData
        except:
            dict[row[0]] = [row[0], 1, row[9], row[17], row[32], row[8], row[33], row[16], row [13], row[15]]

#Reading the file to calculate the Transportation Cost and Transit time
costFile = open("TransportationData.csv", 'rU')
costReader = csv.reader(costFile)
costDict = {}
for row in costReader:
    costDict[row[0]] = row

#Creating the dictionary to figure out what type of shipment it is.
shipFile = open("ShipmentData.csv", 'rU')
shipReader = csv.reader(shipFile)
shipDict = {}
for row in shipReader:
    shipDict[row[0]] = row[8]

finalList = [["WaybillNum", "Number of things", "Shipvia_code", "Ip Date", "Zip Code", "Weight", "Processing Time", "CustomerID", "Vendor Site ID", "Sales Order ID", "Parcel Type", "Transportation Cost", "Transit Time"]]
for i in dict.values():
    temp = i
    parcelType = "Parcel"
    try:
        temp.append(shipDict[i[2]])
        parcelType = shipDict[i[2]]
    except:
        temp.append("Parcel")
    try:
        current_row = costDict[i[4]]
    except:
        current_row = costDict['010']
    cost_row = []
    for z in current_row[2:9]:
        cost_row.append(float(z[1:]))
    wt = float(i[5])
    cost = 0
    if parcelType == "Parcel":
        indx = min(69, int(math.floor(wt)))
        cost = parcel_rates[indx]
    else:
        if wt <= 500:
            cost = max(cost_row[0], min(wt * cost_row[1], 501 * cost_row[2]))
        elif wt <= 1000:
            cost = max(cost_row[0], min(wt * cost_row[2], 1001 * cost_row[3]))
        elif wt <= 2000:
            cost = max(cost_row[0], min(wt * cost_row[3], 2001 * cost_row[4]))
        elif wt <= 5000:
            cost = max(cost_row[0], min(wt * cost_row[4], 5001 * cost_row[5]))
        elif wt <= 10000:
            cost = max(cost_row[0], min(wt * cost_row[5], 10001 * cost_row[6]))
        else:
            cost = max(cost_row[0], wt * cost_row[6])
    temp.append(cost)
    temp.append(current_row[9])
    finalList.append(temp)

with open("out.csv", 'w') as outfile:
    writer = csv.writer(outfile, delimiter = ',')
    writer.writerows(finalList)
