package main

import (
	"fmt"
	// "gonum.org/v1/gonum/graph"
	// "gonum.org/v1/gonum/graph/simple"
	"io"
	"math/rand"
	"os"
	// "sync"
	// "time"
)

// Node a single node that composes the tree
type Node struct {
	id                         int64
	pagerank                   float64
	x                          float64
	z                          float64
	send_state_ch              chan bool
	finished_sending_state_ch  chan bool
	update_state_ch            chan bool
	finished_updating_state_ch chan bool
	data_ch                    chan Msg
}

type Msg struct {
	node_id int64
	nj      int64
	zj      float64
}

func (n Node) String() string {
	return fmt.Sprintf("%v", n.id)
}

type Graph struct {
	nodes map[int64]*Node
	edges map[*Node][]*Node
	// lock  sync.RWMutex
}

func (g *Graph) UpdateNode(id int64, pagerank float64) {
	g.nodes[id].pagerank = pagerank
}

func (g *Graph) GetNode(id int64) *Node {
	return g.nodes[id]
}

func (g *Graph) GetNeighbors(id int64) []*Node {
	node := g.GetNode(id)
	return g.edges[node]
}

func (g *Graph) NumNodes() int {
	return len(g.nodes)
}

func (g *Graph) NumEdges(n *Node) int {
	return len(g.edges[n])
}

func (g *Graph) AddNode(id int64) (n *Node) {
	// g.lock.Lock()
	if g.nodes == nil {
		g.nodes = make(map[int64]*Node)
	}

	n = g.GetNode(id)
	if n == nil {
		n = &Node{
			id:                         id,
			send_state_ch:              make(chan bool),
			update_state_ch:            make(chan bool),
			finished_sending_state_ch:  make(chan bool),
			finished_updating_state_ch: make(chan bool),
			data_ch:                    make(chan Msg, 1)}
		g.nodes[id] = n
	}

	return n
	// g.lock.Unlock()
}

func (g *Graph) AddEdge(src, dst int64) {
	// g.lock.Lock()

	if g.edges == nil {
		g.edges = make(map[*Node][]*Node)
	}

	src_node := g.GetNode(src)
	if src_node == nil {
		src_node = g.AddNode(src)
	}

	dst_node := g.GetNode(dst)
	if dst_node == nil {
		dst_node = g.AddNode(dst)
	}

	g.edges[src_node] = append(g.edges[src_node], dst_node)

	// g.lock.Unlock()
}

func (g *Graph) Print() {
	// g.lock.RLock()
	s := ""
	for _, node := range g.nodes {
		s += fmt.Sprintf("%d (pr: %f xj: %f zj: %f)", node.id, node.pagerank, node.x, node.z) + " -> "
		neighbors := g.edges[node]
		s += fmt.Sprintf("%d ", len(neighbors))
		s += fmt.Sprintf("%v ", neighbors)
		// for j := 0; j < len(neighbors); j++ {
		// 	s += neighbors[j].String() + " "
		// }
		s += "\n"
	}
	fmt.Println(s)
	// g.lock.RUnlock()
}

func loadGraph(filePath string) (g *Graph) {
	fd, err := os.Open(filePath)
	if err != nil {
		panic(fmt.Sprintf("Cannot open %s: %v", filePath, err))
	}

	g = new(Graph)

	var src, dst int64
	for {
		_, err := fmt.Fscanf(fd, "%d %d\n", &src, &dst)
		if err != nil {
			if err == io.EOF {
				return
			} else {
				panic(fmt.Sprint("Error reading %s: %v", filePath, err))
			}
		}
		g.AddEdge(src, dst)
	}

	return
}

func initializePageRank(g *Graph, m float64) {
	var n, initial_value float64
	n = float64(g.NumNodes())
	initial_value = m / n

	for _, node := range g.nodes {
		node.pagerank = initial_value
		node.x = initial_value
		node.z = initial_value
	}
}

func updatePageRank(g *Graph, id int64, selected_id int64) {
	node := g.GetNode(id)

	<-node.send_state_ch
	if id == selected_id {
		fmt.Println(id, "sending state")
		sendState(g, id)
	} else {
		// fmt.Println(id, "ignoring sending state")
	}
	node.finished_sending_state_ch <- true

	<-node.update_state_ch
	if id == selected_id {
		node.z = 0
		// fmt.Println(id, "ignoring updating state")
	} else {
		// fmt.Println(id, "updating state")
		updateState(g, id)
	}
	node.finished_updating_state_ch <- true
}

func sendState(g *Graph, id int64) {
	node := g.GetNode(id)
	neighbors := g.GetNeighbors(id)
	msg := Msg{node_id: id, nj: int64(len(neighbors)), zj: node.z}

	// Send data
	for _, dst := range neighbors {
		// fmt.Println(id, "->", dst, "msg:", msg)
		dst.data_ch <- msg
	}
}

func updateState(g *Graph, id int64) {
	node := g.GetNode(id)
	select {
	case msg := <-node.data_ch:
		// fmt.Println(id, "msg:", msg)
		node.x += 0.85 * msg.zj / float64(msg.nj)
		node.z += 0.85 * msg.zj / float64(msg.nj)
	default:
		// No message to consume
	}
}

func iteratePageRank(selected_id int64, g *Graph, out chan bool) {
	// fmt.Println("Starting iteration")

	// fmt.Println("Sending states")
	for _, node := range g.nodes {
		go updatePageRank(g, node.id, selected_id)
		node.send_state_ch <- true
	}

	for _, node := range g.nodes {
		<-node.finished_sending_state_ch
	}

	// fmt.Println("Updating states")
	for _, node := range g.nodes {
		node.update_state_ch <- true
	}

	for _, node := range g.nodes {
		<-node.finished_updating_state_ch
	}

	// fmt.Println("Finished iteration")
	out <- true
}

func main() {
	m := 0.15
	g := loadGraph("graph.txt")
	// g := loadGraph("web-Google.txt")

	initializePageRank(g, m)
	g.Print()

	out := make(chan bool)

	// r := rand.New(rand.NewSource(time.Now().UnixNano()))
	r := rand.New(rand.NewSource(0))
	var selected_id int64

	for i := 0; i < 200; i++ {
		selected_id = int64(r.Intn(g.NumNodes()))
		go iteratePageRank(selected_id, g, out)
		<-out
		// g.Print()
	}

	g.Print()
	// loadGraph("web-Google.txt")
}
