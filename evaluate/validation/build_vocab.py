import sys
import argparse
import json

from tqdm import tqdm

from conllu.models import TokenList
from typing import Iterable

sys.path.insert(0,'..')
from semarkup import parse_semarkup


def dump_dict_to_json(data: dict, json_file: str) -> None:
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)


def build_vocab(sentences: Iterable[TokenList]) -> dict:
    upos = set()
    xpos = set()
    feats = dict()
    heads = set()
    deprels = set()
    semslots = set()
    semclasses = set()

    for sentence in tqdm(sentences):
        for token in sentence:
            upos.add(token.upos if token.upos is not None else '_')
            xpos.add(token.xpos if token.xpos is not None else '_')
            for cat, gram in token.feats.items():
                if cat not in feats:
                    feats[cat] = set()
                feats[cat].add(gram)
            heads.add(token.head if token.head is not None else '_')
            deprels.add(token.deprel if token.deprel is not None else '_')
            semslots.add(token.semslot if token.semslot is not None else '_')
            semclasses.add(token.semclass if token.semclass is not None else '_')

    # set -> list, since set is not JSON serializable.
    for cat, grams in feats.items():
        feats[cat] = list(grams)

    vocab = {
        "upos": list(upos),
        "xpos": list(xpos),
        "feats": feats,
        "heads": list(heads),
        "deprels": list(deprels),
        "semslots": list(semslots),
        "semclasses": list(semclasses),
    }
    return vocab


def main(input_file: str, dump_file: str) -> None:
    with open(input_file, "r", encoding='utf8') as file:
        sentences = parse_semarkup(file, incr=True)
        vocab = build_vocab(sentences)
        dump_dict_to_json(vocab, dump_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Use SEMarkup input file to build vocabulary for "
        "UPOS, feats, deprel, semslot and semclass tags, "
        "and dump vocabulary to a json file."
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Input SEMarkup file.'
    )
    parser.add_argument(
        'output_file',
        type=str,
        help='Output json file.'
    )
    args = parser.parse_args()
    main(args.input_file, args.output_file)

