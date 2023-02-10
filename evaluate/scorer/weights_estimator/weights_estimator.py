import argparse
import json
import re

import conllu

import numpy as np

from conllu.models import TokenList, Token
from typing import Iterable, List, Tuple, Dict, Optional, TextIO

from tqdm import tqdm


CONLLU_FIELDS = [
    "id",
    "form",
    "lemma",
    "upos",
    "xpos",
    "feats",
    "head",
    "deprel"
]

# Adjust if needed.
IMMUTABLE_POS = {
    'ADP',
    'CCONJ',
    'INTJ',
    'PART',
    'PUNCT',
    'SCONJ',
    'SYM',
    'X'
}
IMMUTABLE_POS_LEMMA_WEIGHT = 0.3


def dump_dict_to_json(data: Dict, json_file: str) -> None:
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)


def collect_tagsets(sentences: Iterable[TokenList]) -> Tuple[set, Dict[str, set]]:
    pos_set = set()
    feats_set = {}

    for sentence in tqdm(sentences):
        for token in sentence:
            pos = token["upos"]
            pos_set.add(pos)

            feats = token["feats"]
            if feats is not None:
                for gram_cat, grammeme in feats.items():
                    if gram_cat not in feats_set:
                        feats_set[gram_cat] = set()
                    feats_set[gram_cat].add(grammeme)

    return pos_set, feats_set


def set_lemma_weights(pos_set: set,
                      immutable_pos: set,
                      immutalbe_pos_lemma_weight: float) -> Dict[str, float]:
    """
    If word is immutalbe, its lemma is trivial.
    We want such cases to have less lemmatization score than mutable ones.

    OK, how to find out whether word is mutable or not?
    Simple: there is a certain set of POS tags which words are known to be immutable.
    """
    # Lemma weight for immutable POS must be smaller than that of a mutable.
    assert 0.0 <= immutalbe_pos_lemma_weight <= 0.5

    lemma_weights = {}
    for pos in pos_set:
        if pos in immutable_pos:
            lemma_weights[pos] = immutalbe_pos_lemma_weight
        else:
            lemma_weights[pos] = 1 - immutalbe_pos_lemma_weight

    return lemma_weights


def estimate_feats_weights(feats_set: Dict[str, set]):
    feats_weights = {}
    for gram_cat, grammemes in feats_set.items():
        # Weight of grammatical category is protortional to its size.
        # It makes sense, for one can easily guess heads or tails,
        # but when it comes to dice, the odds are rather smaller.
        feats_weights[gram_cat] = len(grammemes)

    return feats_weights


def main(tagset_file_path: str, lemma_weights_file_path: str, feats_weights_file_path: str):
    with open(tagset_file_path, 'r') as tagset_file:
        sentences = conllu.parse_incr(tagset_file, fields=CONLLU_FIELDS)
        pos_set, feats_set = collect_tagsets(sentences)

    lemma_weights = set_lemma_weights(pos_set, IMMUTABLE_POS, IMMUTABLE_POS_LEMMA_WEIGHT)
    feats_weights = estimate_feats_weights(feats_set)

    print("Dump weights.")
    dump_dict_to_json(lemma_weights, lemma_weights_file_path)
    dump_dict_to_json(feats_weights, feats_weights_file_path)
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This script estimates lemma- and feats- weights based on their frequencies in a tagset."
    )
    parser.add_argument(
        'tagset_file',
        type=str,
        help='Input tagset file in CONLL-U format.'
    )
    parser.add_argument(
        'lemma_weights_file',
        type=str,
        help='Output JSON file with lemma weights estimated for each POS in tagset.'
    )
    parser.add_argument(
        'feats_weights_file',
        type=str,
        help='Output JSON file with feats weights estimated based .'
    )
    args = parser.parse_args()

    main(args.tagset_file, args.lemma_weights_file, args.feats_weights_file)

