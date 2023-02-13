import pandas as pd
from collections import Counter

from typing import Tuple, List, Dict, Any

from scorer.lca import find_lca


# Common functions.
def is_unique(series: pd.Series) -> bool:
    return len(series.unique()) == len(series)

def enumerate_column(df: pd.DataFrame, column_name: str) -> Dict[int, Any]:
    return {index: value for index, value in enumerate(df[column_name])}

def enumerate_column_inv(df: pd.DataFrame, column_name: str) -> Dict[int, Any]:
    # Ensure column has unique values.
    assert is_unique(df[column_name])
    return {value: index for index, value in enumerate(df[column_name])}


class Taxonomy:
    """
    Taxonomy of semantic classes.
    """
    SEMCLASS_TYPE_ID = 0

    def __init__(self, taxonomy_file: str):
        taxonomy_df = Taxonomy.load(taxonomy_file)
        self.parents = Taxonomy.extract_parents(taxonomy_df)
        self.depths = Taxonomy.extract_depths(taxonomy_df)
        # Semclass tricks.
        semclass_counter = Counter(taxonomy_df["Name"])
        for i, (semclass, count) in enumerate(semclass_counter.items()):
            # All taxonomy semclasses (except the most frequent one) must be unique.
            if i != 0:
                assert count == 1
        masked_semclass = semclass_counter.most_common(1)[0]
        self.semclass_to_idx = {value: index
                                for index, value in enumerate(taxonomy_df["Name"])
                                if value not in masked_semclass}

    @staticmethod
    def load(taxonomy_file_csv: str) -> pd.DataFrame:
        taxonomy = pd.read_csv(
            taxonomy_file_csv,
            dtype={
                'ID': int,
                'ParentID': 'Int64',
                'Depth': int,
                'Name': str,
            }
        )
        return taxonomy

    @staticmethod
    def extract_parents(taxonomy: pd.DataFrame) -> List[int]:
        # Enumerate nodes in a contiguous manner from 0 to max(taxonomy.index)
        node_id_to_idx = enumerate_column_inv(taxonomy, "ID")
        node_id_to_parent_id = taxonomy.set_index("ID")['ParentID'].to_dict()
        node_idx_to_parent_idx = {
            node_id_to_idx[node_id]: (node_id_to_idx[parent_id] if not pd.isna(parent_id) else -1)
            for node_id, parent_id in node_id_to_parent_id.items()
        }

        # Continuous array of parents, i.e. parents[i] = {parent of node with index i}.
        parents = [0] * len(taxonomy)

        for node_idx in range(len(taxonomy)):
            parents[node_idx] = node_idx_to_parent_idx[node_idx]

        return parents

    @staticmethod
    def extract_depths(taxonomy: pd.DataFrame) -> List[int]:
        # Enumerate nodes in a contiguous manner from 0 to max(taxonomy.index)
        node_idx_to_depth = enumerate_column(taxonomy, "Depth")

        # Continuous array of depths, i.e. depths[i] = {depth of node with index i}.
        depths = [0] * len(taxonomy)

        for node_idx in range(len(taxonomy)):
            depths[node_idx] = node_idx_to_depth[node_idx]
            assert 0 <= depths[node_idx]

        return depths

    def has_semclass(self, semclass: str) -> bool:
        return semclass in self.semclass_to_idx

    def calc_path_length(self, semclass1: str, semclass2: str) -> int:
        """
        Return length of shortest (since taxonomy is a set of trees, it's also unique) path
        between two semantic classes in taxonomy.
        If classes are in different trees, return infinity.
        """
        semclass1_idx = self.semclass_to_idx[semclass1]
        semclass2_idx = self.semclass_to_idx[semclass2]

        # Path between u and v in a tree = path from u to LCA(u,v) and path from LCA(u, v) to v.
        # So find LCA(u, v) first.
        lca_index = find_lca(semclass1_idx, semclass2_idx, self.parents, self.depths)

        if lca_index is None:
            # Classes are in different trees.
            return float("inf")

        lca_depth = self.depths[lca_index]
        semclass1_depth = self.depths[semclass1_idx]
        semclass2_depth = self.depths[semclass2_idx]

        # Since lca is an ancestor for both semclass1 and semclass2, it should be higher in taxonomy.
        assert lca_depth <= semclass1_depth and lca_depth <= semclass2_depth

        semclass1_rel_depth = semclass1_depth - lca_depth
        semclass2_rel_depth = semclass2_depth - lca_depth

        return semclass1_rel_depth + semclass2_rel_depth

