from typing import Optional, Any, List
import csv
from itertools import combinations
from collections import deque
import os
import pickle
from tqdm import tqdm
MOVIE_TITLE_TYPE = "movie"
MOVIE_COLUMNS = ["tconst", "titleType", "primaryTitle"]
PRINCIPALS_COLUMNS = ["nconst", "category"]
MOVIES_DATA_PATH = "./datasets/title-basics-f.tsv"
ACTORS_DATA_PATH = "./datasets/title-principals-f.tsv"
ACTORS_NAMES_PATH = "./datasets/name-basics-f.tsv"

global Kevin_Bacon
Kevin_Bacon = "nm0000102"  # Kevin Bacon's ID    

class Bipartite_Graph:
    """
    Bipartite_Graph class
    """
    def __init__(self):
        self._graph = {}

    def add_vertex(self, vertex: str, type: Optional[Any]=None, data: Optional[Any]=None) -> None:
        """
        Adds a vertex to the graph
        :param vertex: the vertex name
        :param data: data associated with the vertex
        """
        if vertex not in self._graph:
            self._graph[vertex] = {'data': data, 'type': type, 'neighbors': []}

    def add_edge(self, vertex1: str, vertex2: str, data: Optional[Any]=None) -> None:
        """
        Adds an edge to the graph
        :param vertex1: vertex1 key
        :param vertex2: vertex2 key
        :param data: the data associated with the vertex
        """
        if not vertex1 in self._graph or not vertex2 in self._graph:
            raise ValueError("The vertexes do not exist")
        self._graph[vertex1]['neighbors'].append(vertex2)
        self._graph[vertex2]['neighbors'].append(vertex1)

    def get_neighbors(self, vertex) -> List[str]:
        """
        Get the list of vertex neighbors
        :param vertex: the vertex to query
        :return: the list of neighbor vertexes
        """
        if vertex in self._graph:
            return self._graph[vertex]['neighbors']
        else:
            return []

    def get_vertex_data(self, vertex: str) -> Optional[Any]:
        """
        Gets  vertex associated data
        :param vertex: the vertex name
        :return: the vertex data
        """
        if self.vertex_exists(vertex):
            return self._graph[vertex]
        else:
            return None

   # Se borró edge_data() al no ser util en un grafo sin pesos

    def print_graph(self) -> None:
        """
        Prints the graph
        """
        for vertex, data in self._graph.items():
            print("Vertex:", vertex)
            print("Name:", data['data'])
            print("Type:", data['type'])
            print("Neighbors:", data['neighbors'])
            print("")

    def vertex_exists(self, vertex: str) -> bool:
        """
        If contains a vertex
        :param vertex: the vertex name
        :return: boolean
        """
        return vertex in self._graph

    def edge_exists(self, vertex1: str, vertex2: str) -> bool:
        """
        If contains an edge
        :param vertex1: the vertex1 name
        :param vertex2: the vertex2 name
        :return: boolean
        """
        return vertex1 in self._graph and vertex2 in self._graph[vertex1]['neighbors']
    
    def get_graph_elements(self) -> None:
        """
        Gets the graph elements
        :return: the graph elements
        """
        return self._graph


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


def load_graph(movies_by_id, actors_by_movie, actor_names_by_id):
    """
    Loads the graph
    :param movies_by_id: the movies data by id as dict
    :param actors_by_movie: the actors data by movie
    :param actor_names_by_id: the actors names by their ids
    :return: a Graph Bipartite with actors and movies vertices
    """
    graph = Bipartite_Graph()
    print("Loading graph")

    for movie_id in movies_by_id.keys():
        movie_title = movies_by_id[movie_id]['primaryTitle']
        if not graph.vertex_exists(movie_id):
            graph.add_vertex(movie_id, "movie", movie_title)
        for actor_id in actors_by_movie[movie_id]:
            if not graph.vertex_exists(actor_id):
                graph.add_vertex(actor_id, "actor", actor_names_by_id.get(actor_id, "ERROR"))	
            graph.add_edge(movie_id, actor_id, movie_title)
    return graph


"""	
Ejercicio 1

Dados dos actores, queremos conocer su grado de separación. El grado de separación se define como la mínima cantidad de películas de distancia a la que se encuentran.

"""

