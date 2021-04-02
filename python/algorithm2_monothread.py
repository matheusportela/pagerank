# Algorithm 2 implementation monothreaded

import queue
import random
import threading
import time

import networkx as nx

NUM_ITERATIONS = 2000

random.seed(0)

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
        nodes = {}
        node_ids = set(self.graph.nodes)

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
            nodes[node.id] = node

        for _ in range(NUM_ITERATIONS):
            selected_node = random.choice(list(self.graph.nodes))

            nodes[selected_node].run_pagerank_step(selected_node)

            for n in (node_ids - set([selected_node])):
                start_channels[n].put(selected_node)
                nodes[n].run_pagerank_step(selected_node)

        return {node.id: node.x for node in nodes.values()}


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
            selected_node = self.start_channels[self.id].get()
            self.run_pagerank_step(selected_node)
            self.end_channels[self.id].put(None)

    def run_pagerank_step(self, selected_node):
        self.send_data(selected_node)
        self.update_pagerank(selected_node)

    def send_data(self, selected_node):
        if self.id != selected_node:
            return

        for dst in self.neighbors:
            self.data_channels[dst].put((self.id, self.n, self.z))

    def update_pagerank(self, selected_node):
        x = self.x
        z = 0

        if self.id == selected_node:
            self.z = 0
        else:
            # Node received an update from its neighbor
            assert(self.data_channels[self.id].qsize() <= 1)
            if not self.data_channels[self.id].empty():
                src, nj, zj = self.data_channels[self.id].get()
                self.x = self.x + ((1 - self.m)/nj)*zj
                self.z = self.z + ((1 - self.m)/nj)*zj


def main():
    graph = Graph()
    graph.load('graphs/graph.txt')
    print(graph.calculate_pagerank())

if __name__ == '__main__':
    main()