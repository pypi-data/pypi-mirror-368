import networkx as nx
import igraph as ig
import os

def get_example(file_name, class_type="ig"):
    """
    Reads the specified example file and returns the corresponding graph object (NetworkX or igraph).
    """
    available_files = [
        "Animal-Network.txt",
        "as20000102.txt",
        "bio-CE-GN.txt",
        "bio-CE-GT.txt",
        "bio-DR-CX.txt",
        "CA-CondMat.txt",
        "CA-HepTh.txt",
        "Email-Enron.txt",
        "mammalia-voles-rob-trapping-22.txt",
        "rec-amazon.txt",
        "rec-eachmovie.txt",
        "rec-movielens-tag-movies-10m.txt",
        "rec-movielens-user-movies-10m.txt",
        "rec-movielens.txt",
        "rec-yelp-user-business.txt"
    ]

    if file_name not in available_files:
        raise ValueError(f"File '{file_name}' not found. Available files: {', '.join(available_files)}")

    # Manually specify the correct path to the examples folder
    examples_path = os.path.join(os.path.dirname(__file__), 'examples')  # Get the path to examples directory
    file_path = os.path.join(examples_path, file_name)  # Full file path

    # Check if the file exists in the examples directory
    if not os.path.exists(file_path):
        raise ValueError(f"File '{file_name}' does not exist at {file_path}")

    # Reading the file and processing as a graph
    edges = set()  # Use a set to automatically avoid duplicate edges
    nodes = set()  # Create a set to keep track of unique nodes
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            elements = line.strip().split()
            if len(elements) == 2:
                u, v = int(elements[0]), int(elements[1])
                if u != v:  # Avoid self-loops
                    # Ensure edges are always stored as (min, max) to standardize direction
                    edges.add((min(u, v), max(u, v)))  # Standardize edge direction
                    nodes.update([u, v])  # Add both nodes to the set

    # Process the graph based on the class_type specified
    if class_type == "nx":
        # Process as NetworkX graph
        G = nx.Graph()
        G.add_nodes_from(nodes)  # Add the unique nodes
        G.add_edges_from(edges)  # Add the standardized edges

        # Print the NetworkX graph information
        print(f"NetworkX Graph - Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
        return G

    elif class_type == "ig":
        # Process as igraph graph
        G_ig = ig.Graph(directed=False)
        G_ig.add_vertices(len(nodes))  # Add vertices
        G_ig.add_edges(list(edges))  # Add the standardized edges

        # Print the igraph graph information
        print(f"igraph Graph - Nodes: {G_ig.vcount()}, Edges: {G_ig.ecount()}")
        return G_ig

    else:
        raise ValueError("Invalid class_type. Please specify 'nx' for NetworkX or 'ig' for igraph.")