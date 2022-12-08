import sys
import random

def generate_graph(_num_nodes=26, _connection_chance=1):
    node_names = []
    edges = set()
    for i in range(_num_nodes):
        char = chr((i % 26) + 65)
        new_name = ''
        for i in range(int(i / 26) + 1):
            new_name += char
        node_names.append(new_name)

    for i in range(_num_nodes - 1):
        for j in range(i + 1, _num_nodes - 1):
            if random.randint(0, 100) / 100 < _connection_chance:
                # connect the 2 nodes
                edges.add((node_names[i], node_names[j], random.randint(1,100)))

    return edges

def write_edges(filepath, edges):
    lines = ''
    
    for e in edges:
        lines+=e[0] + "," + e[1] + "," + str(e[2]) + '\n'

    with open(filepath, "w") as f:
        f.write(lines)

if __name__ == "__main__":
    num_nodes = int(sys.argv[1])

    edges = generate_graph(_num_nodes = num_nodes)
    write_edges("data/mst-generated.csv", edges)

