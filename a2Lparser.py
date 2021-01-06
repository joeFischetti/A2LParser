#imports
import re, pprint, sys, argparse


#set up empty dicts to use for storing objects
axesDefs = {}
mapDefs = {}
compuMethods = {}
measurements = {}

#classes to use for objects that we've parsed

#Map3D is a 3 dimensional map (a map with 2 axes)
class Map3D:
    name = ""
    description = ""
    address = ""
    function = ""
    displayFormat = ""
    xAxisLabel = ""
    xAxisAddress = ""
    xAxisFunction = ""
    yAxisLabel = ""
    yAxisAddress = ""
    yAxisFunction = ""

#An Axis is part of a map
class Axis:
    name = ""
    address = ""
    function = ""

#CompuMethod is the way the raw data is converted into human readable/actual numnbers
class CompuMethod:
    name = ""
    function = ""
    coeffs = ""

#Measurements are memory locations 
class Measurement:
    name = ""
    description = ""
    address = ""

#These are functions used to parse a stanza
def parseMeasurement(stanza):
    lineNum = 0
    thisMeasurement = Measurement()
    
    for line in stanza.split("\n"):
        line = line.strip()
        if lineNum == 0:
            thisMeasurement.name = line.split(" ")[2]
        elif lineNum == 1:
            thisMeasurement.description = line
        if re.match("^ECU_ADDRESS.*", line):
            thisMeasurement.address = line.split(" ")[1]

        lineNum += 1

    measurements[thisMeasurement.name] = thisMeasurement

def parseCompuMethod(stanza):
    lineNum = 0
    thisCompu = CompuMethod()

    for line in stanza.split("\n"):
        line = line.strip()
        if lineNum == 0:
            thisCompu.name = line.split(" ")[2]
        elif lineNum == 5:
            thisCompu.coeffs = line.split("COEFFS ")[1]
            thisCompu.function = str("( " + thisCompu.coeffs.split(" ")[2] + " - x ) / -" + thisCompu.coeffs.split(" ")[1])

        lineNum += 1

    compuMethods[thisCompu.name] = thisCompu


def parseAxis(stanza):

    lineNum = 0
    thisAxis = Axis()

    for line in stanza.split("\n"):
        line = line.strip()
        if lineNum == 0:
            thisAxis.name = line.split(" ")[2]
        elif lineNum == 2:
            thisAxis.address = line
        elif lineNum == 6:
            thisAxis.function = line

        lineNum += 1

    axesDefs[thisAxis.name] = thisAxis

def parseMAP(stanza):
    lineNum = 0

    thisMap = Map3D()

    for line in stanza.split("\n"):
        line = line.strip()
        if lineNum == 0:
            thisMap.name = line.split(" ")[2]
        elif lineNum == 1:
            thisMap.description == line
        elif lineNum == 3:
            thisMap.address = line
        elif lineNum == 6:
            thisMap.function = compuMethods[line].function
        elif lineNum == 10:
            thisMap.displayFormat = line.split(" ")[1]
        elif lineNum == 13:
            thisMap.xAxisLabel = line
        elif lineNum == 14:
            thisMap.xAxisFunction = compuMethods[line].function
        elif lineNum == 19:
            thisMap.xAxisAddress = axesDefs[line.split(' ')[1]].address
        elif lineNum == 23:
            thisMap.yAxisLabel = line
        elif lineNum == 24:
            thisMap.yAxisFunction = compuMethods[line].function
        elif lineNum == 29:
            thisMap.yAxisAddress = axesDefs[line.split(' ')[1]].address

        lineNum += 1

    mapDefs[thisMap.name] = thisMap        
    #print(vars(thisMap))

def getMeasurements(inputFile):
    stanza = ""
    endStanza = True

    for line in inputFile:
        if re.match("\n", line.strip()):
            print("Blank line")
            continue
        elif re.match("^\/begin MEASUREMENT .*", line.strip()):
            endStanza = False
        elif re.match("^/end MEASUREMENT.*", line.strip()):
            endStanza = True
            stanza += line

        if endStanza is False:
            stanza += line

        else:
            if stanza is not "":
                parseMeasurement(stanza)
                stanza = ""

def getCompuMethods(inputFile):
    stanza = ""
    endStanza = True

    for line in inputFile:
        if re.match("\n", line.strip()):
            print("Blank line")
            continue
        elif re.match("^\/begin COMPU_METHOD .*", line.strip()):
            endStanza = False
        elif re.match("^/end COMPU_METHOD.*", line.strip()):
            endStanza = True
            stanza += line

        if endStanza is False:
            stanza += line

        else:
            if stanza is not "":
                parseCompuMethod(stanza)
                stanza = ""
 

def getAxisDefinitions(inputFile):
    stanza = ""
    endStanza = True

    for line in inputFile:
        if re.match("\n", line.strip()):
            print("Blank line")
            continue
        elif re.match("^\/begin AXIS_PTS .*", line.strip()):
            endStanza = False
        elif re.match("^/end AXIS_PTS.*", line.strip()):
            endStanza = True
            stanza += line

        if endStanza is False:
            stanza += line

        else:
            if stanza is not "":
                parseAxis(stanza)
                stanza = ""
   

def getMapDefinitions(inputFile):
    stanza = ""
    endStanza = True

    for line in inputFile:
        if re.match("\n", line.strip()):
            print("Blank line")
            continue
        elif re.match("^\/begin CHARACTERISTIC.*", line.strip()):
            endStanza = False
        elif re.match("^/end CHARACTERISTIC.*", line.strip()):
            endStanza = True
            stanza += line

        if endStanza is False:
            stanza += line

        else:
            if stanza is not "":
                parseMAP(stanza)
                stanza = ""

#build the argument parser and set up the arguments
parser = argparse.ArgumentParser(description='A2L Parser')
parser.add_argument('--file',help="location of the a2L file")

args = parser.parse_args()

#Set the global file path to the argument, or local
if args.file is not None:
    filename = args.file
else:
    filename = "./example.a2l"


#with open(filename, 'r', encoding="iso-8859-1") as inputFile:
#    getCompuMethods(inputFile)
#
#with open(filename, 'r', encoding="iso-8859-1") as inputFile:
#    getAxisDefinitions(inputFile)
#
#with open(filename, 'r', encoding="iso-8859-1") as inputFile:
#    getMapDefinitions(inputFile)
#
with open(filename, 'r', encoding="iso-8859-1") as inputFile:
    getMeasurements(inputFile)

for Measurement in measurements:
    print("MEM_" + measurements[Measurement].name.replace(" ", "_"), end=' ')
    print(measurements[Measurement].address.lstrip('0x'), end=' ')
    print('l', end=' ')
    print('1', end=' ')
    print(measurements[Measurement].description.replace(" ", "_"), end=' ')
    print('')

#for Map in mapDefs:
#    pprint.pprint(vars(mapDefs[Map]))
