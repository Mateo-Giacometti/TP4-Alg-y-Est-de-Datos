from graph import Graph
import csv
from itertools import combinations
from collections import deque
import heapq
from tqdm import tqdm
import os
import pickle
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


# Ejercicio 1

def find_connected_components(graph):
    visited = set()
    graph_components = []
    component_id = 1 

    for vertex in tqdm(graph.get_graph_elements()):
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
            graph_components.append((component_id, component))
            component_id += 1
    graph_components.sort(key=lambda x: len(x[1]), reverse=True)  # Ordenar las componentes por tamaño descendente
    graph_components = {f"Component {component_id}": component for component_id, component in graph_components}
    return graph_components


# Ejercicio 2

def find_shortest_path_to_all(graph, vetex_id: str):
    # Inicializar las distancias de todos los nodos como infinito
    distances = {vetex: float('inf') for vetex in graph.get_graph_elements()}
    distances[vetex_id] = 0

    # Inicializar el heap con el nodo de inicio
    heap = [(0, vetex_id)]

    while heap:
        # Obtener el nodo con la distancia mínima desde el heap
        current_distance, current_node = heapq.heappop(heap)

        # Si la distancia actual es mayor que la distancia almacenada, continuar al siguiente nodo
        if current_distance > distances[current_node]:
            continue

        # Actualizar las distancias de los nodos adyacentes
        for neighbor in graph.get_neighbors(current_node):
            weight = graph.get_edge_data(current_node, neighbor)
            new_distance = distances[current_node] + len(weight)
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                heapq.heappush(heap, (new_distance, neighbor))

    return distances


# Ejercicio 7

# def average_separations(graph, related_components: list):


def main():
    movies_by_id, actors_by_movie, actor_names_by_id = read_data(MOVIES_DATA_PATH, ACTORS_DATA_PATH, ACTORS_NAMES_PATH)
    graph = load_graph(movies_by_id, actors_by_movie, actor_names_by_id)
    # graph.print_graph()
    m = find_connected_components(graph)
    # print(find_shortest_path_to_all(graph, 'nm11640793'))
    # print(graph.get_edge_data('nm11640793', 'nm0098376'))


if __name__ == '__main__':
    main()
    
   





            



