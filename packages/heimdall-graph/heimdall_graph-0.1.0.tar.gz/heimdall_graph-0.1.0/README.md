<p align="center">
  <img src="img/Heimdall.png" alt="Heimdall Logo" width="250">
</p>

## Community Detection using SVD

This package provides a set of tools for graph manipulation, analysis, and community detection using spectral methods. The core of the algorithm is based on the Singular Value Decomposition (SVD) of the signless Laplacian of a graph's adjacency matrix. This approach is particularly useful for identifying cohesive subgroups in complex systems and was originally inspired by the practical application of decomposing process matrices.

## Features:

- Graph Representation: A simple Graph class to represent nodes and edges.

- Data Input: Easily create graphs from various formats, including:

- - Adjacency matrices (CSV)
- - Edge lists (TXT)
- - Manual addition of Nodes and Edges using Graph methods

- Spectral Analysis:

- - Compute the signless Laplacian of the graph.

- - Perform dimensionality reduction using SVD on the Laplacian matrix.

- Community Detection:

- - Identify communities by analyzing the cosine similarity of nodes in the reduced dimensional space.

- - Reorder the adjacency matrix to visually highlight the detected communities.

- Visualization: Plot graphs and matrices using matplotlib for easy interpretation of results.

## Installation

Dependencies

This package requires the following Python libraries:

    pandas

    matplotlib
    
    numpy

You can install these dependencies using pip:
```Bash

pip install pandas matplotlib numpy
```


Package Installation

This project is not yet available on PyPI. To install it, please clone this repository to your local machine.
```Bash

git clone https://github.com/romulorcruz/community_detection/
cd community-detection
```


## Quick Start

Here is a basic example of how to use the package to find communities in a simple graph.

```Python
from heimdall.utils import read_matrix, signless_laplacian, community_detection
from heimdall.core import Graph, Node

# 1. Create a graph with two communities
graph = Graph()
node_list = [Node(i, f'{i+1}') for i in range(7)]
graph.add_nodes(node_list)
edge_list = [(0, 1), (0, 3), (1, 2), (3, 2), # Community 1
             (4, 5), (6, 5),                 # Community 2
             (3, 4)]                         # Bridge
graph.add_edges_by_index(edge_list)

# 2. Get the adjacency matrix
A = graph.to_matrix()

# 3. Find the optimal k number by Scree Plot using dimension reduction
L = signless_laplacian(A)
L_k, S_k = dimension_reduction(L, len(graph.nodes))

# 4. Run the community detection algorithm for k=2 communities
# This returns the reordered cosine similarity matrix and the new node order
A_cos, l_ord = community_detection(A, names, k=2)

```



Input Data Formats

You can easily load your own graph data.

    Adjacency Matrix: A CSV file representing the matrix. The file can contain a header row, which can be skipped using the skiprows parameter in the read_matrix function.

    Edge List: A text file where each line contains two node labels separated by a space, representing an edge between them. Use the add_edges_from_txt method to load this format.

Examples

The examples/ directory contains several Jupyter notebooks that provide detailed walkthroughs with well-known datasets:

    example.ipynb: A simple, programmatically generated graph to demonstrate the core functionality replicating the Somritta dummy example.

    zachary_karate_club.ipynb: Applies the algorithm to the famous Zachary's Karate Club social network.

    dolphins.ipynb: An analysis of the social network of dolphins in Doubtful Sound, New Zealand.

Theoretical Background

The community detection method implemented here is based on spectral graph theory. The main steps are:

    Signless Laplacian: The algorithm computes the signless Laplacian matrix |L| of the graph's adjacency matrix (A), defined as |L| = D + A, where D is the diagonal matrix of node degrees.

    SVD for Dimensionality Reduction: The eigenvectors corresponding to the smallest eigenvalues of |L| provide a new, lower-dimensional representation for the nodes. In this new vector space, nodes that belong to the same community are positioned closer to each other.

    Clustering: By calculating the cosine similarity between nodes in this reduced space, we can identify clusters of nodes that form distinct communities. The final output is a reordered matrix that visually confirms this community structure.

For more in-depth information, please refer to the following papers:

    Complex Networks - Structure and dynamics https://www.sciencedirect.com/science/article/pii/S037015730500462X

    Community detection in graphs using singular value decomposition https://www.researchgate.net/publication/51152953_Community_detection_in_graphs_using_singular_value_decomposition

Contributing

Contributions are welcome! Please feel free to open an issue to discuss a bug or new feature, or submit a pull request.

License

This project is licensed under the MIT License. See the LICENSE file for details.
