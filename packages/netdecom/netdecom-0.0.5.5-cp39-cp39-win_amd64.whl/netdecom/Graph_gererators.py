import random
import igraph as ig
import networkx as nx

try:
    import numpy as np
except ImportError:
    np = None  # If numpy is not available, set np to None


def generator_connected_ug(n, p, class_type="ig"):
    """
    Generates a random connected graph with n nodes and a probability p of adding edges.
    Supports both igraph and networkx based on class_type parameter.
    
    :param n: Number of nodes in the graph
    :param p: Probability of adding an edge between any two nodes (after ensuring connectivity)
    :param class_type: "ig" for igraph graph (default), "nx" for networkx graph
    :return: A connected graph object of the specified type
    """
    if np is None:
        raise ImportError("This function requires numpy, which is not installed on your system.")
    
    if class_type == "nx":
        # NetworkX version
        g = nx.random_tree(n)
        adj_matrix = np.zeros((n, n), dtype=bool)
        for u, v in g.edges():
            adj_matrix[u, v] = True
            adj_matrix[v, u] = True
        
        row_indices, col_indices = np.triu_indices(n, k=1)
        candidate_mask = ~adj_matrix[row_indices, col_indices]
        random_vals = np.random.rand(len(row_indices))
        edges_to_add_mask = (random_vals < p) & candidate_mask
        edges_to_add = [(row_indices[i], col_indices[i]) for i in np.where(edges_to_add_mask)[0]]
        g.add_edges_from(edges_to_add)
        return g
    
    else:
        # igraph version (default)
        g = ig.Graph.Tree(n, 2)
        adj_matrix = np.zeros((n, n), dtype=bool)
        for u, v in g.get_edgelist():
            adj_matrix[u, v] = True
            adj_matrix[v, u] = True
        
        row_indices, col_indices = np.triu_indices(n, k=1)
        candidate_mask = ~adj_matrix[row_indices, col_indices]
        random_vals = np.random.rand(len(row_indices))
        edges_to_add_mask = (random_vals < p) & candidate_mask
        edges_to_add = [(row_indices[i], col_indices[i]) for i in np.where(edges_to_add_mask)[0]]
        if edges_to_add:
            g.add_edges(edges_to_add)
        return g






# This function generates a connected Directed Acyclic Graph (DAG) with n nodes.
# It first creates a directed tree and then probabilistically adds edges with probability p.
# Each node has a maximum of `max_parents` parents, with the default value being 3.
# Additionally, the number of nodes with exactly 3 parents is constrained to not exceed 5% of the total number of nodes.

def generate_connected_dag(n, p, max_parents=3):
    """
    Generate a connected Directed Acyclic Graph (DAG)
    
    Parameters:
        n: Number of nodes
        p: Probability of adding an edge
        max_parents: Maximum number of parents allowed for each node (default is 3)
    
    Additional constraint:
        The number of nodes with 3 parents should not exceed 5% of the total number of nodes
    """
    # Calculate the maximum number of nodes that can have 3 parents (5% of n)
    max_4_parents = int(0.05 * n)
    current_4_parents = 0
    
    # Generate a directed tree
    tree = nx.DiGraph()
    tree.add_nodes_from([f"X{i}" for i in range(n)])
    
    # Build the connected tree structure
    for i in range(1, n):
        possible_parents = [
            f"X{j}" for j in range(i) 
            if tree.in_degree(f"X{j}") < max_parents and
            (tree.in_degree(f"X{j}") != max_parents - 1 or current_4_parents < max_4_parents)
        ]
        
        if possible_parents:
            parent = random.choice(possible_parents)
            tree.add_edge(parent, f"X{i}")
            if tree.in_degree(parent) == max_parents:
                current_4_parents += 1
    
    # Add additional edges based on probability p
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
                
            if random.random() < p:
                target_degree = tree.in_degree(f"X{j}")
                
                # Check all constraints
                if (target_degree < max_parents and 
                    (target_degree != max_parents - 1 or current_4_parents < max_4_parents)):
                    
                    new_tree = tree.copy()
                    new_tree.add_edge(f"X{i}", f"X{j}")
                    
                    if nx.is_directed_acyclic_graph(new_tree):
                        tree.add_edge(f"X{i}", f"X{j}")
                        if tree.in_degree(f"X{j}") == max_parents:
                            current_4_parents += 1
    
    # Final verification
    assert nx.is_directed_acyclic_graph(tree), "The generated graph is not a DAG"
    assert nx.is_weakly_connected(tree), "The graph is not connected"
    assert all(d <= max_parents for _, d in tree.in_degree()), f"There are nodes with more than {max_parents} parents"
    
    # Verify the 4-parent constraint
    nodes_with_4_parents = sum(1 for _, d in tree.in_degree() if d == max_parents)
    assert nodes_with_4_parents <= max_4_parents, f"The number of nodes with 4 parents exceeds {n*0.05}"
    
    return tree

def random_connected_dag(n, p):
    """
    Generate a random Directed Acyclic Graph (DAG) with n nodes and edge probability p. from wuwt461@nenu.edu.cn
    """

    DAG = nx.DiGraph()
    DAG.add_nodes_from(range(n))

    # Randomly shuffle the node order
    nodes = list(range(n))
    random.shuffle(nodes)

    # Create tree structure to ensure connectivity
    for i in range(1, n):
        parent = random.choice(nodes[:i])
        DAG.add_edge(parent, nodes[i])

    # Add additional edges (only from already present nodes to those that appear later)
    for i in range(n):
        for j in range(i+1, n):
            if random.random() < p:
                DAG.add_edge(nodes[i], nodes[j])

    return DAG



