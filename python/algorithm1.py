# Algorithm 1 implementation multithreaded

import queue
import threading
import time

import networkx as nx

NUM_ITERATIONS = 1000

class Graph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def __repr__(self):
        return str(self.graph.edges)

    def load(self, filename):
        self.graph = nx.read_edgelist(filename, create_using=nx.DiGraph)

    def calculate_pagerank(self, m=0.15):
        start_channels = {n: queue.Queue() for n in self.graph.nodes}
        end_channels = {n: queue.Queue() for n in self.graph.nodes}
        data_channels = {n: queue.Queue() for n in self.graph.nodes}
        nodes = []

        for node in self.graph.nodes:
            node = Node(
                node_id=node,
                neighbors=list(self.graph.neighbors(node)),
                num_nodes=len(self.graph.nodes),
                m=m,
                start_channels=start_channels,
                end_channels=end_channels,
                data_channels=data_channels,
            )
            node.start()
            nodes.append(node)

        for _ in range(NUM_ITERATIONS):
            for node in self.graph.nodes:
                start_channels[node].put(None)
                end_channels[node].get()

        return {node.id: node.x for node in nodes}


class Node(threading.Thread):
    def __init__(self, node_id, neighbors, num_nodes, m, start_channels, end_channels, data_channels):
        super().__init__(daemon=True)
        self.id = node_id
        self.neighbors = neighbors
        self.m = m
        self.n = len(self.neighbors)
        self.x = self.m/num_nodes
        self.z = self.m/num_nodes
        self.start_channels = start_channels
        self.end_channels = end_channels
        self.data_channels = data_channels

    def run(self):
        while True:
            self.start_channels[self.id].get()
            self.run_pagerank_step()
            self.end_channels[self.id].put(None)

    def run_pagerank_step(self):
        self.send_data()
        self.update_pagerank()

    def send_data(self):
        for dst in self.neighbors:
            self.data_channels[dst].put((self.id, self.n, self.z))

    def update_pagerank(self):
        x = self.x
        z = 0

        while not self.data_channels[self.id].empty():
            src, nj, zj = self.data_channels[self.id].get()
            x += ((1 - self.m)/nj)*zj
            z += ((1 - self.m)/nj)*zj

        self.x = x
        self.z = z


def main():
    graph = Graph()
    graph.load('graphs/graph.txt')
    print(graph.calculate_pagerank())

if __name__ == '__main__':
    main()