import networkx as nx

class Graph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.channel = {}

    def __repr__(self):
        return str(self.graph.edges)

    def load(self, filename):
        with open(filename) as f:
            for line in f:
                source_node, destination_node = eval(line)
                self.graph.add_edge(source_node, destination_node)

    def calculate_pagerank(self, m=0.15):
        self.initialize_pagerank(m)

        for _ in range(1000):
            for node in self.graph.nodes:
                self.graph = self.calculate_pagerank_step(node, m)

    def initialize_pagerank(self, m):
        n = len(self.graph.nodes)
        initial_value = m/n

        for node in self.graph.nodes:
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

        print(f'Incoming channel for node {node}:')
        print(self.channel)

        if node not in self.channel:
            self.channel[node] = []

        for dst in self.graph.neighbors(node):
            # Send current state
            x = self.graph.nodes[node]['x']
            z = self.graph.nodes[node]['z']

            if dst not in self.channel:
                self.channel[dst] = []
            self.channel[dst].append((node, z))

        # Update received state
        x = self.graph.nodes[node]['x']
        z = 0

        # Update state
        for src, zj in self.channel[node]:
            nj = len(self.graph.edges(src))
            x += ((1 - m)/nj)*zj
            z += ((1 - m)/nj)*zj

        graph.nodes[node]['x'] = x
        graph.nodes[node]['z'] = z

        self.channel[node] = []

        print(f'Outgoing channel for node {node}:')
        print(self.channel)

        return graph


def main():
    graph = Graph()
    graph.load('graph.txt')
    graph.calculate_pagerank()
    print(graph.graph.nodes.data())
    print(nx.pagerank(graph.graph, alpha=0.85))

if __name__ == '__main__':
    main()