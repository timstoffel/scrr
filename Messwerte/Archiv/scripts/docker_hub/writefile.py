import csv

class writefile():
    def __init__(self, ):
        pass

    def writecsv(self, csvname, row):
        with open('./{name}.csv'.format(name=csvname), mode='a+', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(row)

    def writejson(self, name, data):
        with open('./{name}.json'.format(name=name), mode='a+') as jsonfile:
            datastring = str(data).replace('\'', '"')         
            jsonfile.write(datastring)
