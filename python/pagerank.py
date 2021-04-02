# Reference PageRank implementation, using NetworkX to calculate the PageRank
# of a graph

import networkx as nx

class Graph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def load(self, filename):
        self.graph = nx.read_edgelist(filename, create_using=nx.DiGraph)


def main():
    graph = Graph()
    graph.load('graphs/graph.txt')
    print(nx.pagerank(graph.graph, alpha=0.85))


if __name__ == '__main__':
    main()