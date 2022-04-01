#!/usr/bin/env python3
'''
Este archivo implementa un Algoritmo Genetico para encontrar una aproximacion a la cobertura mínima de vértices para un Grafo de entrada dado.

Autor: Leandro Cepeda.

Instrucciones: La estructura de la carpeta es la siguiente: El directorio del proyecto contiene [código, datos, salida].
Los archivos de código deben pegarse en la carpeta de código.
Los archivos de salida son generados automáticamente por los scripts.
Los archivos de datos están formados por números separados por espacios. La primera fila del archivo debe representar los siguientes datos: número de vértices, número de aristas, pesos.
El resto de las filas del archivo representan los siguientes datos:
i = row number = vertex; j = value in row = edge; x = weight

Ejemplo:
* Para el siguiente Graph:

  - 2 - 4 - 6
1   |   |
  - 3 - 5

La estructura del archivo sería la siguiente:
6 7 0
2 3
1 3 4
1 2 5
2 5 6
3. 4
4

Language: Python 3
# Running: python3 code/Approx.py -inst data/karate.graph -alg Approx -time 600 -seed 100
El valor inicial no se utilizará para la implementación de Approx.

La salida serán dos archivos: *.sol y *.trace creados en la carpeta Output del proyecto
*.sol --- registra el tamaño de la cobertura óptima de vértices y los nodos que contiene.
*.trace --- registrar todas las soluciones óptimas encontradas durante la búsqueda y el momento en que se encontró

# Running: python3 n_reinas_ag.py -ti [tamaño individuo] -tp [tamaño poblacion] -g [generaciones] -p [pressure - opcional - default=3] -pm [porcentaje de mutacion] -pc [porcentaje de cruza]

# Help: python3 Approx.py --help

# Doc:
En los AG:
- Poblacion: se define como población al conjunto de soluciones posibles.
- Individuo: a cada una de las soluciones del espacio pareto.
- Función de fitness: a los mecanismos de evaluación sistemática de los individuos para los fines evolutivos.
- En todos los casos de AG  el objeto final es hallar una optimización y es imprescindible aprender a codificar
  en los genomas al problema, de lo contrario la solución nunca será apropiada para el problema en cuestión.

1.Determinación del genoma:
- Definiremos como el Grafo que representa al problema np completo Minimum Vertex cover, un Grafo "G".

2.Determinación de la población:
- Cantidad de individuos de la población.
- Porcentaje de mutación.
- Porcentaje de cruza.
- Cantidad de generaciones que permitirá al algoritmo evolucionar.

3.Determine la función de fitness (FF):
- Recuerde que debe medir la distancia numérica entre cada individuo y la solución buscada
- Recuerde punificar las soluciones que violan las reglas.
- Recuerde la condición de terminación.

4.Determine la función de selección:
- Para simplificar el algoritmo escriba sólo la selección de individuos en base a su fitness.

5.Determine la función de cruza:
- Para simplificar el algoritmo se pondrá solo un punto de corte.
- Además la cruza es con reemplazo, es decir, un algoritmo donde los padres ya no son seleccionables
  si han sido usados para cruzarse durante esa generación.

6.Determine la función de mutación:
- Para simplificar el algoritmo, consiste sólo en el cambio a otra casilla disponible,
  siempre que supere un umbral de XX %. Es decir, una vez determinado que un par de individuos se cruzarán,
  se obtiene un número al azar  ntre 0 y 99, y sólo se efectúa la cruza si dicho número supera el umbral de XX.
'''

import random
import numpy
import matplotlib.pyplot as plt
import argparse


def crear_individuo(fileline):
    """
    Devuelve un individio a partir de una fila del archivo de entrada.
    """

    # TODO: leer fila del archivo y devolver individuo correspondiente
    return list(map(int, fileline.readline().split()))


def crear_poblacion(archivo):
    """
    Devuelve una poblacion de individuos, partiendo de un archivo de entrada.
    """
    adj_list = []
    with open(archivo) as f:
        num_vertices, num_edges, weighted = map(int, f.readline().split())
        for i in range(num_vertices):
            adj_list.append(crear_individuo(f))
    return adj_list


