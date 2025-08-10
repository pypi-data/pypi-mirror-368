"""
Visualization Tools for Genomic Data
"""
import matplotlib.pyplot as plt
import seaborn as sns

def plot_gc_distribution(gc_values):
    """Plot histogram of GC content values."""
    plt.figure(figsize=(8,5))
    plt.hist(gc_values, bins=20, color='skyblue', edgecolor='black')
    plt.xlabel('GC Content (%)')
    plt.ylabel('Frequency')
    plt.title('GC Content Distribution')
    plt.show()

def plot_heatmap(data, x_labels=None, y_labels=None, title="Heatmap"):
    """Plot a heatmap from a 2D array or DataFrame."""
    plt.figure(figsize=(8,6))
    sns.heatmap(data, xticklabels=x_labels, yticklabels=y_labels, cmap="viridis", annot=True)
    plt.title(title)
    plt.show()

def plot_phylogenetic_tree(tree):
    """Stub for phylogenetic tree plotting (requires tree object)."""
    # Implementation depends on tree format (e.g., Biopython)
    pass
