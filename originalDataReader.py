#Reads the original data which is unit level and converts it to shipment level data.
import csv
import math

#Opens the Raw CSV file containing original Data.
csvfile = open("scriptData.csv", "r",encoding='utf-8', errors='ignore')
reader = csv.reader(csvfile, dialect=csv.excel_tab)
next(reader, None)

dict = {}

#Puts each row in the data into a Dictionary with the Waybill as the key.
#This is also counts the number of times each Waybill appears in the column "Number of Things"
for row in reader:

    #tempData = [WaybillNum, Number of things, Shipvia_code, Ip Date, Zip Code, Weight, Processing Time]

    row = row[0].split('|')
    try:

        tempData = dict[row[0]]
        tempData[1] = tempData[1] + 1
        tempData[5] = float(tempData[5]) + float(row[8])
        dict[row[0]] = tempData
    except:

        dict[row[0]] = [row[0], 1, row[9], row[1], row[24], row[8], row[32], row[16], row [13], row[15], row[34], row[30]]

#The following section reads the data corresponding to the transportation data costs
#This file is in the format 3DZ ,State , Minimum Cost ,500,1000,2000,5000,10000, 10001+ lb,Transit Time
#Creates dictionary based on 3DZ
costFile = open("TransportationData.csv", 'rU')
costReader = csv.reader(costFile)
costDict = {}
for row in costReader:

    costDict[row[0]] = row

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


#The following section reads the data for Shipment Type of each carrier.
#This will be essentially used to determine if a product is currently being shipped LTL or Parcel.
#The Key is the ShipVia Code and the Value is the Shipment Type ie LTL/Parcel
shipFile = open("ShipmentData.csv", 'rU')
shipReader = csv.reader(shipFile)
shipDict = {}
for row in shipReader:
    shipDict[row[0]] = row[8]

#This section contains the data that will be written to the final CSV file. In addition to the data in the dictionary
#"dict", it also contains PArcel Type, Transportation Cost and Transit Time.
finalList = [["WaybillNum", "Number of things", "Shipvia_code", "ship Date", "Zip Code", "Weight", "Processing Time", "CustomerID", "Vendor Site ID", "Sales Order ID", "Time from ShipDate","Work Center", "Parcel Type", "Transportation Cost", "Transit Time"]]


for i in dict.values():
    temp = i
    parcelType = "Parcel"
    try:
        temp.append(shipDict[i[2]])
        parcelType = shipDict[i[2]]
    except:
        #This exception case is for rows that don't have an associated LTL or Parcel Type
        temp.append("Parcel")

	#This section incorporates the zipcodes, "zones" the customers are located and calculates the corresponding
	#current costs associated with the current shipments.
    zip1 = i[4]
    if (len(zip1) > 2):
        zip1 = zip1[:3]
    else:
        zip1 = zip1[:2]
    zipcode = i[4]
    if len(zipcode) == 2:
        zipcode = '0' + zipcode
    else:
        zipcode = zipcode[:3]
    if int(zipcode) > 915:
        zipcode = '915'
    current_row = costDict[zipcode]
    cost_row = []
    for z in current_row[2:9]:
        cost_row.append(float(z[1:]))
    wt = float(i[5])
    cost = 0
    #Parcel Costs were calculated based on distance and weight.
    if parcelType == "Parcel":
        zone = zoneDict[str(int(zip1))]
        wt_ind = min(150, int(math.ceil(wt)))
        cost = parcelRatesDict[str(wt_ind) + "-" + zone]
    #LTL costs are calculated on the basis of weight of shipment.
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

#This section writes the final shipment level data to a CSV file which is analyzed in outAnalyzer.
with open("out_2.csv", 'w', newline = '') as outfile:
    writer = csv.writer(outfile, delimiter = ',')
    writer.writerows(finalList)
