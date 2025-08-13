from typing import Any, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
import os

''' Subpackage for Complex Systems Objects and Methods

    Objects:
        Node: The basic element of a Graph. It stores its index, a human-readable 
              label, and information about its connections and degree.
        Graph: A collection of Nodes and the links between them. This class is designed 
               for undirected graphs and includes methods for construction, modification, 
               and visualization, as well as for converting the graph to and from a 
               matrix representation.
'''


Array_like = Any
x,y = 'x','y'

class Node:
    ''' Basic element of a Graph.
    
    A Node is defined by its unique index and an optional label. It maintains a list 
    of its direct connections to other nodes.
    
    Attributes:
        index (int): A unique integer identifier for the node.
        label (str): A human-readable label. Defaults to the node's index if not provided.
        edges (List[Node]): A list of Node objects to which this node is directly connected.
        degree (int): The number of edges connected to this node.
    '''
    def __init__(self, index: int, label: str = None):
        ''' Initializes a Node object.
        
        params:
            index (int): The unique integer identifier for the node.
            label (str): An optional string label for the node. If None, the index is used as the label.
        '''
        self.index = index
        self.label = label if label is not None else str(index)
        self.edges = []
        self.degree = 0
        
    def link(self, other_node: 'Node'):
        ''' Creates a directed link from this node to another node.
        
        Note: For an undirected graph, this method should be called on both nodes in a pair.
        
        params:
            other_node (Node): The node to which a link will be established.
        '''
        self.edges.append(other_node)
        self.degree += 1

    def __repr__(self) -> str:
        ''' Returns a detailed string representation of the Node. '''
        edge_labels = [n.label for n in self.edges]
        return f'Node Label: {self.label}\nNode Index: {self.index}\nNode Edges: {edge_labels}\nNode Degree: {self.degree}'
            
