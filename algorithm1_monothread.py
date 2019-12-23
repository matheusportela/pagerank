import queue
import networkx as nx

channels = {}

class Graph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def __repr__(self):
        return str(self.graph.edges)

    def load(self, filename):
        self.graph = nx.read_edgelist(filename)

    def calculate_pagerank(self, m=0.15):
        self.initialize_pagerank(m)

        for _ in range(1000):
            for node in self.graph.nodes:
                self.graph = self.calculate_pagerank_step(node, m)

        return {n: data['x'] for n, data in self.graph.nodes.data()}

    def initialize_pagerank(self, m):
        n = len(self.graph.nodes)
        initial_value = m/n

        for node in self.graph.nodes:
            channels[node] = queue.Queue()

            self.graph.nodes[node]['x'] = initial_value
            self.graph.nodes[node]['z'] = initial_value

            num_edges = len(self.graph.adj[node])
            edge_weight = 1/num_edges
            for dst in self.graph.adj[node]:
                self.graph.edges[node, dst]['weight'] = edge_weight

    def calculate_pagerank_step(self, node, m):
        graph = nx.DiGraph()
        graph.add_nodes_from(self.graph.nodes.data())
        graph.add_edges_from(self.graph.edges.data())

        for dst in self.graph.neighbors(node):
            # Send current state
            x = self.graph.nodes[node]['x']
            z = self.graph.nodes[node]['z']

            channels[dst].put((node, z))

        # Update received state
        x = self.graph.nodes[node]['x']
        z = 0

        # Update state
        while not channels[node].empty():
            src, zj = channels[node].get()
            nj = len(self.graph.edges(src))
            x += ((1 - m)/nj)*zj
            z += ((1 - m)/nj)*zj

        graph.nodes[node]['x'] = x
        graph.nodes[node]['z'] = z

        return graph


def main():
    graph = Graph()
    graph.load('graph.txt')
    print(graph.calculate_pagerank())
    print(nx.pagerank(graph.graph, alpha=0.85))

if __name__ == '__main__':
    main()