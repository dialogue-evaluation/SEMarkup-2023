#!/bin/bash

pip install pandas numpy tqdm conllu more-itertools

python3 program/score.py $1 $2

