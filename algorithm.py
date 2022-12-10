import sys
import threading
import time
from matplotlib._api import caching_module_getattr
import networkx
import matplotlib
from matplotlib import pyplot

def load_graph(filepath):
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
    #vt = vertices # trees in the algorithm
    vt = []
    for v in vertices:
        vt.append(frozenset([v]))
    et = set() # edges in the MST

    while len(vt) > 1:
        for tree in vt:
            minimum = (None, None, sys.float_info.max)
            #mn = []
            for node in tree:
                mce = min_cost_edge(node, vt, edges)
                if mce and mce[2] < minimum[2]:
                    #mn.append(mce)
                    minimum = mce
            #minimum = min(mn, key=lambda x : x[2])
            et.add(minimum)
            vt = combine_trees(vt, minimum)

    return (vt, et)

def borukva_threaded(vertices : set, edges : set):
    #vt = vertices # trees in the algorithm
    global lock
    global minimum
    vt = []
    for v in vertices:
        vt.append(frozenset([v]))
    et = set() # edges in the MST
    lock = False

    def find_mce(node):
        global lock
        global minimum
        mce = min_cost_edge(node, vt, edges)
        if mce:
            while True:
                if lock:
                    continue
                lock = True
                if mce[2] < minimum[2]:
                    minimum = mce
                lock = False
                break

    while len(vt) > 1:
        for tree in vt:
            minimum = (None, None, sys.float_info.max)
            threads = []
            for node in tree:
                threads.append(t := threading.Thread(target=find_mce(node)))
                t.start()
            for t in threads:
                t.join()
            et.add(minimum)
            vt = combine_trees(vt, minimum)

    return (vt, et)

def borukva_threaded_optimised(vertices : set, edges : set):
    #vt = vertices # trees in the algorithm
    global lock
    global minimum
    vt = []
    for v in vertices:
        vt.append(frozenset([v]))
    et = set() # edges in the MST
    lock = False

    def chunks(s : set, n):
        i = 0
        set_i = 0
        setlist = [set()] * n
        for item in s:
            if i > len(s) / n:
                i = 0
                set_i += 1
            setlist[set_i].add(item)
        return setlist


    def find_mce(chunk):
        global lock
        global minimum
        lowest = (0, 0, sys.float_info.max)
        for node in chunk:
            mce = min_cost_edge(node, vt, edges)
            if mce and mce[2] < lowest[2]:
                lowest = mce
        while True:
            if lock:
                continue
            else:
                lock = True
                if lowest[2] < minimum[2]:
                    minimum = lowest
                lock = False
                break

    while len(vt) > 1:
        for tree in vt:
            minimum = (None, None, sys.float_info.max)
            threads = []
            for chunk in chunks(tree, 4):
                threads.append(t := threading.Thread(target=find_mce(chunk)))
                t.start()
            for t in threads:
                t.join()
            et.add(minimum)
            vt = combine_trees(vt, minimum)

    return (vt, et)

def plot_graph(edges, mst_edges):
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

    print("starting threaded run")
    start_threaded = time.time()
    mst = borukva_threaded(vertices, edges) # paralelised algorithm
    end_threaded = time.time()

    print(" min spanning tree multi-threaded ".center(70,'='))
    print(mst[1])

    print("starting serial run")
    start_single = time.time()
    mst = borukva(vertices, edges) # single threaded algorithm
    end_single = time.time()

    print(" min spanning tree single-threaded ".center(70,'='))
    print(mst[1])

    print("starting optmised threaded run")
    start_threaded_optimised = time.time()
    #mst = borukva_threaded_optimised(vertices, edges) # single threaded algorithm
    end_threaded_optimised = time.time()

    print(" min spanning tree threaded optimised".center(70,'='))
    print(mst[1])

    print("time threaded: ", end_threaded - start_threaded)
    print("time without threading: ", end_single - start_single)
    print("time with optimised threading: ", end_threaded_optimised - start_threaded_optimised)

    if graphic:
        plot_graph(edges, mst[1])
