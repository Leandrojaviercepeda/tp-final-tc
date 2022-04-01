'''
Este archivo implementa el método Branch and Bound para encontrar la cobertura mínima de vértices para un Grafo de entrada dado.

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
### Running: python3 code/BnB.py -inst data/karate.graph -alg BnB -time 600 -seed 100
El valor inicial no se utilizará para la implementación de BnB.

La salida serán dos archivos: *.sol y *.trace creados en la carpeta Output del proyecto
*.sol --- registra el tamaño de la cobertura óptima de vértices y los nodos que contiene.
*.trace --- registrar todas las soluciones óptimas encontradas durante la búsqueda y el momento en que se encontró

### Help: python3 BnB.py --help
'''

import argparse
import networkx as nx
import operator
import time
import os


def parse(datafile):
    '''
    Funcion para analisis de archivos de entrada
    '''
    adj_list = []
    with open(datafile) as f:
        num_vertices, num_edges, weighted = map(int, f.readline().split())
        for i in range(num_vertices):
            adj_list.append(map(int, f.readline().split()))
    return adj_list


def create_graph(adj_list):
    '''
    Utiliza la lista de adyacencia para crear un Grafo
    '''
    G = nx.Graph()
    for i in range(len(adj_list)):
        for j in adj_list[i]:
            G.add_edge(i + 1, j)
    print(G)
    return G


def BnB(G, T):
    '''
    Funcion Branch and Bound para encontrar el VC minimo de un Grafo
    '''
    # HORA DE INICIO DEL REGISTRO
    start_time = time.time()
    end_time = start_time
    delta_time = end_time-start_time
    # lista de veces en que se encuentra la solución, tuple=(VC size,delta_time)
    times = []

    # INICIALIZAR SOLUCIÓN CONJUNTOS VC Y CONJUNTO FRONTERA A CONJUNTO VACÍO
    OptVC = []
    CurVC = []
    Frontier = []
    neighbor = []

    # ESTABLECER LÍMITE SUPERIOR INICIAL
    UpperBound = G.number_of_nodes()
    print('Initial UpperBound:', UpperBound)

    CurG = G.copy()  # hacer una copia de G
    # ordena el diccionario del grado de los nodos para encontrar el nodo con el grado más alto
    v = find_maxdeg(CurG)

    # ADJUNTAR (V,1,(parent,state)) Y (V,0,(parent,state)) A LA FRONTERA
    # tuplas de node,state,(parent vertex,parent vertex state)
    Frontier.append((v[0], 0, (-1, -1)))
    Frontier.append((v[0], 1, (-1, -1)))

    while Frontier != [] and delta_time < T:
        # establecer el nodo actual en el último elemento en Frontier
        (vi, state, parent) = Frontier.pop()

        backtrack = False

        if state == 0:  # si no se selecciona vi, estado de todos los vecinos=1
            neighbor = CurG.neighbors(vi)  # almacenar todos los vecinos de vi
            for node in list(neighbor):
                CurVC.append((node, 1))
                # El nodo está en VC, elimina vecinos de CurG
                CurG.remove_node(node)
        elif state == 1:  # si se selecciona vi, estado de todos los vecinos=0
            CurG.remove_node(vi)  # vi está en VC, elimine el nodo de G
        else:
            pass

        CurVC.append((vi, state))
        CurVC_size = VC_Size(CurVC)

        if CurG.number_of_edges() == 0:  # fin de la exploración, solución encontrada

            if CurVC_size < UpperBound:
                OptVC = CurVC.copy()
                print('Current Opt VC size', CurVC_size)
                UpperBound = CurVC_size
                times.append((CurVC_size, time.time()-start_time))
            backtrack = True

        else:  # solución parcial
            CurLB = Lowerbound(CurG) + CurVC_size

            if CurLB < UpperBound:  # worth exploring
                vj = find_maxdeg(CurG)
                # (vi,state) Es padre de vj
                Frontier.append((vj[0], 0, (vi, state)))
                Frontier.append((vj[0], 1, (vi, state)))
            else:
                # final de la ruta, dará como resultado una peor solución, retrocede al padre
                backtrack = True

        if backtrack == True:
            if Frontier != []:  # De lo contrario no más candidatos para procesar
                # padre del último elemento en Frontier (tuple of (vertex,state))
                nextnode_parent = Frontier[-1][2]

                # retroceder al nivel de nextnode_parent
                if nextnode_parent in CurVC:

                    id = CurVC.index(nextnode_parent) + 1
                    # deshacer los cambios desde el final de la copia de seguridad de CurVC hasta el nodo principal
                    while id < len(CurVC):
                        mynode, mystate = CurVC.pop()  # deshacer la adición a CurVC
                        # deshacer la eliminación de CurG
                        CurG.add_node(mynode)

                        # encuentra todas las aristas conectadas a vi en el Grafo G
                        # o los bordes que se conectaron a los nodos que no están en el conjunto de VC actual.

                        curVC_nodes = list(map(lambda t: t[0], CurVC))
                        for nd in G.neighbors(mynode):
                            if (nd in CurG.nodes()) and (nd not in curVC_nodes):
                                # esto agrega bordes de vi de regreso a CurG que posiblemente fueron eliminados
                                CurG.add_edge(nd, mynode)

                elif nextnode_parent == (-1, -1):
                    # retroceder al nodo raíz
                    CurVC.clear()
                    CurG = G.copy()
                else:
                    print('error in backtracking step')

        end_time = time.time()
        delta_time = end_time-start_time
        if delta_time > T:
            print('Cutoff time reached')

    return OptVC, times


