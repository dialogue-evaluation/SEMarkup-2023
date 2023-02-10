#!/bin/bash

mkdir scoring_program

# Copy codalab scripts.
cp metadata scoring_program
cp run.sh scoring_program
cp score.py scoring_program

# Copy actual evaluation scripts.
cp ../evaluate.py scoring_program
cp ../semarkup.py scoring_program
cp -r ../scorer scoring_program

