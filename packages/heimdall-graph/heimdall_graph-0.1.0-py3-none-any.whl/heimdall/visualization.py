import heimdall
import matplotlib.pyplot as plt
from typing import Any, List, Tuple, Optional
import numpy as np
Array_like = Any

'''Subpackage for functions to help with visualization of community detection'''

def scree_plot(
    S_k: Array_like, 
    title: str = "Scree Plot"
):
    ''' Scree plot for analysing single values decayment, it help for finding possible optimal k values'''
    max_k = len(S_k) + 1
    plt.figure(figsize=(8, 5))
    plt.scatter(range(1, max_k), S_k[:max_k], color='dodgerblue', s=60, edgecolor='black')
    plt.plot(range(1, max_k), S_k[:max_k], color='gray', linestyle='--')
    plt.xlabel("Component Number")
    plt.ylabel("Magnitude of Singular Value")
    plt.title(title)
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    plt.show()

def similarity_matrix_plot(
    A: Array_like,
    title: str = "Cosine Similarity Matrix",
    labels: Optional[List[str]] = None,
    threshold: Optional[float] = None, 
    cmap: str = "binary"
):
    """
    Plots a well-formatted and annotated similarity matrix heatmap.

    params:
        A (Array_like): The square similarity matrix to plot.
        title (str): The title of the plot.
        labels (Optional[List[str]]): Optional labels for the x and y axes.
        threshold (Optional[float]): If provided, binarizes the matrix for plotting.
        cmap (str): The colormap for the heatmap.
    """
    matrix_to_plot = np.copy(A)

    if threshold is not None:
        matrix_to_plot = matrix_to_plot > threshold  
    else:
        threshold = 0.5
        
    fig, ax = plt.subplots(figsize=(8, 8))

    im = ax.imshow(matrix_to_plot, cmap=cmap, vmin=0, vmax=1)
    
    cbar = fig.colorbar(im, ax=ax, use_gridspec=True)
    cbar.ax.set_ylabel("Similarity", rotation=-90, va="bottom", fontsize=12)

    if labels:
        ax.set_xticks(np.arange(len(labels)))
        ax.set_yticks(np.arange(len(labels)))
        ax.set_xticklabels(labels)
        ax.set_yticklabels(labels)

        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add text annotations for smal matrices (less than 10 rows)
    if A.shape[0] < 10:
        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                text_color = "black" if matrix_to_plot[i, j] > threshold else "white"
                ax.text(j, i, f"{A[i, j]:.2f}",
                        ha="center", va="center", color=text_color)

    ax.set_title(title, fontsize=16, pad=20)
    fig.tight_layout()
    plt.show()