def evaluar_aptitud(individuo):
    """
Evalua la aptitud del individuo recibido como parámetro. Para este caso de n-reinas,
    es necesario evaluar si las reinas ubicadas en el tablero se amenazan entre si.

Devuelve un valor entero que corresponde al numero de amenazas para cada individuo.
    """
    contDA1 = 0
    contDA2 = 0
    contDB1 = 0
    contDB2 = 0
    idoGlobal = 0

    # contamos las coinsidencias en el mismo renglon
    for i in range(0, len(individuo)):
        # cuenta coinsidencias en el condidato por renglon
        auxcont = individuo.count(i)
        if auxcont > 1:  # si son mas de dos entonces se atacan
            idoGlobal = idoGlobal + auxcont

    for i in range(0, len(individuo)):
        auxcont = 0
        for j in range(0, i+1):
            if individuo[j] == i-j:
                auxcont = auxcont + 1
        if auxcont > 1:
            contDA1 = contDA1 + auxcont

    for k in range(1, len(individuo)):
        auxcont = 0
        i = len(individuo) - k
        for j in range(i, len(individuo)):
            if individuo[j] == (len(individuo)-1) - (j-i):
                auxcont = auxcont + 1
        if auxcont > 1:
            contDA2 = contDA2 + auxcont

    for i in range(0, len(individuo)):
        auxcont = 0
        for j in range(0, len(individuo)):
            if individuo[j] == (len(individuo)-1)-(i-j):
                auxcont = auxcont + 1
        if auxcont > 1:
            contDB1 = contDB1 + auxcont

    for i in range(1, len(individuo)):
        auxcont = 0
        for j in range(i, len(individuo)):
            if individuo[j] == j-i:
                auxcont = auxcont + 1
        if auxcont > 1:
            contDB2 = contDB2 + auxcont

    # print(idoGlobal, contDA1, contDA2, contDB1, contDB2)
    idoGlobal = idoGlobal + contDA1 + contDA2 + contDB1 + contDB2

    return idoGlobal


def calcular_fitness(individuo):
    return evaluar_aptitud(individuo)


def seleccion_individuos(poblacion, pressure=3):
    """
    Devuelve una lista de individuos seleccionados por mejor fitness, limitada por pressure.
    """

    # Calcula el fitness de cada individuo, y lo guarda en pares ordenados de la forma (5 , [1,2,1,1,4,1,8,9,4,1])
    evaluados = [(calcular_fitness(i), i) for i in poblacion]

    # Ordena los pares ordenados y se queda solo con el array de valores
    poblacion_evaluada = [i[1] for i in sorted(evaluados)]

    nueva_poblacion = [i for i in poblacion_evaluada]

    # Esta linea selecciona los 'n' individuos del final, donde n viene dado por 'pressure'
    seleccionados = numpy.copy(poblacion_evaluada[:pressure])

    # Convierte a la lista en inmutable
    seleccionados.flags.writeable = False

    return nueva_poblacion, seleccionados


def cruza(poblacion, seleccionados, porcentaje_cruza, pressure=3):
    """
    Devuelve una nueva poblacion en la que los individuos menos aptos son cruzados
    a partir de individuos padres mas aptos. Esta nueva poblacion se crea a partir
    de la recibida como parametro, ademas es posible definirse la cantidad de elementos
    aptos a seleccionar para posteriormente realizar la cruza, a partir del parametro "pressure"
    """

    nueva_poblacion = [i for i in poblacion]

    # Cruza los individuos que fueron seleccionados como padres
    for i in range(0, pressure):
        # Se elige un punto para hacer el intercambio
        punto = random.randint(1, len(seleccionados[0])-1)

        # Se eligen dos padres
        padres = seleccionados[numpy.random.choice(
            seleccionados.shape[0], size=2, replace=False), :]

        # Se mezcla el material genetico de los padres en cada nuevo individuo
        nueva_poblacion[i][:punto] = padres[0][:punto]
        nueva_poblacion[i][punto:] = padres[1][punto:]

    # Cruza los individuos que no fueron seleccionados como padres
    for i in range(pressure, len(nueva_poblacion)):
        if random.random() <= porcentaje_cruza:
            # Se elige un punto para hacer el intercambio
            punto = random.randint(1, len(seleccionados[0])-1)

            # Se eligen dos padres
            padres = seleccionados[numpy.random.choice(
                seleccionados.shape[0], size=2, replace=False), :]

            # Se mezcla el material genetico de los padres en cada nuevo individuo
            nueva_poblacion[i][:punto] = padres[0][:punto]
            nueva_poblacion[i][punto:] = padres[1][punto:]

    return nueva_poblacion


