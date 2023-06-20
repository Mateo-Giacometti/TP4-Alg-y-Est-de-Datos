from graph import Graph
import csv
from itertools import combinations
from collections import deque
import heapq
from tqdm import tqdm
import os
import pickle
import time
import random
MOVIE_TITLE_TYPE = "movie"
MOVIE_COLUMNS = ["tconst", "titleType", "primaryTitle"]
PRINCIPALS_COLUMNS = ["nconst", "category"]
MOVIES_DATA_PATH = "./datasets/title-basics-f.tsv"
ACTORS_DATA_PATH = "./datasets/title-principals-f.tsv"
ACTORS_NAMES_PATH = "./datasets/name-basics-f.tsv"


def read_data(movies_file, actors_file, actors_name_file):
    print("Reading data")
    if os.path.exists('data.pickle'):
        print("Reading from pre-saved file")
        try:
            with open('data.pickle', 'rb') as file:
                movies_by_id, actors_by_movie, actor_names_by_id = pickle.load(file)
                return movies_by_id, actors_by_movie, actor_names_by_id
        except Exception:
            pass
    movies_by_id = {}
    with open(movies_file, "r", newline="", encoding="utf-8") as file1:
        reader = csv.DictReader(file1, delimiter="\t")
        for row in reader:
            if row["titleType"] == MOVIE_TITLE_TYPE:
                movies_by_id[row['tconst']] = {'primaryTitle': row['primaryTitle']}

    actors_ids = set()
    actors_by_movie = {m: set() for m in movies_by_id.keys()}
    with open(actors_file, "r", newline="", encoding="utf-8") as file2:
        reader = csv.DictReader(file2, delimiter="\t")
        for row in reader:
            if row["tconst"] in actors_by_movie:
                actors_by_movie[row["tconst"]].update([row["nconst"]])
                actors_ids.update([row["nconst"]])

    actor_names_by_id = {}
    with open(actors_name_file, "r", newline="", encoding="utf-8") as file2:
        reader = csv.DictReader(file2, delimiter="\t")
        for row in reader:
            if row["nconst"] in actors_ids:
                actor_names_by_id[row["nconst"]] = row["primaryName"]

    with open('data.pickle', 'wb') as file:
        pickle.dump((movies_by_id, actors_by_movie, actor_names_by_id), file)

    return movies_by_id, actors_by_movie, actor_names_by_id


def load_graph(movies_by_id, actors_by_movie, actor_names_by_id) -> Graph:
    """
    Loads the graph
    :param movies_by_id: the movies data by id as dict
    :param actors_by_movie: the actors data by movie
    :param actor_names_by_id: the actors names by their ids
    :return: a Graph
    """
    graph = Graph()
    print("Loading graph")

    for movie_id in movies_by_id.keys():
        movie_title = movies_by_id[movie_id]['primaryTitle']
        for actor1, actor2 in combinations(actors_by_movie[movie_id], 2):
            if not graph.vertex_exists(actor1):
                graph.add_vertex(actor1, actor_names_by_id.get(actor1, "ERROR"))
            if not graph.vertex_exists(actor2):
                graph.add_vertex(actor2, actor_names_by_id.get(actor2, "ERROR"))
            existing_data = set()
            if graph.edge_exists(actor1, actor2):
                existing_data = graph.get_edge_data(actor1, actor2)
            graph.add_edge(vertex1=actor1, vertex2=actor2,
                           data={movie_title} | existing_data)
    
    print("Graph loaded")
    return graph

"""
Ejercicio 1

Nos interesa entender cuan “particionado” esta nuestro grafo. Con esta información podríamos “clusterizar” a nuestra comunidad de artistas. 
Se pide hallar la cantidad de componentes conexas que lo componen, y asignar a cada vértice en una misma componente conexa un mismo identificador. 
Una componente conexa se define como un subgrafo maximal conexo. ¿Cuántas componentes conexas hay? ¿Cuál es la segunda componente conexa más grande? 
¿Cúal es la más chica de todas?

"""

