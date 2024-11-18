#!/usr/bin/python

from collections import namedtuple
import numpy as np
import matplotlib.pyplot as plt
import time
import sys

class Edge:
    def __init__ (self, origin=None):
        self.origin = origin
        self.weight = 1

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)
        
    def __str__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)
    

class Airport:
    def __init__ (self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = []
        self.routeHash = dict()
        self.outweight = 0
        self.pageIndex = len(airportList)

    def __repr__(self):
        return f"{self.code}\t{self.pageIndex}\t{self.name}"

edgeList = [] # list of Edge
edgeHash = dict() # hash of edge to ease the match
airportList = [] # list of Airport
airportHash = dict() # hash key IATA code -> Airport

def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r");
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5 :
                raise Exception('not an IATA code')
            a.name=temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code=temp[4][1:-1]
        except Exception as inst:
            pass
        else:
            cont += 1
            airportList.append(a)
            airportHash[a.code] = a
    airportsTxt.close()
    print(f"There were {cont} Airports with IATA code")


def readRoutes(fd):
    print("Reading Routes file from {0}".format(fd))
    routesTxt = open(fd, "r")
    cont = 0
    for line in routesTxt.readlines():
        try:
            temp = line.split(',')
            if len(temp[2]) != 3 or len(temp[4]) != 3:
                raise Exception('not an IATA code')
            if temp[2] not in airportHash or temp[4] not in airportHash:
                raise Exception('IATA code not found')
            a = airportHash[temp[2]]
            b = airportHash[temp[4]]
            if a.routeHash.get(b.code) != None:
                raise Exception('route already exists')
            a.routeHash[b.code] = len(a.routes)
            a.routes.append(Edge(b))
            a.outweight += 1
            cont += 1
        except Exception as inst:
            pass
    routesTxt.close()
    print(f"There were {cont} routes")
    
def getProbabilityMatrix():
    n = len(airportList)
    alpha = 0.15

    # Crear la matriz de probabilidad inicial
    P = np.zeros((n, n))
    for i, airport in enumerate(airportList):
        if airport.outweight == 0:
            # Nodos sin salidas distribuyen uniformemente el peso
            P[:, i] = 1 / n
        else:
            for edge in airport.routes:
                j = airportHash[edge.origin.code].pageIndex
                P[j][i] = 1 / airport.outweight

    # Incorporar el factor de amortiguación (damping factor)
    Pa = alpha * np.ones((n, n)) / n + (1 - alpha) * P
    return Pa


def computePageRanks():
    global history  # Usamos la variable global para almacenar los valores intermedios.
    
    P = getProbabilityMatrix()
    n = len(airportList)
    x = np.ones(n) / n  # Vector inicial uniformemente distribuido
    x = x.reshape((n, 1))
    
    # Almacenar las probabilidades en cada iteración
    history = [x.flatten()]  # Guardamos el estado inicial (iteración 0)
    
    iterations = 1
    threshold = 1e-6
    while True:
        x_new = np.dot(P, x)
        history.append(x_new.flatten())  # Guardar el estado en cada iteración
        if np.linalg.norm(x_new - x) < threshold:
            break
        x = x_new
        iterations += 1
    
    # Actualizamos los PageRanks finales
    for i, airport in enumerate(airportList):
        airport.pageRank = x[i][0]
    
    return iterations  # Ya no retornamos `history`, ya que es global



    
def outputPageRanks():
    print("Outputting Page Ranks")
    for airport in airportList:
        print(f"{airport.code}\t{airport.pageRank}")
        
import matplotlib.pyplot as plt

def plot_convergence(history):
    iterations = len(history)
    n_nodes = len(history[0])
    
    for i in range(n_nodes):
        node_history = [iteration[i] for iteration in history]
        plt.plot(range(iterations), node_history, label=f'Node {i}')
    
    plt.xlabel("Iteration")
    plt.ylabel("PageRank Value")
    plt.title("PageRank Convergence")
    plt.legend(title="Nodes", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(alpha=0.3)
    plt.figure(figsize=(12, 6))  # Ajusta el tamaño de la gráfica


    # Guardar la gráfica en un archivo
    plt.savefig("pagerank_convergence.png", dpi=300, bbox_inches="tight")
    print("Graph saved as 'pagerank_convergence.png'")



def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")
    time1 = time.time()
    iterations = computePageRanks()
    time2 = time.time()
    # outputPageRanks()
    print("#Iterations:", iterations)
    print("Time of computePageRanks():", time2-time1)
    print("Sum of Page Ranks:", sum([airport.pageRank for airport in airportList]))
    
    # Graficar la convergencia de los valores de PageRank
    plot_convergence(history)


if __name__ == "__main__":
    sys.exit(main())
