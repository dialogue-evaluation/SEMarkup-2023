import sys
import json
import argparse

from tqdm import tqdm

from typing import Dict, Iterable

sys.path.insert(0,'..')
from semarkup import parse_semarkup, Sentence


IS_VALID = True


def expect(condition: bool, message: str, sentence: Sentence) -> None:
    global IS_VALID
    if not condition:
        print(f"Error: {message}")
        print(f"Sentence:\n{sentence.serialize()}")
        IS_VALID = False


def load_dict_from_json(json_file_path: str) -> Dict:
    with open(json_file_path, "r") as file:
        data = json.load(file)
    return data


def validate_semarkup(sentences: Iterable[Sentence], vocab_file: str = None) -> None:
    if vocab_file is not None:
        vocab = load_dict_from_json(vocab_file)
        vocab["upos"] = set(vocab["upos"])
        vocab["xpos"] = set(vocab["xpos"])
        for cat, grams in vocab["feats"].items():
            vocab["feats"][cat] = set(grams)
        vocab["heads"] = set(vocab["heads"])
        vocab["deprels"] = set(vocab["deprels"])
        vocab["semslots"] = set(vocab["semslots"])
        vocab["semclasses"] = set(vocab["semclasses"])

    for sentence in tqdm(sentences):
        roots_count = 0

        for token in sentence:
            # UPOS
            if vocab_file is not None:
                expect(
                    token.upos in vocab["upos"],
                    f"UPOS {token.upos} is out of vocabulary.", sentence
                )
            # XPOS
            expect(
                token.xpos is None,
                f"XPOS is not _.", sentence
            )
            # Feats
            if vocab_file is not None:
                for cat, gram in token.feats.items():
                    expect(
                        cat in vocab["feats"],
                        f"grammatical category {cat} is out of vocabulary.", sentence
                    )
                    expect(
                        gram in vocab["feats"][cat],
                        f"grammeme {gram} is out of vocabulary.", sentence
                    )
            # Head
            expect(
                token.head is None or type(token.head) is int,
                f"Head must be either _ or integer.", sentence
            )
            if type(token.head) is int:
                expect(
                    0 <= token.head,
                    "Head must be non-negative.", sentence,
                )
                expect(
                    token.head <= len(sentence),
                    "Head must not exceed sentence length.", sentence,
                )
                if token.head == 0:
                    roots_count += 1
            # Semslot
            if vocab_file is not None:
                expect(
                    token.semslot in vocab["semslots"],
                    f"Semslot {token.semslot} is out of vocabulary.", sentence
                )
            # Semclass
            if vocab_file is not None:
                expect(
                    token.semclass in vocab["semclasses"],
                    f"Semclass {token.semclass} is out of vocabulary.", sentence
                )

        expect(
            roots_count,
            "There must be one ROOT (head=0) in a sentence.", sentence,
        )


def main(semarkup_file_path: str, vocab_file: str) -> None:
    print(f"Load sentences...")
    with open(semarkup_file_path, "r", encoding='utf8') as semarkup_file:
        sentences = parse_semarkup(semarkup_file, incr=True)
        validate_semarkup(sentences, vocab_file)
        if IS_VALID:
            print("Seems legit!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SEMarkup sanity check.')
    parser.add_argument(
        'semarkup_file',
        type=str,
        help='SEMarkup file to check.'
    )
    parser.add_argument(
        '-vocab_file',
        type=str,
        help="JSON file with ground-truth vocabulary (use build_vocab.py to build one)."
        "For example, you can use it if you have a correct train SEMarkup file and "
        "want to make sure test SEMarkup file doesn't have tags which are not present in test (OOV).",
        default=None
    )
    args = parser.parse_args()
    main(args.semarkup_file, args.vocab_file)

