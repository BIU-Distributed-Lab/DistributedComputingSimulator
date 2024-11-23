
class UnionFind:
    """
    A class to represent the Union-Find (Disjoint Set) data structure.

    Attributes:
        parent (list): The parent pointers for each node.
        rank (list): The rank of each tree (used for union by rank).
    """

    def __init__(self, size):
        """
        Initializes the Union-Find structure with a given size.

        Args:
            size (int): Number of elements (nodes).
        """
        self.parent = list(range(size))
        self.rank = [1] * size

    def find(self, node):
        """
        Finds the root of the node with path compression.

        Args:
            node (int): The node to find the root of.

        Returns:
            int: The root of the node.
        """
        if self.parent[node] != node:
            self.parent[node] = self.find(self.parent[node])  # Path compression
        return self.parent[node]

    def union(self, node1, node2):
        """
        Unites two sets by connecting the roots of the two nodes.

        Args:
            node1 (int): First node.
            node2 (int): Second node.
        """
        root1 = self.find(node1)
        root2 = self.find(node2)

        if root1 != root2:
            # Union by rank
            if self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            elif self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1
