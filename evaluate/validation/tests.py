import os
import sys
import argparse
import subprocess
import re
import tempfile
import random
import copy

from typing import List, Tuple
from conllu.models import TokenList

sys.path.insert(0,'..')
from semarkup import parse_semarkup, write_semarkup


def make_trash_tags(sentences: List[TokenList]) -> List[TokenList]:
    trash_sentences = copy.deepcopy(sentences)

    for trash_sentence in trash_sentences:
        for trash_token in trash_sentence:
            trash_token["lemma"] = '-_-'
            trash_token["upos"] = '-_-'
            trash_token["xpos"] = '-_-'
            trash_token["feats"] = '-_-'
            trash_token["head"] = -42
            trash_token["deprel"] = '-_-'
            trash_token["semslot"] = '-_-'
            trash_token["semclass"] = '-_-'

    return trash_sentences


def make_random_tags(sentences: List[TokenList]) -> List[TokenList]:
    lemmas = set()
    upos = set()
    xpos = set()
    feats = set()
    heads = set()
    deprels = set()
    semslots = set()
    semclasses = set()

    for sentence in sentences:
        for token in sentence:
            lemmas.add(token["lemma"])
            upos.add(token["upos"])
            xpos.add(token["xpos"])
            if token["feats"] is not None:
                feats.add("|".join([f"{k}={v}" for k, v in token["feats"].items()]))
            else:
                feats.add('_')
            heads.add(token["head"])
            deprels.add(token["deprel"])
            semslots.add(token["semslot"])
            semclasses.add(token["semclass"])

    lemmas = list(lemmas)
    upos = list(upos)
    xpos = list(xpos)
    feats = list(feats)
    heads = list(heads)
    deprels = list(deprels)
    semslots = list(semslots)
    semclasses = list(semclasses)

    random_tag_sentences = copy.deepcopy(sentences)
    for sentence in random_tag_sentences:
        for token in sentence:
            token["lemma"] = random.choice(lemmas)
            token["upos"] = random.choice(upos)
            token["xpos"] = random.choice(xpos)
            token["feats"] = random.choice(feats)
            token["head"] = random.choice(heads)
            token["deprel"] = random.choice(deprels)
            token["semslot"] = random.choice(semslots)
            token["semclass"] = random.choice(semclasses)

    return random_tag_sentences


def run_test(sentences, evaluate_args):
    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    write_semarkup(tmpfile.name, sentences)

    evaluate_args[2] = tmpfile.name
    print(f"Command to be run: {evaluate_args}")
    result = subprocess.run(evaluate_args, capture_output=True)

    tmpfile.close()
    os.unlink(tmpfile.name)

    out = result.stdout.decode('utf-8')
    print()
    print("Test output:")
    print(out)

    err = result.stderr.decode('utf-8')
    if len(err) != 0:
        print(err)
        assert False

    scores = []
    scores += re.findall("Total score: ([0|1]\.[0-9]*)", out)
    scores += re.findall("Lemmatization score: ([0|1]\.[0-9]*)", out)
    scores += re.findall("POS score: ([0|1]\.[0-9]*)", out)
    scores += re.findall("Feats score: ([0|1]\.[0-9]*)", out)
    scores += re.findall("LAS: ([0|1]\.[0-9]*)", out)
    scores += re.findall("UAS: ([0|1]\.[0-9]*)", out)
    scores += re.findall("SemSlot score: ([0|1]\.[0-9]*)", out)
    scores += re.findall("SemClass score: ([0|1]\.[0-9]*)", out)
    assert len(scores) == 8
    return list(map(float, scores))


def main(gold_file_path: str) -> None:

    print("Load sentences...")
    with open(gold_file_path, "r") as file:
        sentences = parse_semarkup(file, incr=False)

    evaluate_args = [
        'python3',
        '../evaluate.py',
        'here goes tmp file',
        gold_file_path,
    ]

    print()
    print("========== Gold tags test (1/5) ==========")
    print()
    scores = run_test(sentences, evaluate_args)
    for score in scores:
        assert score == 1.0
    print("Passed.")

    print()
    print("========== Trash tags test (2/5) ==========")
    print()
    trash_tag_sentences = make_trash_tags(sentences)
    scores = run_test(trash_tag_sentences, evaluate_args)
    for score in scores:
        assert score == 0.0
    print("Passed.")

    print()
    print("========== Sentence count mismatch test (3/5) ==========")
    print()
    # 1
    is_passed = True
    try:
        run_test(sentences[:-1], evaluate_args)
        # Must not reach this place.
        is_passed = False
    except Exception as e:
        print(f"Exception successfuly caught.")
    if not is_passed:
        print("TEST FAILED:")
        print("Exception expected, but none was found.")
        return
    print("Passed.")

    print()
    print("========== Sentence length mismatch test (4/5) ==========")
    print()
    is_passed = True
    try:
        short_sentences = [
            TokenList(sentence[:-1], sentence.metadata)
            for sentence in sentences
        ]
        run_test(short_sentences, evaluate_args)
        is_passed = False
    except Exception as e:
        print(f"Exception successfuly caught.")
    if not is_passed:
        print("TEST FAILED:")
        print("Exception expected, but none was found.")
        return
    print("Passed.")

    print()
    print("========== Random tags test (5/5) ==========")
    print()
    random_tag_sentences = make_random_tags(sentences)
    scores = run_test(random_tag_sentences, evaluate_args)

    print("TESTS PASSED.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate.py tester.')
    parser.add_argument(
        'gold_file',
        type=str,
        help='Seed file in SEMarkup format.'
    )
    args = parser.parse_args()

    main(args.gold_file)

