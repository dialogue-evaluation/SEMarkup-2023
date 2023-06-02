#!/usr/bin/env python3

import sys
import argparse

from typing import List
from conllu.models import TokenList

sys.path.append('../../evaluate')
from semarkup import parse_semarkup, write_semarkup


def train_val_split(sentences: List[TokenList], train_fraction: float) -> None:
    assert 0.0 < train_fraction < 1.0, "train_fraction must be in (0.0, 1.0) range."

    train_sentences, val_sentences = [], []

    dataset_size = len(sentences)

    for sentence_index, sentence in enumerate(sentences):
        if sentence_index <= int(train_fraction * dataset_size):
            train_sentences.append(sentence)
        else:
            val_sentences.append(sentence)

    return train_sentences, val_sentences


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Split dataset file into train and validation files.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'dataset',
        type=str,
        help='Dataset file in SEMarkup format to be splitted.'
    )
    parser.add_argument(
        'train_file',
        type=str,
        help='A train file to be produced.'
    )
    parser.add_argument(
        'val_file',
        type=str,
        help='A validation file to be produced.'
    )
    parser.add_argument(
        'train_fraction',
        type=float,
        help='A fraction of train part.'
    )
    args = parser.parse_args()

    print("Load sentences...")
    with open(args.dataset, 'r') as file:
        sentences = parse_semarkup(file, incr=False)

    train_sentences, val_sentences = train_val_split(sentences, args.train_fraction)

    write_semarkup(args.train_file, train_sentences)
    write_semarkup(args.val_file, val_sentences)
    print("Done.")