def find_connected_components(graph: Graph) -> dict:
    """	
    Finds the connected components of a graph.

    Parameters
    ----------
    graph : Graph
        The graph to find the connected components.
    
    Returns
    -------
    dict
        A dictionary with the format {component_id: [vertex1, vertex2, ...]}.
    """
    visited = set()
    graph_components = []
    for vertex in graph.get_graph_elements():
        if vertex not in visited:
            component = []
            stack = deque()
            stack.append(vertex)
            while stack:
                current_vertex = stack.pop()
                if current_vertex not in visited:
                    visited.add(current_vertex)
                    component.append(current_vertex)
                    for neighbor in graph.get_neighbors(current_vertex):
                        stack.append(neighbor)
            graph_components.append(component)
    graph_components.sort(key=lambda x: len(x), reverse=True)
    graph_components_dict = {f"Component {idx+1}": component for idx, component in enumerate(graph_components)}
    return graph_components_dict


"""
Ejercicio 2

Dado un artista, queremos conocer el camino mínimo (que sume la minima cantidad de colaboraciones totales) a todos los demás artistas.

"""

def find_shortest_path_to_all(graph: Graph, vertex_id: str) -> dict:
    """
    Finds the shortest path from a vertex to all the other vertices in the graph.

    Parameters
    ----------
    graph : Graph
        The graph to find the shortest path.
    vertex_id : str
        The vertex to start the search from.
    
    Returns
    -------
    dict
        A dictionary with the format {vertex_id: {'distance': distance, 'path': [vertex1, vertex2, ...]}}.
    """
    results = {vertex: {'distance': float('inf'), 'path': []} for vertex in graph.get_graph_elements()}
    results[vertex_id]['distance'] = 0
    results[vertex_id]['path'] = [vertex_id]
    heap = [(0, vertex_id)]
    while heap:
        current_distance, current_node = heapq.heappop(heap)
        if current_distance > results[current_node]['distance']: continue
        for neighbor in graph.get_neighbors(current_node):
            weight = graph.get_edge_data(current_node, neighbor)
            new_distance = results[current_node]['distance'] + len(weight)
            if new_distance < results[neighbor]['distance']:
                results[neighbor]['distance'] = new_distance
                results[neighbor]['path'] = results[current_node]['path'] + [neighbor]
                heapq.heappush(heap, (new_distance, neighbor))
    return results

"""	
Ejercicio 3

Queremos conocer el camino minimo (con pesos) entre cualquier par de artistas. ¿Cuánto demora calcular esto?

"""

def find_shortest_path_between_vertices(graph: Graph, start_vertex: str, end_vertex: str) -> tuple: #Mirar documentación
    """
    Finds the shortest path between two vertices.

    Parameters
    ----------
    graph : Graph
        The graph to find the shortest path.
    start_vertex : str
        The vertex to start the search from.
    end_vertex : str
        The vertex to end the search.

    Returns
    -------
    tuple
        A tuple with the format (distance, list with the vertices that make up the path, execution time).
        
    """
    start_time = time.time()
    short_paths = find_shortest_path_to_all(graph, start_vertex)
    the_path = short_paths[end_vertex]
    end_time = time.time()
    elapsed_time = end_time - start_time
    return the_path['distance'], the_path['path'], elapsed_time

"""
Ejercicio 4

¿Cuál es el diámetro del grafo para la componente conexa principal? Utilice máximo 15 minutos para calcularlo, si no le es posible calcularlo de forma exacta, indique:
a) ¿Cuánto demoraría hacerlo de forma exacta?
b) Estime el diámetro del grafo utilizando el tiempo dado

"""

def find_shortest_path_to_all_without_weights(graph: Graph, vertex_id: str) -> dict:
    """
    Finds the shortest path from a vertex to all the other vertices in the graph without considering the weights.

    Parameters
    ----------
    graph : Graph
        The graph to find the shortest path.
    vertex_id : str
        The vertex to start the search from.
    
    Returns
    -------
    dict
        A dictionary with the format {vertex_id: {'distance': distance, 'path': [vertex1, vertex2, ...]}}.
    """
    visited = set()
    results = {vertex: {'distance': float('inf'), 'path': []} for vertex in graph.get_graph_elements()}
    results[vertex_id]['distance'] = 0
    results[vertex_id]['path'] = [vertex_id]
    queue = deque([(vertex_id, 0)])
    while queue:
        current_node, current_distance = queue.popleft()
        if current_node in visited: continue
        visited.add(current_node)
        for neighbor in graph.get_neighbors(current_node):
            new_distance = current_distance + 1
            if new_distance < results[neighbor]['distance']:
                results[neighbor]['distance'] = new_distance
                results[neighbor]['path'] = results[current_node]['path'] + [neighbor]
                queue.append((neighbor, new_distance))
    return results


