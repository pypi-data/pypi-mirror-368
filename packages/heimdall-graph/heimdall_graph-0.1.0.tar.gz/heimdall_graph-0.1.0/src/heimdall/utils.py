import numpy as np
from typing import Tuple, Any, List, Optional
import heimdall.visualization

''' Subpackage for functions for the community detection by SVD decomposition, by the end, we expect a function with decomposition 
of communities by the analysis of cossine similarty matrix.

    functions:
        read matrix: Read a adjacency matrix directly by a file with the adjacency matrix data.
        signless_laplacian: Returns the signless_laplacian by the adjacency matrix.
        dimension_reduction: Reduces the dimensionality of the representactive eigenvectors of nodes received from SVD decomposition.
        cossine_similarty_matrix: Returns the cossine similarty matrix of rows.
        reorder_symetric_matrix: Returns the similarty adjacence matrix by the order of similarty between nodes.
        community_detection: Return the final ordered matrix using the other fuctions in the package

    Some functions include visualization functions from the visualization subpackage.
        
'''

Array_like = Any

def read_matrix(
    A_path: str, 
    labels_path: str, 
    delimiter: str = ','
) -> Tuple[Array_like, Array_like]:
    
    ''' Read the matrix file and the labels file using numpy loadtxt function'''

    labels = np.loadtxt(labels_path, delimiter=delimiter)
    A = np.loadtxt(A_path, delimiter=delimiter)
    return (A, labels)

def signless_laplacian(A: Array_like) -> Array_like:
    ''' Return the Signless Laplacian |L| from a Adjacency Matrix.
    
    The signless Laplacian is defined by:
    $$ |L| = A + D $$
    Where:
        D is the diagonal matrix from the array of sum of row values
        A is the adjacency matrix
        params:
            A(np.array):Expected to be a square, symmetric matrix with non-negative entries.
        returns:
            sig_L(np.array): Signless Laplacian Matrix |L|
    '''

    D = np.diag(A.sum(axis=1))
    sig_L = A + D

    return sig_L

def dimension_reduction(
    A: Array_like, 
    k: int = None,
    plot: bool = True,
    *,
    title: str = "Scree Plot"
) -> Tuple[Array_like, Array_like]:
    
    ''' Return the A matrix reduced by the k most important Eigenvalues.

    The reduced matrix is defined by:
    $$ B_{reduced} = U_k \cdot S_k \cdot V_k^{T} $$
    
    Where:
        U_k is the U matrix from SVD decomposition reduced to k columns, 
        S_k is the diagonal matrix from the S eigenvalues from SVD decomposition reduced to k most
        contributive eigenvalues
        V_k^{T} is the V^{T} matrix from SVD decomposition reduced to k rows 

        params:
            A(np.array): Matrix that will be reduced
            k(int): Number of eigenvalues from S matrix
        returns: 
            A_reduced(np.array): Matrix reduced from S_k contribution with the same dimensions from entry matrix
    '''
    if k is None:
        k = A.shape[0]
    u, s, vt = np.linalg.svd(A)
    u_k: Array_like = u[:, :k]
    s_k: Array_like = np.diag(s[:k])
    vt_k: Array_like = vt[:k, :]

    A_reduced = np.dot(np.dot(u_k, s_k), vt_k)

    if plot:
        heimdall.visualization.scree_plot(s[:k], title=title)

    return A_reduced, s[:k]

def cosine_similarity_matrix(A: Array_like) -> Array_like:

    '''Returns the Cosine similarity matrix between the rows of a matrix

    The cosine similarty matrix is defined by:
    $$ C_{i,j} = cos(\theta) = \frac{A_{i} \cdot A_{j}}{||A_{i}|| \cdot ||A_{j}||} $$
 
        params:
            A(np.array): Entry Matrix
        returns:
            C_ij(np.array): Cosine similarity matrix
    '''
    temp = []
    for i in A:
        for j in A:
            temp.append(np.dot(i,j)/(np.linalg.norm(i)*np.linalg.norm(j)))
    C_ij: Array_like = np.array(temp).reshape(A.shape)

    return C_ij

def reorder_symmetric_matrix(
    A: Array_like,
    labels: Optional[List[str]],
    plot: bool = True,
    *,
    title: str = "Cosine Similarity Matrix",
    threshold: Optional[float] = None, 
    cmap: str = "bone"
    ) -> Tuple[Array_like, List]:

    '''Reorder a symetric matrix by the descending order of elements. (Up -> Down)

        params: 
            A(np.array): Symetric matrix will be ordered
            labels(list): Labels of vertexes in order of adjacency matrix
        returns:
            A_ordered(np.array): Descending ordered matrix from A
            labels_ordered: Labels of A after ordenation
    '''
    perm_indices = np.argsort(A[:, 0])[::-1]
    A_ordered = A[np.ix_(perm_indices, perm_indices)]
    labels_ordered = [labels[i] for i in perm_indices]

    if plot:
        heimdall.visualization.similarity_matrix_plot(A_ordered, title=title, labels=labels_ordered,threshold=threshold, cmap=cmap)

    return (A_ordered, labels_ordered)

def community_detection(
    A: Array_like, 
    labels: List[str], 
    K: int, 
    plot: Optional[bool] = True,
    *,
    s_title: str = "Scree Plot",
    m_title: str = None,
    threshold: Optional[float] = None, 
    cmap: str = "bone"
) -> Tuple[Array_like, List]:
    '''' Find the signless laplacian, applies the demensionality reduction of a eigenvector by a given k, find the cosine
    similarty matrix and order it.

    params:
        A(Array_like): Adjacency matrix
        labels(List[str]): List of the nodes labels ordered in the same order of the node in adjacency matrix
        K(int): Number of representative eigenvalues will be used for dimensionality reduction of erepresentative eigenvector of node
        plot(Optional[bool]): If True provide the plot of Scree Plot of representative eigenvalues
        s_title(Optional[str]): Title of Scree Plot
        m_title(Optional[str]): Title of Cosine Similarty Matrix plot
        threshold(Optional[float]): Threshold value for Cosine Similarty Matrix plot
        cmap(Optional[str]): Compatible with matplotlib.pyplot cmap string, "bone" by default
     
    '''
    if m_title is None:
        m_title = f"Cosine Similarity Matrix K={K}"
    L = signless_laplacian(A)
    L_k, _ = dimension_reduction(L, K, plot=plot, title=s_title)
    C = cosine_similarity_matrix(L_k)
    C_ord, l_ord = reorder_symmetric_matrix(C, labels, plot=plot, title=m_title,threshold=threshold, cmap=cmap)
    
    return C_ord, l_ord