def find_maxdeg(g):
    '''
    Funcion para encontrar el vertice con grado maximo en el Grafo restante
    '''
    deglist = g.degree()
    deglist_sorted = sorted(deglist, reverse=True, key=operator.itemgetter(
        1))  # ordenar en orden descendente de grado de nodo
    v = deglist_sorted[0]  # tupla - (node,degree)
    return v


def Lowerbound(graph):
    '''
    Funcion para estimar el limite inferior
    '''
    lb = graph.number_of_edges() / find_maxdeg(graph)[1]
    lb = ceil(lb)
    return lb


def ceil(d):
    '''
    Funcion para devolver el entero mínimo que es mayor que d
    '''
    if d > int(d):
        return int(d) + 1
    else:
        return int(d)


def VC_Size(VC):
    '''
    Funcion para calcular el tamaño de la cubierta VC (numero de nodos con state=1)
    '''
    # VC es una lista de tuplas, donde cada tupla = (node_ID, state, (node_ID, state)) vc_size es el número de nodos que tienen state == 1
    vc_size = 0
    for element in VC:
        vc_size = vc_size + element[1]
    return vc_size

##################################################################
# MAIN BODY OF CODE


def main(inputfile, output_dir, cutoff, randSeed):
    # LEER EL ARCHIVO DE ENTRADA EN EL GRAPH
    adj_list = parse(inputfile)
    g = create_graph(adj_list)

    Sol_VC, times = BnB(g, cutoff)

    # ELIMINAR NODOS FALSOS (ESTADO=0) EN SoL_VC OBTENIDO
    for element in Sol_VC:
        if element[1] == 0:
            Sol_VC.remove(element)

    # ESCRIBIR SOLUCIÓN Y ARCHIVOS DE SEGUIMIENTO A "*.SOL" Y '*.TRACE" RESPECTIVAMENTE
    inputdir, inputfile = os.path.split(inputfile)

    # ESCRIBIR ARCHIVOS SOL
    with open(inputfile.split('.')[0] + '_BnB_'+str(cutoff)+'.sol', 'w') as f:
        f.write('%i\n' % (len(Sol_VC)))
        f.write(','.join([str(x[0]) for x in Sol_VC]))

    # ESCRIBIR ARCHIVOS DE SEGUIMIENTO
    with open(inputfile.split('.')[0] + '_BnB_'+str(cutoff)+'.trace', 'w') as f:
        for t in times:
            f.write('%.2f,%i\n' % ((t[1]), t[0]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Input parser for BnB')
    parser.add_argument('-inst', action='store', type=str,
                        required=True, help='Inputgraph datafile')
    parser.add_argument('-alg', action='store', default=1000,
                        type=str, required=True, help='Name of algorithm')
    parser.add_argument('-time', action='store', default=1000, type=int,
                        required=True, help='Cutoff running time for algorithm')
    parser.add_argument('-seed', action='store', default=1000,
                        type=int, required=False, help='random seed')
    args = parser.parse_args()

    algorithm = args.alg
    graph_file = args.inst
    output_dir = './output'
    cutoff = args.time
    randSeed = args.seed
    main(graph_file, output_dir, cutoff, randSeed)
