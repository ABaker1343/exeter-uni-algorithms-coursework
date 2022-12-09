package main

import (
    "os"
    "fmt"
    "strings"
    "strconv"
    "math"
)

type edge struct {
    node1 string
    node2 string
    cost float64
}

type set map[string]bool

func loadGraph(filepath string) (set, []edge) {
    data, err := os.ReadFile(filepath)
    if err != nil {
        panic("failed to read file")
    }

    content := string(data)
    lines := strings.Split(content, "\n")

    vertices := make(set)
    edges := make([]edge, 0)

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
        edges = append(edges, edge{splits[0], splits[1], cost})
        
    }

    return vertices, edges
}

func getCheapestEdge(node string, edges *[]edge) edge {
    cheapest := edge{"", "", math.MaxFloat64}
    for _, e := range *edges {
        if strings.Compare(e.node1, node) == 0 || strings.Compare(e.node2, node) == 0 {
            if e.cost < cheapest.cost {
                cheapest = e
            }
        }
    }
    return cheapest
}

func combineTrees(vt *[]set, e edge) {
}

func borukva(vertices set, edges []edge) []edge {
    vt := make([]set, 0) // slice of sets
    for v := range vertices {
        new_set := make(set)
        new_set[v] = true
        vt = append(vt, new_set)
    }
    et := make([]edge, 0) // start with empty slice of edges

    for _, tree := range vt { // for each tree in the list of trees
        minimum := edge{"", "", math.MaxFloat64}
        for node := range tree { // for each key in the tree
            // find the cheapest edge connecting out of the tree
            cheapest := getCheapestEdge(node, &edges)
            if strings.Compare(cheapest.node1, "") != 0 {
                if cheapest.cost < minimum.cost {
                    minimum = cheapest
                }
            }
        combineTrees(&vt, minimum)
        et = append(et, minimum)
        }
    }





    return et
}

func main() {
    vertices, edges := loadGraph("../data/mst-example-2.csv")
    fmt.Println(vertices, edges)
}
