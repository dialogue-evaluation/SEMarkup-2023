import argparse

import numpy as np
from sklearn.metrics import f1_score

from semarkup import parse_semarkup


def map_str_to_int(str_array: list) -> list:
    str_to_int = dict((key, i) for i, key in enumerate(set(str_array)))
    int_array = list(map(str_to_int.get, str_array))
    return int_array


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
    args = parser.parse_args()

    with open(args.test_file, 'r') as test_file, open(args.gold_file, 'r') as gold_file:
        test_sentences = parse_semarkup(test_file, incr=False)
        gold_sentences = parse_semarkup(gold_file, incr=False)

    semslot_pred = []
    semslot_true = []
    semclass_pred = []
    semclass_true = []

    assert len(test_sentences) == len(gold_sentences)
    for test_sentence, gold_sentence in zip(test_sentences, gold_sentences):
        assert len(test_sentence) == len(gold_sentence)
        for test_token, gold_token in zip(test_sentence, gold_sentence):
            semslot_pred.append(test_token["semslot"])
            semslot_true.append(gold_token["semslot"])
            semclass_pred.append(test_token["semclass"])
            semclass_true.append(gold_token["semclass"])

    semslot_concat = map_str_to_int(semslot_pred + semslot_true)
    semslot_pred_int, semslot_true_int = semslot_concat[:len(semslot_pred)], semslot_concat[len(semslot_pred):]
    assert len(semslot_pred_int) == len(semslot_pred) and len(semslot_true_int) == len(semslot_true)

    semclass_concat = map_str_to_int(semclass_pred + semclass_true)
    semclass_pred_int, semclass_true_int = semclass_concat[:len(semclass_pred)], semclass_concat[len(semclass_pred):]
    assert len(semclass_pred_int) == len(semclass_pred) and len(semclass_true_int) == len(semclass_true)

    print(f"Semslot micro f1: {f1_score(semslot_true_int, semslot_pred_int, average='micro'):.3f}")
    print(f"Semslot macro f1: {f1_score(semslot_true_int, semslot_pred_int, average='macro'):.3f}")
    print(f"Semclass micro f1: {f1_score(semclass_true_int, semclass_pred_int, average='micro'):.3f}")
    print(f"Semclass macro f1: {f1_score(semclass_true_int, semclass_pred_int, average='macro'):.3f}")

