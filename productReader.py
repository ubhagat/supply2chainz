import csv
productsFile = open("products.csv", 'rU')
productReader = csv.reader(productsFile)
productList = productReader.next()
print productList
