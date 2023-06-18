from graph import Graph
import csv
from itertools import combinations
from collections import deque
import heapq
from tqdm import tqdm
import os
import pickle
import time
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
    return graph

"""
Ejercicio 1

Nos interesa entender cuan “particionado” esta nuestro grafo. Con esta información podríamos “clusterizar” a nuestra comunidad de artistas. 
Se pide hallar la cantidad de componentes conexas que lo componen, y asignar a cada vértice en una misma componente conexa un mismo identificador. 
Una componente conexa se define como un subgrafo maximal conexo. ¿Cuántas componentes conexas hay? ¿Cuál es la segunda componente conexa más grande? 
¿Cúal es la más chica de todas?

"""

def find_connected_components(graph):
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

def find_shortest_path_to_all(graph, vertex_id: str):
    results = {vertex: {'distance': float('inf'), 'path': []} for vertex in graph.get_graph_elements()}
    results[vertex_id]['distance'] = 0
    results[vertex_id]['path'] = [vertex_id]
    heap = [(0, vertex_id)]
    while heap:
        current_distance, current_node = heapq.heappop(heap)
        if current_distance > results[current_node]['distance']:
            continue
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

def find_shortest_path_between_vertices(graph, start_vertex, end_vertex):
    start_time = time.time()
    short_paths = find_shortest_path_to_all(graph, start_vertex)
    the_path = short_paths[end_vertex]
    end_time = time.time()
    elapsed_time = end_time - start_time
    return the_path, elapsed_time

"""
Ejercicio 4

¿Cuál es el diámetro del grafo para la componente conexa principal? Utilice máximo 15 minutos para calcularlo, si no le es posible calcularlo de forma exacta, indique:
a) ¿Cuánto demoraría hacerlo de forma exacta?
b) Estime el diámetro del grafo utilizando el tiempo dado

"""

def find_diameter(graph, graph_connected_component: str):
    diameter = 0
    connected_component = find_connected_components(graph)[graph_connected_component]
    start_time = time.time()
    for vertex in tqdm(connected_component):
        if time.time() - start_time >= 200:  # Verificar si han transcurrido 15 minutos (900 segundos)
            break
        separations = find_shortest_path_to_all(graph, vertex)
        separations = [separation['distance'] for separation in separations.values()]
        separations = [separation for separation in separations if separation != float('inf')]
        if max(separations) > diameter:
            diameter = max(separations)
    return diameter

"""
Ejercicio 5

¿Cuál es, en la componente conexa principal, el promedio de separaciones para cada actor y para todos en general? De ser imposible de calcular estimelo.

"""

def average_separations(graph, graph_connected_component: str):
    average_per_vertex = {}
    total_average = 0
    connected_component = find_connected_components(graph)[graph_connected_component]
    for vertex in tqdm(connected_component):
        separations = find_shortest_path_to_all(graph, vertex)
        separations = [separation['distance'] for separation in separations.values()]
        separations = [separation for separation in separations if separation != float('inf')]
        separations = sum(separations) / len(separations)
        average_per_vertex[vertex] = separations
        total_average += separations
    total_average = total_average / len(connected_component)
    return average_per_vertex, total_average

def estimated_average_separation(graph, graph_connected_component: str):
    estimated_average_per_vertex = {}
    estimated_total_average = 0
    connected_component = find_connected_components(graph)[graph_connected_component]
    start_time = time.time()  # Obtener el tiempo de inicio
    for vertex in connected_component:
        if time.time() - start_time >= 900:  # Verificar si han transcurrido 15 minutos (900 segundos)
            break
        separations = find_shortest_path_to_all(graph, vertex)
        separations = [separation['distance'] for separation in separations.values()]
        separations = [separation for separation in separations if separation != float('inf')]
        separations = sum(separations) / len(separations)
        estimated_average_per_vertex[vertex] = separations
        estimated_total_average += separations

    estimated_total_average = estimated_total_average / len(estimated_average_per_vertex)
    return estimated_average_per_vertex, estimated_total_average


def main():
    movies_by_id, actors_by_movie, actor_names_by_id = read_data(MOVIES_DATA_PATH, ACTORS_DATA_PATH, ACTORS_NAMES_PATH)
    graph = load_graph(movies_by_id, actors_by_movie, actor_names_by_id)
    m = find_connected_components(graph)
    print(len(m["Component 1"]))
    print(len(m["Component 2"]))
    print(len(m[f"Component {len(m)}"]))
    # coso = find_shortest_path_to_all(graph, 'nm7057284')
    # print(coso['nm0888572'])
    # print(find_shortest_path_between_vertices(graph, 'nm7057284', 'nm0888572'))
    # print(estimated_average_separation(graph, 'Component 1'))
    # print(find_diameter(graph, 'Component 1'))


if __name__ == '__main__':
    main()