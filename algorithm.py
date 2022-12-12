import sys
import threading
import time
from matplotlib._api import caching_module_getattr
import networkx
import matplotlib
from matplotlib import pyplot

def load_graph(filepath):
    """
    function to create the vertices and edges from a file
    """
    with open(filepath) as f:
        content = f.read()
    vertices = set()
    edges = set()
    for line in content.split("\n"):
        if not line: continue
        splits = line.split(',')
        if len(splits) < 3:
            break
        vertices.add(splits[0]) # first node
        vertices.add(splits[1]) # second node
        edges.add((splits[0], splits[1], float(splits[2]))) # edge

    return vertices, edges

def min_cost_edge(node, vt, edges):
    """
    function that find the edge with the least cost for a given node in a graph
    the retured edge will always lead outside of the graph or null
    """
    min_cost = sys.float_info.max
    mce = None
    for e in edges:
        if e[0] == node or e[1] == node:
            if e[2] < min_cost:
                # make sure they are not in the same tree already
                same = False
                for v in vt:
                    if e[0] in v and e[1] in v:
                        same = True
                        break
                if not same:
                    min_cost = e[2]
                    mce = e
    return mce

def combine_trees(vertices : list[set], edge : tuple):
    """
    function for combining the trees into one using the edges
    """

    # find the two trees that contain the edges we are linking and combine those trees

    tree1 = set()
    tree2 = set()

    for v in vertices:
        if edge[0] in v:
            tree1 = v
        elif edge[1] in v:
            tree2 = v

    # combine the 2 trees
    if tree1 and tree2:
        new_tree = tree1.union(tree2)
        vertices.remove(tree1)
        vertices.remove(tree2)
        vertices.append(new_tree)

    return vertices

def borukva(vertices : set, edges : set):
    """
    function to execute the algorithm and return the set of edges for the minimum spanning tree
    """
    #vt = vertices # trees in the algorithm
    vt = []
    for v in vertices:
        vt.append(frozenset([v]))
    et = set() # edges in the MST

    while len(vt) > 1:
        for tree in vt: # for each tree in the current list of trees
            minimum = (None, None, sys.float_info.max)
            #mn = []
            for node in tree: # for each node in that tree find the minimum node leaving the tree
                mce = min_cost_edge(node, vt, edges)
                if mce and mce[2] < minimum[2]:
                    #mn.append(mce)
                    minimum = mce
            #minimum = min(mn, key=lambda x : x[2])
            et.add(minimum)
            vt = combine_trees(vt, minimum)

    return (vt, et)

def plot_graph(edges, mst_edges):
    """
    function to plot the mst on a graphical graph
    """
    pyplot.clf()
    G = networkx.Graph()

    all_edges = []
    for e in edges:
        G.add_node(e[0])
        G.add_node(e[1])
        G.add_edge(e[0], e[1], weight=e[2])
        all_edges.append((e[0], e[1]))

    mst = []
    for e in mst_edges:
        mst.append((e[0], e[1]))

    pos = networkx.spring_layout(G, k=2)
    edge_labels = dict([((u, v,), d['weight']) for u, v, d in G.edges(data=True)])
    networkx.draw_networkx_nodes(G, pos, node_size=300)
    networkx.draw_networkx_edges(G, pos, edgelist=all_edges, style="dashed")
    networkx.draw_networkx_edges(G, pos, edgelist=mst_edges, width=3, edge_color="red")

    networkx.draw_networkx_labels(G, pos)
    networkx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    pyplot.axis('off')
    pyplot.show()

if __name__ == "__main__":
    """
    main function
    """
    graphic = False
    filepath = sys.argv[1]
    for arg in sys.argv:
        if arg == '-g' or arg == '--graphic':
            graphic = True
            try:
                matplotlib.use("tkAgg") # set the backend for matplotlib to tk
            except:
                matplotlib.use("qtagg")

    vertices, edges = load_graph(filepath) # load in the graph file

    start_single = time.time()
    mst = borukva(vertices, edges) # single threaded algorithm
    end_single = time.time()

    print(" min spanning tree single-threaded ".center(70,'='))
    print(mst[1])

    print("time without threading: ", end_single - start_single)

    if graphic:
        plot_graph(edges, mst[1])