def mutacion(poblacion, porcentaje_mutacion, pressure=3):
    """
    Devuelve una nueva poblacion con los individuos de la poblacion recibida 
    como parametro ya mutados. Se debe tener en cuenta que la mutacion es posterior 
    a la cruza. El criterio de mutacion para el caso es el intercambio de dos genes 
    seleccionados al azar.
"""
    nueva_poblacion = [i for i in poblacion]

    for i in range(len(nueva_poblacion)):

        # Cada individuo de la poblacion (menos los padres) tienen una probabilidad de mutar
        if random.random() <= porcentaje_mutacion:

            # Se elige un punto al azar
            punto1 = random.randint(0, len(nueva_poblacion[0])-1)

            # Se elige un valor al azar
            valor = random.randint(0, len(nueva_poblacion[0])-1)

            while nueva_poblacion[i][punto1] == valor:
                valor = random.randint(0, len(nueva_poblacion[0])-1)

            # Se aplica la mutacion
            nueva_poblacion[i][punto1] = valor

    return nueva_poblacion


def mejor_individuo_poblacion_final(poblacion_final):

    mejor_fitness = 10

    for i in poblacion_final:
        if evaluar_aptitud(i) <= mejor_fitness:
            mejor_fitness = evaluar_aptitud(i)
            mejor_individuo = i

    return mejor_individuo


def algoritmo_genetico(genoma, generaciones, porcentaje_mutacion, porcentaje_cruza, pressure=3):

    poblacion_inicial = genoma
    print(f'\nPOBLACION INICIAL: {poblacion_inicial}\n')

    poblacion_final = None
    for i in range(0, generaciones):

        poblacion_por_mejor_FF, seleccionados = seleccion_individuos(
            poblacion_inicial, pressure)
        poblacion_cruzada = cruza(
            poblacion_por_mejor_FF, seleccionados, porcentaje_cruza, pressure)
        poblacion_final = mutacion(
            poblacion_cruzada, porcentaje_mutacion, pressure)

    return poblacion_final


def plotear_solucion(individuo):
    print(f'Individuo: {individuo}')
    plt.figure()
    x = range(len(individuo))
    x = numpy.array(x)
    y = numpy.array(individuo)
    x = x + 0.5
    y = y + 0.5
    plt.scatter(x, y)
    plt.xlim(0, len(individuo))
    plt.ylim(0, len(individuo))
    plt.xticks(x-0.5)
    plt.yticks(x-0.5)
    plt.grid(True)
    plt.title(f"Individuo solucion: {individuo}")
    plt.show()


def main(genoma, generaciones, porcentaje_mutacion, porcentaje_cruza, pressure, corridas):
    soluciones = []

    for i in range(corridas):
        print(f'\nEJECUCION N°: {i+1}')

        poblacion_final = algoritmo_genetico(
            genoma, generaciones, porcentaje_mutacion, porcentaje_cruza, pressure)
        print(
            f'POBLACION FINAL (individuo, fitness): {[(i, evaluar_aptitud(i)) for i in poblacion_final]}\n')

        mejor_individuo = mejor_individuo_poblacion_final(poblacion_final)
        print(
            f'MEJOR INDIVIDUO ENCONTRADO: {mejor_individuo}, SU FITNESS ES: {evaluar_aptitud(mejor_individuo)}\n')

        if evaluar_aptitud(mejor_individuo) == 0:
            soluciones.append(mejor_individuo)

    print(f'\nSe encontraron {len(soluciones)} soluciones: {soluciones}\n')

    if len(soluciones) > 0:
        for s in soluciones:
            plotear_solucion(s)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Analizador de entrada para Approx', description='Minimum vertex cover approximation')
    parser.add_argument('-inst', action='store', type=str,
                        required=True, help='Archivo de datos de Grafo de entrada')
    parser.add_argument('-g', help='Cantidad de generaciones', type=int)
    parser.add_argument('-pm', help='Porcentaje de mutacion', type=float)
    parser.add_argument('-pc', help='Porcentaje de cruza', type=float)
    parser.add_argument(
        '-p', help='Pressure (candidatos a ser padres - min(2) - max(tp))', type=int, default=3)
    parser.add_argument('-c', help='Cantidad de corridas', type=int)

    args = parser.parse_args()

    GRAP_FILE = args.inst
    GENOMA = crear_poblacion(GRAP_FILE)
    GENERACIONES = args.g
    PRESSURE = args.p
    PORCENTAJE_MUTACION = args.pm
    PORCENTAJE_CRUZA = args.pc
    CORRIDAS = args.c

    print(f'\n{parser.prog} - {parser.description}\n')

    print(f'GENOMA: {GENOMA}')
    print(f'GENERACIONES: {GENERACIONES}')
    print(f'PORCENTAJE_MUTACION: {PORCENTAJE_MUTACION}')
    print(f'PRESSURE: {PRESSURE}')

    main(GENOMA, GENERACIONES, PRESSURE,
         PORCENTAJE_MUTACION, PORCENTAJE_CRUZA, CORRIDAS)
