import csv
import math

csv.field_size_limit(1000000000000)
csvfile = open("scriptData.csv", 'rU')
reader = csv.reader(csvfile, dialect=csv.excel_tab)
header = reader.next()

dict = {}

for row in reader:
    #print row
    #tempData = [WaybillNum, Number of things, Shipvia_code, Ip Date, Zip Code, Weight, Processing Time]

    row = row[0].split('%')
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

#Reading the data for Parcel Rates
ParcelRatesFile = open("Parcel_Rates.csv", 'rU')
rateReader = csv.reader(ParcelRatesFile)
parcelRatesDict = {}
for row in rateReader:
    parcelRatesDict[row[0] + "-" + row[1]] = row[2]

#Readingt the Parcel Zones
ParcelZonesFile = open("ParcelZones.csv", 'rU')
zoneReader = csv.reader(ParcelZonesFile)
zoneDict = {}
for row in zoneReader:
    zoneDict[row[0]] = row[1]


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
        #This exception case is for rows that don't have an associated LTL or Parcel Type
        temp.append("Parcel")
    # try:
    #     current_row = costDict[i[4]]
    # except:
    #     current_row = costDict['010']

    zipcode = i[4]
    if len(zipcode) == 2:
        zipcode = '0' + zipcode
    if int(zipcode) > 915:
        zipcode = '915'
    current_row = costDict[zipcode]
    cost_row = []
    for z in current_row[2:9]:
        cost_row.append(float(z[1:]))
    wt = float(i[5])
    cost = 0
    if parcelType == "Parcel":
        zone = zoneDict[str(int(i[4]))]
        wt_ind = min(150, int(math.ceil(wt)))
        cost = parcelRatesDict[str(wt_ind) + "-" + zone]
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
