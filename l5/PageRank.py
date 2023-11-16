#!/usr/bin/python

from collections import namedtuple
import time
import sys

class Edge:
    def __init__ (self, origin=None):
        self.origin = origin
        self.weight = 1.0

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)

    ## write rest of code that you need for this class

class Airport:
    def __init__ (self, iden=None, name=None, pageIndex=None):
        self.code = iden
        self.name = name
        self.routeHash = dict()
        self.outweight = 0.0
        self.pageIndex = pageIndex

    def __repr__(self):
        return f"{self.code}\t{self.pageIndex}\t{self.name}"
    
    def addRoute (self, origin):
        if origin in self.routeHash:
            self.routeHash[origin].weight += 1
        else:
            newEdge = Edge(origin)
            self.routeHash[origin] = newEdge



airportList = [] # list of Airport
airportHash = dict() # hash key IATA code -> Airport

def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r", encoding="utf-8")
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5 :
                raise Exception('not an IATA code')
            a.name=temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code=temp[4][1:-1]
            a.pageIndex = cont
        except Exception as inst:
            pass
        else:
            cont += 1
            airportList.append(a)
            airportHash[a.code] = a
    airportsTxt.close()
    print(f"There were {cont} Airports with IATA code")


def readRoutes(fd):
    print("Reading Routes file from {fd}")
    routesTxt = open(fd, "r", encoding="utf-8")
    cont = 0
    for line in routesTxt.readlines():
        try:
            info = line.split(',')
            
            origin = info[2]
            dest = info[4]

            if len(origin) != 3 or len(dest) != 3:
                raise Exception ("Route's airports not in IATA code")
            
            if origin in airportHash and dest in airportHash:
                airportHash[dest].addRoute(origin) 
                airportHash[origin].outweight += 1
            else:
                raise Exception ('origin or destination not found')
                
        except Exception as inst:
            pass
        else:
            cont += 1

def computePageRanks():
    n = len(airportList) # number of vertices in G
    P = [1/n]*n # vector of length n and sum 1 (the all 1/n vector)
    L =  0.8 # the chosen damping factor, between 0 and 1
    tol = 1e-16  # tolerance for the convergence, we choose 0.00000001 because the sake of science
    iterations = 0  # count of iterations
    maxIterations = 1000

    disconnected = 0
    for airport in airportList:
        if airport.outweight == 0:
            disconnected += 1

    discConstWeight = disconnected*(L/float(n-1))
    discVarWeight = 1/n

    while True:
        iterations += 1
        Q = [0] * n  # new PageRank values
        discWeight = discConstWeight * discVarWeight
        for airport in airportList:
            sumPR = 0

            for edge in airport.routeHash.values():  # itetarete on incoming routes
                originAirport = airportHash[edge.origin]
                
                if originAirport.outweight > 0:
                    sumPR += P[originAirport.pageIndex] * edge.weight / originAirport.outweight

            Q[airport.pageIndex] = (1 - L) / n + L * sumPR + discWeight  # new PageRank value for airport

        discVarWeight = (1 - L) / n + discWeight

        # has converged?
        if max(abs(Q[i] - P[i]) for i in range(n)) < tol:
            break

        P = Q

        print("Sumatory of iteration", iterations, ":" , sum(i for i in P))    # Check if P sums 1 each iteration


        if iterations >= maxIterations:  # if not converged and exceeded max_iterations exit
            break

    return iterations, P  # return the number of iterations and the final PageRanks values

def outputPageRanks(Q):
    # create a list of tuples (airport code, PageRank value)
    airportRanks = [(airportList[i].code, Q[i]) for i in range(len(Q))]

    # sort the list by PageRank in descending order
    airportRanks.sort(key=lambda x: x[1], reverse=True)

    # prepare the output text
    output = "Airport Code\tPageRank\n"
    for code, rank in airportRanks:
        output += f"{code}\t{rank}\n"

    # write the output text on the file
    with open("airport_pageranks.txt", "w") as file:
        file.write(output)

    print("PageRanks written to airport_pageranks.txt")

def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")
    time1 = time.time()
    iterations, Q = computePageRanks()
    time2 = time.time()
    outputPageRanks(Q)
    print("#Iterations:", iterations)
    print("Time of computePageRanks():", time2-time1)


if __name__ == "__main__":
    sys.exit(main())
