#!/usr/bin/python

from collections import namedtuple
import numpy as np
import matplotlib.pyplot as plt
import time
import sys
from collections import defaultdict

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
    alpha = 0.05

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
    
    return iterations 



    
def outputPageRanks():
    print("Outputting Page Ranks")
    for airport in airportList:
        print(f"{airport.code}\t{airport.pageRank}")
        


def plot_convergence(history):
    iterations = len(history)
    n_nodes = len(history[0])
    sorted_indices = np.argsort(history[-1])  # Ordenar los nodos por su PageRank final
    step = max(1, n_nodes // 10)  # Dividir el total de nodos por 10, asegurando que el paso sea al menos 1
    selected_indices = sorted_indices[::step][:10]  # Seleccionar cada x-ésimo nodo, hasta un máximo de 10
    
    for i in selected_indices:
        node_history = [iteration[i] for iteration in history]
        plt.plot(range(iterations), node_history, label=f'Node {i}')
    
    plt.xlabel("Iteration")
    plt.ylabel("PageRank Value")
    plt.title("PageRank Convergence")
    plt.legend(title="Nodes", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(alpha=0.3)

    # Guardar la gráfica en un archivo
    plt.savefig("pagerank_convergence_1.png", dpi=300, bbox_inches="tight")
    
def plot_pagerank_distribution(airportList):
    # Obtener los valores de PageRank
    pageranks = [airport.pageRank for airport in airportList]
    
    # Crear un histograma de los valores de PageRank
    plt.figure(figsize=(10, 6))
    plt.hist(pageranks, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    
    # Agregar etiquetas y título
    plt.xlabel("PageRank Value")
    plt.ylabel("Frequency")
    plt.title("Distribution of PageRank Across Nodes")
    plt.yscale('log')  # Aplicar escala logarítmica al eje y
    plt.grid(alpha=0.3)
    
    # Guardar la gráfica como archivo
    plt.savefig("pagerank_distribution_1.png", dpi=300, bbox_inches="tight")
    
    
def plot_country_pagerank_distribution(airportList):
    from collections import defaultdict
    import numpy as np
    import matplotlib.pyplot as plt

    # Crear un diccionario para almacenar la suma de PageRank por país
    country_pagerank = defaultdict(float)

    # Sumar los PageRanks por país
    for airport in airportList:
        country = airport.name.split(", ")[-1]
        country_pagerank[country] += airport.pageRank

    # Calcular el porcentaje de importancia de cada país
    total_pagerank = sum(country_pagerank.values())
    country_importance = {country: (pagerank / total_pagerank) * 100 for country, pagerank in country_pagerank.items()}

    # Ordenar los países por importancia
    sorted_countries = sorted(country_importance.items(), key=lambda x: x[1], reverse=True)

    # Seleccionar los principales países
    top_countries = sorted_countries[:10]  # Top 10 países
    labels, values = zip(*top_countries)

    # Convertir valores a proporciones angulares
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values_scaled = np.array(values)  # Escalar si es necesario

    # Configurar el gráfico polar
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    bars = ax.bar(angles, values_scaled, width=0.3, color='grey', edgecolor='black', alpha=0.8)

    # Resaltar las primeras barras
    for i, bar in enumerate(bars[:3]):  # Destacar el Top 3
        bar.set_color("orange")
        bar.set_alpha(0.9)

    # Agregar etiquetas
    ax.set_yticklabels([])
    ax.set_xticks(angles)
    ax.set_xticklabels([f"{label}\n{value:.0f}%" for label, value in top_countries], fontsize=12, color='black')

    # Estilo del título
    plt.title("Percentage of Importance by Country (PageRank)", size=15, color='black', y=1.1)
    plt.tight_layout()

    # Guardar el gráfico
    plt.savefig("country_pagerank_radial_1.png", dpi=300, bbox_inches="tight")


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
    print("Top 10 airports by PageRank:")
    for airport in sorted(airportList, key=lambda x: x.pageRank, reverse=True)[:10]:
        print(f"{airport.code}\t{airport.pageRank:.6f}\t{airport.name}")
    
    print("Bottom 10 airports by PageRank:")
    for airport in sorted(airportList, key=lambda x: x.pageRank)[:10]:
        print(f"{airport.code}\t{airport.pageRank:.6f}\t{airport.name}")
    
    # Graficar la convergencia de los valores de PageRank
    plot_convergence(history)
    plot_pagerank_distribution(airportList)
    plot_country_pagerank_distribution(airportList)


if __name__ == "__main__":
    sys.exit(main())
