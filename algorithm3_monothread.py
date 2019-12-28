import queue
import random
import threading
import time

import networkx as nx

random.seed(0)

class Graph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def __repr__(self):
        return str(self.graph.edges)

    def load(self, filename):
        self.graph = nx.read_edgelist(filename, create_using=nx.DiGraph)
        # self.graph = nx.les_miserables_graph()

    def calculate_pagerank(self, m=0.15):
        start_channels = {n: queue.Queue() for n in self.graph.nodes}
        end_channels = {n: queue.Queue() for n in self.graph.nodes}
        data_channels = {n: queue.Queue() for n in self.graph.nodes}
        sent_data_channels = {n: queue.Queue() for n in self.graph.nodes}
        start_update_channels = {n: queue.Queue() for n in self.graph.nodes}
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
                sent_data_channels=sent_data_channels,
                start_update_channels=start_update_channels,
            )
            nodes[node.id] = node

        for _ in range(100):
            for n in node_ids:
                nodes[n].choose_update()
                nodes[n].send_data()
                nodes[n].update_pagerank()

        return {node.id: node.x for node in nodes.values()}


class Node(threading.Thread):
    def __init__(self, node_id, neighbors, num_nodes, m, start_channels, end_channels, data_channels, sent_data_channels, start_update_channels):
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
        self.sent_data_channels = sent_data_channels
        self.start_update_channels = start_update_channels
        self.is_updating = False

    def run(self):
        while True:
            # self.start_channels[self.id].get()
            self.run_pagerank_step()
            # self.end_channels[self.id].put(None)

    def run_pagerank_step(self):
        self.choose_update()
        self.send_data()
        self.update_pagerank()

    def send_data(self):
        if self.is_updating:
            for dst in self.neighbors:
                self.data_channels[dst].put((self.id, self.n, self.z))

        # self.sent_data_channels[self.id].put(None)

    def choose_update(self):
        self.is_updating = random.random() < 0.5

    def update_pagerank(self):
        # self.start_update_channels[self.id].get()

        x = self.x
        z = 0 if self.is_updating else self.z

        while not self.data_channels[self.id].empty():
            src, nj, zj = self.data_channels[self.id].get()
            x += ((1 - self.m)/nj)*zj
            z += ((1 - self.m)/nj)*zj

        self.x = x
        self.z = z


def main():
    graph = Graph()
    # graph.load('graph.txt')
    graph.load('web-Google.txt')
    print(graph.calculate_pagerank())
    # print(nx.pagerank(graph.graph, alpha=0.85))

if __name__ == '__main__':
    main()