def degree_of_separation(graph: Bipartite_Graph, vertex1: str, vertex2: str) -> float:
    """	
    Calculate the degree of separation between two vertices in the graph (minimum number of films away at which both are). 
    
    Parameters
    ----------
    graph : Bipartite_Graph
        The graph to search
    vertex1 : str
        The first vertex's ID (where the search begins)
    vertex2 : str
        The second vertex's ID (where the search ends)

    Returns
    -------
    float
        The degree of separation between the two vertices (inf if they are not connected)
    """
    if not graph.vertex_exists(vertex1) or not graph.vertex_exists(vertex2): return float('inf')
    if graph.get_vertex_type(vertex1) != 'actor' or graph.get_vertex_type(vertex2) != 'actor': return float('inf') # Preguntar si es necesario
    if vertex1 == vertex2: return 0.0
    visited = set()
    queues = deque()
    queues.append((vertex1, 0.0))
    while queues:
        current_vertex, current_distance = queues.popleft()
        if current_vertex == vertex2: return current_distance/2 
        if current_vertex not in visited:
            visited.add(current_vertex)
            for neighbor in graph.get_neighbors(current_vertex):
                queues.append((neighbor, current_distance + 1.0))
    return float('inf')


"""
Ejercicio 2

Encuentre quien está a mayor grado de separación de Kevin Bacon en su componente conexa.

"""

def min_distance_to_all_vertices(graph: Bipartite_Graph, vertex_id: str) -> dict:
    """
    Calculate the minimum distance from a vertex to all the other vertices in the graph (minimum number of films away at which both are). 

    Parameters
    ----------
    graph : Bipartite_Graph
        The graph to search
    vertex_id : str
        The vertex's ID to search from

    Returns
    -------
    dict
        A dictionary with the minimum distance to all vertices in the graph
    """
    if not graph.vertex_exists(vertex_id): return {"The vertex does not exist" : float('inf')}
    if graph.get_vertex_data(vertex_id)['type'] != "actor": return {"The vertex is not an actor" : float('inf')}
    distances = {}
    for vertex in graph.get_graph_elements():
        if graph.get_vertex_data(vertex)['type'] == "actor":
            distances[vertex] = float('inf')
    distances[vertex_id] = 0
    queues = deque()
    queues.append((vertex_id, 0))
    while queues:
        current_vertex, current_distance = queues.popleft()
        for movie in graph.get_neighbors(current_vertex):
            for neighbor in graph.get_neighbors(movie):
                if distances[neighbor] == float('inf'):
                    distances[neighbor] = current_distance + 1.0
                    queues.append((neighbor, current_distance + 1.0))
    return distances


def greatest_distance_to_Kevin_Bacon(graph: Bipartite_Graph) -> tuple: 
    """
    Calculate the greatest distance from Kevin Bacon to all the other actors in the graph (minimum number of films away at which both are).

    Parameters
    ----------
    graph : Bipartite_Graph
        The graph to search

    Returns
    -------
    tuple
        A tuple with the greatest distance and the actors with that distance
    """
    bacon_max_distance_actors = []  
    max_distance = 0
    distances = min_distance_to_all_vertices(graph, Kevin_Bacon)
    for actor in distances:
        if distances[actor] > max_distance and distances[actor] != float('inf'):
            bacon_max_distance_actors = []
            max_distance = distances[actor]
            bacon_max_distance_actors.append(actor)
        elif distances[actor] == max_distance: bacon_max_distance_actors.append(actor)
    return max_distance, bacon_max_distance_actors


def main():
    movies_by_id, actors_by_movie, actor_names_by_id = read_data(MOVIES_DATA_PATH, ACTORS_DATA_PATH, ACTORS_NAMES_PATH)
    graph = load_graph(movies_by_id, actors_by_movie, actor_names_by_id)
    # graph.print_graph()
    # print(len(graph.get_graph_elements()))
    # print(degree_of_separation(graph, 'nm2900398', 'nm1001351'))

    # pepe = min_distance_to_all_vertices(graph, 'nm2900398')
    # print(pepe['nm1001351'])

    print(greatest_distance_to_Kevin_Bacon(graph))
    

if __name__ == '__main__':
    main()
