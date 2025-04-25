import re

# Define the Sink structure using a dataclass for clarity
from dataclasses import dataclass
import math

@dataclass
class Sink:
    x: int
    y: int
    cap: float
    
@dataclass
class Edge:
    x1: int
    y1: int
    x2: int
    y2: int
    
@dataclass
class XPar:
    TapA: Sink
    TapB: Sink
    SinkA: Sink
    SinkB: Sink
    EdgeA1: Edge
    EdgeA2: Edge
    EdgeB1: Edge
    EdgeB2: Edge
    Quadrant: int
    Len45: float
    Len90: float

# Global variables
numPins = None
unitRes = None
unitCap = None
sinks = []

def parse_file(filepath):
    global numPins, unitRes, unitCap, sinks

    with open(filepath, 'r') as file:
        lines = file.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith("NumPins"):
            numPins = int(re.search(r'\d+', line).group())
        elif line.startswith("PerUnitResistance"):
            unitRes = float(re.search(r'[\d.]+', line).group())
        elif line.startswith("PerUnitCapacitance"):
            #print (re.search(r'[\d.eE+-]+', line).group())
            #unitCap = float(re.search(r'([\d.eE+-]+)', line).group())
            unitCap = float(re.search(r'[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?', line).group())
        elif line.startswith("Sink"):
            # Read next two lines for Coordinate and Capacitive Load
            coord_line = lines[i + 1].strip()
            cap_line = lines[i + 2].strip()

            coord_match = re.search(r'Coordinate\s*:\s*(\d+)\s+(\d+)', coord_line)
            cap_match = re.search(r'Capacitive Load\s*:\s*([\d.eE+-]+)', cap_line)

            if coord_match and cap_match:
                x = int(coord_match.group(1))
                y = int(coord_match.group(2))
                cap = float(cap_match.group(1))
                sinks.append(Sink(x, y, cap))

            i += 2  # Skip the next two lines that we've just processed

        i += 1

def manhattanDistance(sink1, sink2):
    return abs(sink1.x - sink2.x) + abs(sink1.y - sink2.y)

def closestPoints(tapSinks,xPars):
    sinkA = tapSinks[0]
    sinkB = tapSinks[1]
    #dist = manhattanDistance(tapSinks[0], tapSinks[1])
    dist = greatestx+greatesty
    for i in range(0,len(tapSinks)):
        sinkTwin = Sink(0,0,0)
        for xPar in xPars:
            if xPar.TapA == tapSinks[i]:
                sinkTwin = xPar.TapB
            elif xPar.TapB == tapSinks[i]:
                sinkTwin = xPar.TapA
        for j in range(i+1,len(tapSinks)):
            if (manhattanDistance(tapSinks[i], tapSinks[j]) < dist and (tapSinks[j].x != sinkTwin.x and tapSinks[j].y != sinkTwin.y)):
                sinkA = tapSinks[i]
                sinkB = tapSinks[j]
                dist = manhattanDistance(tapSinks[i], tapSinks[j])
    return sinkA,sinkB

