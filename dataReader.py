import csv

class Driver:
    def __init__(self,id, fName, lName,age, city,state):
        self.id = int(id)
        self.firstName = fName
        self.lastName = lName
        self.age = int(age)
        self.city = city
        self.state = state

    def __str__(self):
        return str(self.__dict__)

class Assignment:
    def __init__(self, id, route, weekDay):
        self.id = int(id)
        self.route = route
        self.weekDay = weekDay
    
    def __str__(self):
        return str(self.__dict__)

class Route:
    def __init__(self, rNumber, rName, depCity, depCityCode, destCity, destCode, rType, depTimeHours, depTimeMin, tTimeHours, tTimeMin):
        self.routeNumber = int(rNumber)
        self.routeName = rName
        self.departureCity = depCity
        self.departureCode = depCityCode
        self.desinationCode = destCode
        self.routeType = rType
        self.departureHour = int(depTimeHours)
        self.departureMin = int(depTimeMin)
        self.travelTimeHour = int(tTimeHours)
        self.travelTimeMin = int(tTimeMin)
        self.totalDepartueTime = 60*int(depTimeHours) + int(depTimeMin)
        self.totalTime = int(tTimeHours) * 60 + int(tTimeMin)
    
    def __str__(self):
        return str(self.__dict__)


data = []
for line in open("Assignment.csv"):
    csv_row = line.strip('\n').lower().split(',')
    try:
        data.append(Assignment(csv_row[0],csv_row[1],csv_row[2]))
    except:
        continue

for line in open("Driver.csv"):
    csv_row = line.strip('\n').lower().split(',')
    try:
        data.append(Driver(csv_row[0],csv_row[1],csv_row[2],csv_row[3],csv_row[4],csv_row[5]))
    except:
        continue

for line in open("Routes.csv"):
    csv_row = line.strip('\n').lower().split(',')
    try:
        data.append(Route(csv_row[0], csv_row[1],csv_row[2],csv_row[3],csv_row[4],csv_row[5],csv_row[6],csv_row[7],csv_row[8],csv_row[9],csv_row[10]))
    except:
        continue


for i in data:
    print(i)

