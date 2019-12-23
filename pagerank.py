import networkx as nx

class Graph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def __repr__(self):
        return str(self.graph.edges)

    def load(self, filename):
        with open(filename) as f:
            for line in f:
                source_node, destination_node = eval(line)
                self.graph.add_edge(source_node, destination_node)

    def calculate_pagerank(self, alpha=0.85):
        self.initialize_pagerank()

        for _ in range(100):
            self.graph = self.calculate_pagerank_step(alpha)

    def initialize_pagerank(self):
        num_nodes = len(self.graph.nodes)
        initial_pagerank = 1/num_nodes

        for node in self.graph.nodes:
            self.graph.nodes[node]['pagerank'] = initial_pagerank

            num_edges = len(self.graph.adj[node])
            edge_weight = 1/num_edges
            for dst in self.graph.adj[node]:
                self.graph.edges[node, dst]['weight'] = edge_weight

    def calculate_pagerank_step(self, alpha):
        graph = nx.DiGraph()

        for src, dst in self.graph.edges:
            pagerank = self.graph.nodes[src]['pagerank']
            weight = self.graph.edges[src, dst]['weight']
            sent_pagerank = alpha*pagerank*weight

            self.add_edge(graph, src, dst, weight, alpha)

            graph.nodes[dst]['pagerank'] += sent_pagerank

        return graph

    def add_edge(self, graph, src, dst, weight, alpha):
        num_nodes = len(self.graph.nodes)
        graph.add_edge(src, dst, weight=weight)
        initial_pagerank = (1 - alpha)/num_nodes

        if graph.nodes[src].get('pagerank') is None:
            graph.nodes[src]['pagerank'] = initial_pagerank
        if graph.nodes[dst].get('pagerank') is None:
            graph.nodes[dst]['pagerank'] = initial_pagerank


def main():
    graph = Graph()
    graph.load('graph.txt')
    graph.calculate_pagerank()
    print(graph.graph.nodes.data())
    print(nx.pagerank(graph.graph, alpha=0.85))

if __name__ == '__main__':
    main()