def createTappingPoint(edge1,edge2,sink1,sink2,quadrant):
    length1 = math.sqrt((edge1.x2-edge1.x1)**2 + (edge1.y2-edge1.y1)**2)
    length2 = math.sqrt((edge2.x2-edge2.x1)**2 + (edge2.y2-edge2.y1)**2)
    #print(sink1.cap)
    totalLength = length1+length2
    totalRes = totalLength*unitRes
    totalCap = totalLength*unitCap
    #edgeproportion = length1/totalLength
    tapLength = (totalLength * (totalCap + 2*sink1.cap)) / (2*(totalCap + sink1.cap + sink2.cap)) #relative to sink2
    tapCap = totalCap+sink1.cap+sink2.cap
    #Design mirroring functionality for 2nd tapping point
    if (tapLength > length2): #enters 45 deg segment
        tapDist = round((totalLength-tapLength)/math.sqrt(2))
        #print(tapDist)
        if quadrant == 1:
            tapA = Sink(sink1.x+tapDist,sink1.y+tapDist,tapCap)
            tapB = Sink(sink2.x-tapDist,sink2.y-tapDist,tapCap)
        if quadrant == 2:
            tapA = Sink(sink1.x-tapDist,sink1.y+tapDist,tapCap)
            tapB = Sink(sink2.x+tapDist,sink2.y-tapDist,tapCap)
        if quadrant == 3:
            tapA = Sink(sink1.x-tapDist,sink1.y-tapDist,tapCap)
            tapB = Sink(sink2.x+tapDist,sink2.y+tapDist,tapCap)
        if quadrant == 4:
            tapA = Sink(sink1.x+tapDist,sink1.y-tapDist,tapCap)
            tapB = Sink(sink2.x-tapDist,sink2.y+tapDist,tapCap)
    elif (tapLength <= length2): #on 90 deg segment
        tapDist = round(tapLength)
        #print(tapDist)
        if edge2.x1 == edge2.x2: #90 deg in y direction
            if quadrant == 1 or quadrant == 2:
                tapA = Sink(sink2.x,sink2.y-tapDist,tapCap)
                tapB = Sink(sink1.x,sink1.y+tapDist,tapCap)
            if quadrant == 3 or quadrant == 4:
                tapA = Sink(sink2.x,sink2.y+tapDist,tapCap)
                tapB = Sink(sink1.x,sink1.y-tapDist,tapCap)
        elif edge2.y1 == edge2.y2: #90 deg in x direction
            if quadrant == 1 or quadrant == 4:
                tapA = Sink(sink2.x-tapDist,sink2.y,tapCap)
                tapB = Sink(sink1.x+tapDist,sink1.y,tapCap)
            if quadrant == 2 or quadrant == 3:
                tapA = Sink(sink2.x+tapDist,sink2.y,tapCap)
                tapB = Sink(sink1.x-tapDist,sink1.y,tapCap)
        else:
            print("Edge 1 and 2 are not 45 and 90 degrees")
            if quadrant == 1:
                tapA = Sink(sink1.x+tapDist,sink1.y+tapDist,tapCap)
                tapB = Sink(sink2.x-tapDist,sink2.y-tapDist,tapCap)
            if quadrant == 2:
                tapA = Sink(sink1.x-tapDist,sink1.y+tapDist,tapCap)
                tapB = Sink(sink2.x+tapDist,sink2.y-tapDist,tapCap)
            if quadrant == 3:
                tapA = Sink(sink1.x-tapDist,sink1.y-tapDist,tapCap)
                tapB = Sink(sink2.x+tapDist,sink2.y+tapDist,tapCap)
            if quadrant == 4:
                tapA = Sink(sink1.x+tapDist,sink1.y-tapDist,tapCap)
                tapB = Sink(sink2.x-tapDist,sink2.y+tapDist,tapCap)
    else:
        print("Out of bounds taplength")


    print(edge1,edge2)
    #print(totalLength)
    #print(length1)
    #print(length2)
    #print(edgeproportion)
    #print(tapLength)
    return tapA,tapB



