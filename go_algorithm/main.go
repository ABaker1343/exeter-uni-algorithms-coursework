package main

import (
	"fmt"
	"math"
	"os"
	"reflect"
	"strconv"
	"strings"
	"time"
)

// structure that will house the information about an edege
type edge struct {
	node1 string
	node2 string
	cost  float64
}

// make types for sets just to make code more readable and easier to edit
type set map[string]bool
type edgeSet map[edge]bool

func loadGraph(filepath string) (set, edgeSet) {
	// function that will read a file and load the graph that it contains
	// returns the edges and vertices in the file

	data, err := os.ReadFile(filepath)
	if err != nil {
		panic("failed to read file")
	}

	content := string(data)
	lines := strings.Split(content, "\n")

	vertices := make(set)
	edges := make(edgeSet, 0)

	for _, l := range lines {
		fmt.Println(l)
		splits := strings.Split(l, ",")
		if len(splits) < 3 {
			break
		}
		vertices[splits[0]] = true
		vertices[splits[1]] = true
		cost, err := strconv.ParseFloat(splits[2], 32)
		if err != nil {
			panic("failed to parse float")
		}
		//edges = append(edges, edge{splits[0], splits[1], cost})
		edges[edge{splits[0], splits[1], cost}] = true

	}

	return vertices, edges
}

func getCheapestEdge(node string, edges *edgeSet, vt *[]set) edge {
	// function that returns the cheapest edge that leaves its own tree for any given node and set of trees
	// if there is none then the function return an empty edge with maxfloat value

	cheapest := edge{"", "", math.MaxFloat64}
	for e := range *edges {
		if strings.Compare(e.node1, node) == 0 || strings.Compare(e.node2, node) == 0 {
			if e.cost < cheapest.cost {
				same := false
				for _, v := range *vt {
					if v[e.node1] && v[e.node2] {
						same = true
						break
					}
				}
				if !same {
					cheapest = e
				}
			}
		}
	}
	return cheapest
}

func union(set1 set, set2 set) set {
	// function to create the union of two sets
	newSet := set1
	for k := range set2 {
		newSet[k] = true
	}
	return newSet
}

func remove(slice *[]set, s set) {
	// function to remove from a value from a slice by value
	for i, v := range *slice {
		if reflect.DeepEqual(v, s) {
			(*slice)[i] = (*slice)[len(*slice)-1]
			*slice = (*slice)[:len(*slice)-1]
		}
	}
}

func combineTrees(vt *[]set, e edge) {
	// function to combine two trees into one
	var tree1 set
	var tree2 set

	for _, tree := range *vt {
		if tree[e.node1] {
			tree1 = tree
		} else if tree[e.node2] {
			tree2 = tree
		}
	}

	remove(vt, tree1)
	remove(vt, tree2)
	newTree := union(tree1, tree2)
	*vt = append(*vt, newTree)
}

func getCheapestEdgeThread(node string, edges *edgeSet, vt *[]set, com chan edge) {
	// function that finds the cheapest edge leaving the tree for any given node
	// this version of the function writes the output to a channel instead of returning so that it can be used in a
	// multi-threaded context

	cheapest := edge{"", "", math.MaxFloat64}
	for e := range *edges {
		if strings.Compare(e.node1, node) == 0 || strings.Compare(e.node2, node) == 0 {
			if e.cost < cheapest.cost {
				same := false
				for _, v := range *vt {
					if v[e.node1] && v[e.node2] {
						same = true
						break
					}
				}
				if !same {
					cheapest = e
				}
			}
		}
	}
	com <- cheapest
}

func borukvaThreaded(vertices set, edges edgeSet) map[edge]bool {
	// function to compute the algorithm
	// this version runs the algorithm utilising multi-threading

	vt := make([]set, 0) // slice of sets
	for v := range vertices {
		new_set := make(set)
		new_set[v] = true
		vt = append(vt, new_set)
	}
	//et := make([]edge, 0) // start with empty slice of edges
	et := make(map[edge]bool)

	com := make(chan edge, len(vertices))

	for len(vt) > 1 {
		for _, tree := range vt { // for each tree in the list of trees
			threadCount := 0
			for node := range tree { // for each key in the tree
				// find the cheapest edge connecting out of the tree
				go getCheapestEdgeThread(node, &edges, &vt, com)
				threadCount++
			}
			cheapest := edge{"", "", math.MaxFloat64}
			for i := 0; i < threadCount; i++ {
				newEdge := <-com
				if strings.Compare(newEdge.node1, "") != 0 && newEdge.cost < cheapest.cost {
					cheapest = newEdge
				}
			}
			if cheapest.cost != math.MaxFloat64 {
				combineTrees(&vt, cheapest)
				et[cheapest] = true
				break
			}
		}
	}

	return et
}

func borukva(vertices set, edges edgeSet) map[edge]bool {
	// single-threaded implementation of the algorithm

	vt := make([]set, 0) // slice of sets
	for v := range vertices {
		new_set := make(set)
		new_set[v] = true
		vt = append(vt, new_set)
	}
	//et := make([]edge, 0) // start with empty slice of edges
	et := make(map[edge]bool)

	for len(vt) > 1 {
		minimum := edge{"", "", math.MaxFloat64}
		for _, tree := range vt { // for each tree in the list of trees
			for node := range tree { // for each key in the tree
				// find the cheapest edge connecting out of the tree
				cheapest := getCheapestEdge(node, &edges, &vt)
				if strings.Compare(cheapest.node1, "") != 0 {
					if cheapest.cost < minimum.cost {
						minimum = cheapest
					}
				}
			}
			if minimum.cost != math.MaxFloat64 {
				combineTrees(&vt, minimum)
				//et = append(et, minimum)
				et[minimum] = true
				//delete(edges, minimum)
				//time.Sleep(5 * time.Second)
				break
			}
		}
	}

	return et
}

func main() {
	filepath := os.Args[1]
	vertices, edges := loadGraph(filepath)
	// run the algorithm on a single thread
	startTime := time.Now()
	mst := borukva(vertices, edges)
	elapsed := time.Since(startTime)
	for e := range mst {
		fmt.Println(e)
	}
	// run the algorithm in a multi-threaded context
	fmt.Println("starting threaded run")
	startThreaded := time.Now()
	mst = borukvaThreaded(vertices, edges)
	elapsedThreaded := time.Since(startThreaded)
	for e := range mst {
		fmt.Println(e)
	}
	// compare the time taken for each run
	fmt.Println("time taken in serial: ", elapsed)
	fmt.Println("time taken in threaded algorithm: ", elapsedThreaded)

}