class Graph:
    ''' Represents a set of nodes and the links between them for an undirected graph.
    
    A Graph is mathematically defined as a pair of sets:
    $$ G = (\\mathcal{N}, \\mathcal{E}) $$
    Where:
        - $\\mathcal{N}$ is the set of nodes (vertices).
        - $\\mathcal{E}$ is the set of edges (links) connecting pairs of nodes.
        
    This class assumes the graph is undirected, meaning if a node `A` is linked to `B`,
    `B` is also considered linked to `A`.

    Attributes:
        nodes (List[Node]): A list of all Node objects in the graph, representing $\\mathcal{N}$.
        edges (List[Tuple[Node, Node]]): A list of all unique edges, represented as tuples of Node objects, corresponding to $\\mathcal{E}$.
        n (int): The total number of nodes in the graph (the cardinality of $\\mathcal{N}$).
        k (int): The total number of unique edges in the graph (the cardinality of $\\mathcal{E}$).
    '''
    def __init__(self, nodes: List[Node] = None):
        ''' Initializes a Graph object from a list of nodes.
        
        params:
            nodes (List[Node]): An optional list of Node objects to initialize the graph with.
                                 The graph's edge list will be populated based on the `edges`
                                 attribute of each node provided.
        '''
        self.nodes = list(nodes) if nodes is not None else []
        self.edges = [] # List[Tuple[Node, Node]]
        
        for node in self.nodes:
            for other_node in node.edges:
                # Add edge only if its reverse is not present
                if (node, other_node) not in self.edges and (other_node, node) not in self.edges:
                    self.edges.append((node, other_node))
        
        self.n = len(self.nodes)
        self.k = len(self.edges)

    def __repr__(self) -> str:
        ''' Returns a summary string representation of the Graph. '''
        nodes_repr = [node.label for node in self.nodes]
        edges_repr = [(n1.label, n2.label) for n1, n2 in self.edges]
        return f'Nodes: {nodes_repr}\nEdges by node label: {edges_repr}\nNumber of nodes: {self.n}\nNumber of links: {self.k}'

    def _get_last_index(self) -> int:
        ''' Private method to get the next available node index. '''
        return len(self.nodes)

    def add_node(self, node: Node):
        ''' Adds a single Node object to the graph.
        
        The graph's node and edge lists are updated accordingly.
        
        params:
            node (Node): The Node object to be added.
        '''
        self.nodes.append(node)
        self.n = len(self.nodes)

    def add_nodes(self, node_list: List[Node]):
        ''' Adds multiple Node objects to the graph from a list.
        
        params:
            node_list (List[Node]): A list of Node objects to add.
        '''
        for node in node_list:
            self.add_node(node)

    def add_edge(self, node: Node, other_node: Node):
        ''' Adds an undirected edge between two nodes.
        
        This method establishes a link from `node` to `other_node` and from `other_node`
        to `node`. The edge is then added to the graph's edge list.
        
        params:
            node (Node): The first node in the edge pair.
            other_node (Node): The second node in the edge pair.
        '''
        node.link(other_node)
        other_node.link(node)
        if (node, other_node) not in self.edges and (other_node, node) not in self.edges:
            self.edges.append((node, other_node))
            self.k += 1

    def add_edge_by_index(self, node_index: int, other_node_index: int):
        ''' Adds an edge using the indices of the two nodes.
        
        params:
            node_index (int): The index of the first node.
            other_node_index (int): The index of the second node.
        '''
        node1 = self.nodes[node_index]
        node2 = self.nodes[other_node_index]
        self.add_edge(node1, node2)

    
    def add_edges_by_index(self, edge_list: List[Tuple[int,int]]):
        ''' Recursively adds an edge using the indices of the two nodes.
        
        params:
            node_list(List[Tuple[int,int]]): List of tuple of edge nodes indexes.
        '''
        for edge in edge_list:
            self.add_edge_by_index(edge[0], edge[1])

    def add_edges_from_txt(self, file_path: str, skiprows: int = 0):
        ''' Adds edges from a text file.
        
        The file should contain two columns of node labels representing edges. If a node
        label from the file does not exist in the graph, a new node is automatically
        created and added.
        
        params:
            file_path (str): The relative path to the .txt file.
            skiprows (int): The number of initial rows to skip in the file.
        '''
        temp = np.loadtxt(file_path, skiprows=skiprows, dtype=str)
        if temp.ndim == 1: # Handle case with a single edge in the file
             temp = temp.reshape(1, -1)

        for row in temp:
            node_label, other_node_label = row
            
            # Find existing nodes or create new ones
            node = next((n for n in self.nodes if n.label == node_label), None)
            other_node = next((n for n in self.nodes if n.label == other_node_label), None)
            
            if node is None:
                print(f'Node with label "{node_label}" not found. Creating new node.')
                node = Node(self._get_last_index(), node_label)
                self.add_node(node)
            if other_node is None:
                print(f'Node with label "{other_node_label}" not found. Creating new node.')
                other_node = Node(self._get_last_index(), other_node_label)
                self.add_node(other_node)
                
            self.add_edge(node, other_node)

    def from_matrix(self, A: Array_like):
        ''' Constructs the graph's nodes and edges from an adjacency matrix.
        
        This method will overwrite any existing nodes and edges in the graph.
        
        params:
            A (np.array): A square, symmetric adjacency matrix where A[i, j] = 1 
                          indicates an edge between node i and node j.
        '''
        self.nodes = [Node(i) for i in range(A.shape[0])]
        self.edges = []
        
        # Use np.where to find all connected pairs
        rows, cols = np.where(A == 1)
        
        for i, j in zip(rows, cols):
            self.nodes[i].link(self.nodes[j])
            if i < j:
                self.edges.append((self.nodes[i], self.nodes[j]))
                
        self.n = len(self.nodes)
        self.k = len(self.edges)

    def plot(self, pos: dict = None, show_labels: bool = True):
        """
        Generates a plot of the graph structure using matplotlib.

        params:
            pos (dict): An optional dictionary mapping node indices to (x, y) coordinates.
                        If None, nodes are arranged in a circle.
            show_labels (bool): If True, displays the labels of the nodes on the plot.
        """
        if pos is None:
            # Create a circular layout if no position is provided
            angle = np.linspace(0, 2 * np.pi, self.n, endpoint=False)
            pos = {node.index: (np.cos(a), np.sin(a)) for node, a in zip(self.nodes, angle)}

        fig, ax = plt.subplots(figsize=(8, 8))

        # Plot edges
        for n1, n2 in self.edges:
            x_values = [pos[n1.index][0], pos[n2.index][0]]
            y_values = [pos[n1.index][1], pos[n2.index][1]]
            ax.plot(x_values, y_values, color='gray', zorder=1)

        # Plot nodes
        for node in self.nodes:
            x, y = pos[node.index]
            ax.scatter(x, y, s=500, color='skyblue', zorder=2, edgecolors='black')
            if show_labels:
                ax.text(x, y, str(node.label), color='black', ha='center', va='center', fontsize=10, zorder=3)

        plt.title("Graph Visualization", fontsize=16)
        plt.axis('off')
        plt.tight_layout()
        plt.show()

    def to_matrix(self, save: bool = False, path: str = 'data') -> Array_like:
        ''' Generates the adjacency matrix for the current graph.
        
        Optionally saves the matrix and corresponding node labels to files.

        params:
            save (bool): If True, saves the adjacency matrix and labels to disk.
            path (str): The directory where the files will be saved.
            
        returns:
            np.array: The (n x n) adjacency matrix of the graph.
        '''
        a_matrix = np.zeros((self.n, self.n), dtype=int)
        
        # Create a mapping from node object to its index
        node_to_idx = {node: i for i, node in enumerate(self.nodes)}
        
        for n1, n2 in self.edges:
            idx1 = node_to_idx[n1]
            idx2 = node_to_idx[n2]
            a_matrix[idx1, idx2] = 1
            a_matrix[idx2, idx1] = 1
        
        if save:
            os.makedirs(path, exist_ok=True)
            matrix_file = os.path.join(path, 'adjacency_matrix.csv')
            labels_file = os.path.join(path, 'node_labels.txt')
            
            np.savetxt(matrix_file, a_matrix, fmt='%d', delimiter=',')
            np.savetxt(labels_file, self.to_labels_list(), fmt='%s')
            print(f"Matrix saved to {matrix_file}")
            print(f"Labels saved to {labels_file}")

        return a_matrix
    
    def to_labels_list(self) -> List[str]:
        ''' Returns an ordered list of node labels.
        
        The order of labels corresponds to the row/column order in the adjacency matrix.
        
        returns:
            List[str]: A list of node labels.
        '''
        return [node.label for node in self.nodes]
    