def find_diameter(graph: Graph, graph_connected_component: str, execution_time: int = 900): 
    """
    Finds the diameter of a graph connected component (exact or approximate).

    Parameters
    ----------
    graph : Graph
        The graph to find the diameter.
    graph_connected_component : str
        The connected component to find the diameter.
    execution_time : int
        The time to find the diameter (default 900 seconds).
    
    Returns
    -------
    tuple
        A tuple with the format (diameter of the connected component, total time, time to finish).
    """
    diameter = 0
    number_of_vertices_analyzed = 0
    total_time = 0
    time_to_finish = 0
    connected_component = find_connected_components(graph)[graph_connected_component]
    random.shuffle(connected_component)
    start_time = time.time()
    for vertex in connected_component:
        if time.time() - start_time >= execution_time: break
        number_of_vertices_analyzed += 1
        separations = find_shortest_path_to_all_without_weights(graph, vertex)
        for separation in separations.values():
            if separation['distance'] == float('inf'): continue
            if separation['distance'] > diameter: diameter = separation['distance']    
    end_time = time.time()
    total_time = len(connected_component)*((end_time - start_time)/number_of_vertices_analyzed)
    time_to_finish = total_time - (end_time - start_time)
    return diameter, total_time, time_to_finish

"""
Ejercicio 5

¿Cuál es, en la componente conexa principal, el promedio de separaciones para cada actor y para todos en general? De ser imposible de calcular estimelo.

"""

def average_separations(graph: Graph, graph_connected_component: str, execution_time: int = 900) -> tuple:
    """
    Finds the average separations for each vertex and for all the vertices in the graph connected component.

    Parameters
    ----------
    graph : Graph
        The graph to find the average separations.
    graph_connected_component : str
        The connected component to find the average separations.
    execution_time : int
        The time to find the average separations (default 900 seconds).

    Returns
    -------
    tuple
        A tuple with the format (average separations for each vertex, average separations for all the vertices, total time, time to finish).
    """
    number_of_vertices_analyzed = 0
    total_time = 0
    time_to_finish = 0
    total_average = 0
    average_per_vertex = {}
    connected_component = find_connected_components(graph)[graph_connected_component]
    random.shuffle(connected_component)
    start_time = time.time()
    for vertex in connected_component:
        if time.time() - start_time >= execution_time: break
        number_of_vertices_analyzed += 1
        vertex_separation = 0
        separations = find_shortest_path_to_all_without_weights(graph, vertex)
        for separation in separations.values():
            if separation['distance'] == float('inf'): continue
            vertex_separation += separation['distance']
        average_per_vertex[vertex] = vertex_separation / len(connected_component)
        total_average += vertex_separation / len(connected_component)
    end_time = time.time()
    total_average = total_average / len(average_per_vertex)
    total_time = len(connected_component)*((end_time - start_time)/number_of_vertices_analyzed)
    time_to_finish = total_time - (end_time - start_time)
    return average_per_vertex, total_average, total_time, time_to_finish



def main():
    movies_by_id, actors_by_movie, actor_names_by_id = read_data(MOVIES_DATA_PATH, ACTORS_DATA_PATH, ACTORS_NAMES_PATH)
    graph = load_graph(movies_by_id, actors_by_movie, actor_names_by_id)
    # m = find_connected_components(graph)
    # print(f"The number of connected components is {len(m)}")
    # print(f"The largest connected component has {len(m['Component 1'])} vertices")
    # print(f"The second largest connected component has {len(m['Component 2'])} vertices")
    # print(f"The smallest connected components has {len(m[f'Component {len(m)}'])} vertices")
    
    
    # print(len(m["Component 2"]))
    # print(len(m[f"Component {len(m)}"]))
    # coso = find_shortest_path_to_all(graph, 'nm7057284')
    # print(coso['nm0179132'])
    # coso1 = find_shortest_path_to_all_without_weights(graph, 'nm7057284')
    # print(coso1['nm0179132'])
    # print(find_shortest_path_between_vertices(graph, 'nm7057284', 'nm0888572'))
    # print(average_separations(graph, 'Component 1', 50))
    # print(find_diameter(graph, 'Component 1', 100))

    # coso1 = find_shortest_path_to_all_without_weights(graph, 'nm11549950')
    # print(coso1['nm8311374'])


if __name__ == '__main__':
    main()