def createXPar(sink1, sink2):
    diffx = abs(sink1.x - sink2.x)
    diffy = abs(sink1.y - sink2.y)
    if (diffx == 0):
        print(sink1 + sink2 + " =x, move one of them")
    if (diffy == 0):
        print(sink1 + sink2 + " =y, move one of them")
    quadrant = 0
    if (sink2.x > sink1.x):
        if (sink2.y > sink1.y):
            quadrant = 1
        elif (sink2.y < sink1.y):
            quadrant = 4
    elif (sink2.x < sink1.x):
        if (sink2.y > sink1.y):
            quadrant = 2
        elif (sink2.y < sink1.y):
            quadrant = 3
    if (diffx < diffy): #x is smaller than y, so 45deg terminates in x direction after diffx
        if (quadrant==1 or quadrant==2): #generate tapping point based on total length, find spot within edge
            EdgeA1 = Edge(sink1.x,sink1.y,sink2.x,sink1.y+diffx) #90 +/-45deg
            EdgeA2 = Edge(sink2.x,sink1.y+diffx,sink2.x,sink2.y) #90deg
            EdgeB1 = Edge(sink1.x,sink1.y,sink1.x,sink2.y-diffx) #90deg
            EdgeB2 = Edge(sink1.x,sink2.y-diffx,sink2.x,sink2.y) #90 +/-45deg
        elif (quadrant==3 or quadrant==4):
            EdgeA1 = Edge(sink1.x,sink1.y,sink2.x,sink1.y-diffx) #90 +/-45deg
            EdgeA2 = Edge(sink2.x,sink1.y-diffx,sink2.x,sink2.y) #-90deg
            EdgeB1 = Edge(sink1.x,sink1.y,sink1.x,sink2.y+diffx) #-90deg
            EdgeB2 = Edge(sink1.x,sink2.y+diffx,sink2.x,sink2.y) #90 +/-45deg
        #make the xPar, calculate tapping point
    elif (diffx > diffy): #x is larger than y, so 45deg terminates in y direction after diffy
        if (quadrant==1 or quadrant==4): #generate tapping point based on total length, find spot within edge
            EdgeA1 = Edge(sink1.x,sink1.y,sink1.x+diffy,sink2.y) #-90 +/-45deg
            EdgeA2 = Edge(sink1.x+diffy,sink2.y,sink2.x,sink2.y) #0deg
            EdgeB1 = Edge(sink1.x,sink1.y,sink2.x-diffy,sink1.y) #0deg
            EdgeB2 = Edge(sink2.x-diffy,sink1.y,sink2.x,sink2.y) #-90 +/-45deg
        elif (quadrant==2 or quadrant==3):
            EdgeA1 = Edge(sink1.x,sink1.y,sink1.x-diffy,sink2.y) #-90 +/-45deg
            EdgeA2 = Edge(sink1.x-diffy,sink2.y,sink2.x,sink2.y) #180deg
            EdgeB1 = Edge(sink1.x,sink1.y,sink2.x+diffy,sink1.y) #180deg
            EdgeB2 = Edge(sink2.x+diffy,sink1.y,sink2.x,sink2.y) #-90 +/-45deg
        #make the xPar, calculate tapping point
    else:
        EdgeA1 = Edge(sink1.x,sink1.y,sink2.x,sink2.y) #Duplicate edges so functions work, will delete at end
        EdgeA2 = Edge(sink1.x,sink1.y,sink2.x,sink2.y) 
        EdgeB1 = Edge(sink1.x,sink1.y,sink2.x,sink2.y) 
        EdgeB2 = Edge(sink1.x,sink1.y,sink2.x,sink2.y) 

    #tapA = createTappingPoint(EdgeA1,EdgeA2,sink1,sink2)
    #tapB = createTappingPoint(EdgeB2,EdgeB1,sink1,sink2)
    tapA, tapB = createTappingPoint(EdgeA1,EdgeA2,sink1,sink2,quadrant)
    #tapA = Sink(EdgeA1.x2,EdgeA1.y2,sink1.cap+sink2.cap)
    #tapB = Sink(EdgeB1.x2,EdgeB1.y2,sink1.cap+sink2.cap)
    return XPar(tapA,tapB,sink1,sink2,EdgeA1,EdgeA2,EdgeB1,EdgeB2,quadrant,0,0)
    

# Example usage
parse_file("r1.txt")

# Optional: print out a summary
print(f"NumPins: {numPins}")
print(f"PerUnitResistance: {unitRes}")
print(f"PerUnitCapacitance: {unitCap}")
print(f"Number of sinks parsed: {len(sinks)}")
print(f"First sink: {sinks[0]}")
print(f"First sink: {sinks[1]}")
print(manhattanDistance(sinks[0], sinks[1]))

greatestx = 0
greatesty = 0
for sink in sinks:
    if (sink.x > greatestx):
        greatestx = sink.x
    if (sink.y > greatesty):
        greatesty = sink.y

