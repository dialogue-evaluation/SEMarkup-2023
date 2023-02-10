import os
import sys
import argparse
import json

import numpy as np

from typing import Dict, Tuple

from scorer.scorer import SEMarkupScorer
from semarkup import parse_semarkup


OUTPUT_PRECISION = 4


def load_dict_from_json(json_file_path: str) -> Dict:
    with open(json_file_path, "r") as file:
        data = json.load(file)
    return data


def main(test_file_path: str,
         gold_file_path: str,
         taxonomy_file: str,
         lemma_weights_file: str,
         feats_weights_file: str,
         score_semantic_only: bool) -> Tuple[float]:

    print(f"Load taxonomy from {taxonomy_file}.")
    print(f"Load lemma weights from {lemma_weights_file}.")
    lemma_weights = load_dict_from_json(lemma_weights_file)
    print(f"Load feats weights from {feats_weights_file}.")
    feats_weights = load_dict_from_json(feats_weights_file)

    print("Build scorer...")
    scorer = SEMarkupScorer(
        taxonomy_file,
        semclasses_out_of_taxonomy={'_'},
        lemma_weights=lemma_weights,
        feats_weights=feats_weights
    )

    print("Evaluate...")
    with open(test_file_path, 'r') as test_file, open(gold_file_path, 'r') as gold_file:
        test_sentences = parse_semarkup(test_file, incr=True)
        gold_sentences = parse_semarkup(gold_file, incr=True)
        scores = scorer.score_sentences(test_sentences, gold_sentences)

    # Exit on errors.
    if scores is None:
        print("Errors encountered, exit.")
        return 0, 0, 0, 0, 0, 0, 0, 0

    lemma, pos, feats, head, deprel, semslot, semclass = scores
    # Average average scores into total score.
    if score_semantic_only:
        total = np.mean([head, semslot, semclass])
    else:
        total = np.mean([lemma, pos, feats, head, deprel, semslot, semclass])

    return total, lemma, pos, feats, head, deprel, semslot, semclass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='SEMarkup-2023 evaluation script.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'test_file',
        type=str,
        help='Test file in SEMarkup format with predicted tags.'
    )
    parser.add_argument(
        'gold_file',
        type=str,
        help="Gold file in SEMarkup format with true tags.\n"
        "For example, SEMarkup-2023-Evaluate/train.conllu."
    )
    script_dir = os.path.dirname(__file__)
    default_rel_taxonomy_path = "../tagsets/semantic_hierarchy.csv"
    parser.add_argument(
        '-taxonomy_file',
        type=str,
        help="File in CSV format with semantic class taxonomy.",
        default=os.path.normpath(os.path.join(script_dir, default_rel_taxonomy_path))
    )
    default_rel_lemma_weights_path = "scorer/weights_estimator/weights/lemma_weights.json"
    parser.add_argument(
        '-lemma_weights_file',
        type=str,
        help="JSON file with 'POS' -> 'lemma weight for this POS' relations.",
        default=os.path.normpath(os.path.join(script_dir, default_rel_lemma_weights_path))
    )
    default_rel_feats_weights_path = "scorer/weights_estimator/weights/feats_weights.json"
    parser.add_argument(
        '-feats_weights_file',
        type=str,
        help="JSON file with 'grammatical category' -> 'weight of this category' relations.",
        default=os.path.normpath(os.path.join(script_dir, default_rel_feats_weights_path))
    )

    parser.add_argument(
        '--score_semantic_only',
        action='store_true',
        help="A flag. If set, script scores 'head', 'semslot' and 'semclass' tags only.\n"
        "Otherwise, scores all tags: "
        "'lemma', 'upos', 'feats', 'head', 'deprel', 'semslot', 'semclass'."
    )
    args = parser.parse_args()

    total, lemma, pos, feats, head, deprel, semslot, semclass = main(
        args.test_file,
        args.gold_file,
        args.taxonomy_file,
        args.lemma_weights_file,
        args.feats_weights_file,
        args.score_semantic_only
    )

    print()
    print(f"=========================")
    print(f"Total score: {total:.{OUTPUT_PRECISION}f}")
    print(f"--------")
    print(f"Details:")
    if not args.score_semantic_only:
        print(f"Lemmatization score: {lemma:.{OUTPUT_PRECISION}f}")
        print(f"POS score: {pos:.{OUTPUT_PRECISION}f}")
        print(f"Feats score: {feats:.{OUTPUT_PRECISION}f}")
        print(f"LAS: {deprel:.{OUTPUT_PRECISION}f}")
    print(f"UAS: {head:.{OUTPUT_PRECISION}f}")
    print(f"SemSlot score: {semslot:.{OUTPUT_PRECISION}f}")
    print(f"SemClass score: {semclass:.{OUTPUT_PRECISION}f}")

