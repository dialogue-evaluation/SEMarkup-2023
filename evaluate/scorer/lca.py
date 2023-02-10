from typing import List, Optional


def find_lca(u: int, v: int, parents: List[int], depths: List[int]) -> Optional[int]:
    """
    Find Lowest Common Ancestor (LCA) in a forest formed by child-parent relations.
    """
    def uplift(node_idx: int, height: int):
        nonlocal parents

        assert height >= 0

        for _ in range(height):
            node_idx = parents[node_idx]

        return node_idx

    # Make depths equal.
    if depths[u] < depths[v]:
        v = uplift(v, depths[v] - depths[u])
    elif depths[u] > depths[v]:
        u = uplift(u, depths[u] - depths[v])

    assert(depths[u] == depths[v])
    current_depth = depths[u]

    while u != v:
        # Hit the root -> u and v are in different trees -> no LCA.
        if current_depth == 0:
            u = v = None
            break

        # Uplift vertexes simultaneously. 
        u = parents[u]
        v = parents[v]
        current_depth -= 1

    assert u == v
    lca = u

    return lca

