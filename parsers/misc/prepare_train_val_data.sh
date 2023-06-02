#!/usr/bin/env bash

mkdir ../data
./train_val_split.py ../../train.conllu ../data/train.conllu ../data/val.conllu 0.8