print(greatestx,greatesty)
f = open("Sinks.txt", "w")
f.write(str(0) + " " + str(0) + " " + str(greatestx+10) + " " + str(greatesty+10) + "\n")
f.write(str(len(sinks)) + "\n")
for sink in sinks:
    f.write(str(sink.x) + " " + str(sink.y) + "\n")
f.close()

        

tapSinks = sinks
xPars = []

f = open("Edges.txt", "w")
iterations = numPins-1
#f.write(str(iterations*4) + "\n")
f.write(str(iterations*2) + "\n")

t = open("Taps.txt","w")
t.write(str(iterations*2) + "\n")
t.write(str(iterations*2) + "\n")

#print(closestPoints(tapSinks,xPars))
#while len(tapSinks) > 2:
for i in range(0,iterations):
    sink1, sink2 = closestPoints(tapSinks,xPars)
    #xPars.append(createXPar(sink1,sink2))
    print(sink1,sink2)
    Xpar = createXPar(sink1,sink2)
    #createTappingPoint(Xpar.EdgeA1,Xpar.EdgeA2,Xpar.SinkA,Xpar.SinkB,Xpar.Quadrant)
    #createTappingPoint(Xpar.EdgeB2,Xpar.EdgeB1,Xpar.SinkB,Xpar.SinkA,Xpar.Quadrant) #reverse edges and sinks to retain same 45 and 90 edge order
    #print(Xpar)
    t.write(str(Xpar.TapA.x)+" "+str(Xpar.TapA.y)+"\n")
    t.write(str(Xpar.TapB.x)+" "+str(Xpar.TapB.y)+"\n")

    f.write(str(Xpar.EdgeA1.x1)+" "+str(Xpar.EdgeA1.y1)+" "+str(Xpar.EdgeA1.x2)+" "+str(Xpar.EdgeA1.y2)+"\n")
    f.write(str(Xpar.EdgeA2.x1)+" "+str(Xpar.EdgeA2.y1)+" "+str(Xpar.EdgeA2.x2)+" "+str(Xpar.EdgeA2.y2)+"\n")
    #f.write(str(Xpar.EdgeB1.x1)+" "+str(Xpar.EdgeB1.y1)+" "+str(Xpar.EdgeB1.x2)+" "+str(Xpar.EdgeB1.y2)+"\n")
    #f.write(str(Xpar.EdgeB2.x1)+" "+str(Xpar.EdgeB2.y1)+" "+str(Xpar.EdgeB2.x2)+" "+str(Xpar.EdgeB2.y2)+"\n")
    """ for xPar in xPars:
        if xPar.TapA == sink1 or xPar.TapA == sink2:
            print("Removed sinkTwin: "+str(xPar.TapB))
            print("Removed xPar: "+str(xPar))
            tapSinks.remove(xPar.TapB)
            xPars.remove(xPar)
        elif xPar.TapB == sink1 or xPar.TapB == sink2:
            print("Removed sinkTwin: "+str(xPar.TapA))
            print("Removed xPar: "+str(xPar))
            tapSinks.remove(xPar.TapA)
            xPars.remove(xPar) """
    print("Removed sink1: "+str(sink1))
    tapSinks.remove(sink1)
    print("Removed sink2: "+str(sink2))
    tapSinks.remove(sink2)
    print("Added TapA: "+str(Xpar.TapA))
    tapSinks.append(Xpar.TapA)
    print("Added TapB: "+str(Xpar.TapB))
    #tapSinks.append(Xpar.TapB)
    xPars.append(Xpar)
    #break

t.close()
f.close()
#add last 2 edges
    
    
            

#iterate through all sinks and pair two closest
#generate x-parallelogram and 2 potential tapping points, all in datastructure
#if statement so 2 tapping points arent chosen to connect
#tie tapping points together, if one is selected remove x-flip option
#add edges to edge list only after one of the tapping points is connected
#Elmore delay, tapping point cap = first half wire length, downstream res and cap = wirelength and sink cap
#length of 45deg segment = manDist*sqrt(2)/2
#generate graph of length savings at each iteration, should trend up as points get farther apart