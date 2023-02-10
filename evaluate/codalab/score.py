import os
from sys import argv
import glob
import yaml

from evaluate import main


def ls(filename):
    return sorted(glob.glob(filename))

def mkdir(d):
    if not os.path.exists(d):
        os.makedirs(d)


if __name__ == "__main__":
    assert len(argv) == 3, "Incorrect number of input arguments"
    input_dir = argv[1]
    output_dir = argv[2]

    # Create the output directory, if it does not already exist and open output files
    mkdir(output_dir)
    score_file = open(os.path.join(output_dir, 'scores.txt'), 'w')
    html_file = open(os.path.join(output_dir, 'scores.html'), 'w')

    gold_files = ls(os.path.join(input_dir, 'ref', '*.conllu'))
    assert len(gold_files) <= 1, "Only one (1) file is allowed to submit."
    assert 1 <= len(gold_files), "No files found."
    gold_file = gold_files[0]

    test_files = ls(os.path.join(input_dir, 'res', '*.txt'))
    assert len(test_files) <= 1, "Only one (1) file is allowed to submit."
    assert 1 <= len(test_files), "No files found."
    test_file = test_files[0]

    taxonomy = os.path.join(input_dir, 'ref', 'semantic_hierarchy.csv')
    run_path = input_dir[:input_dir.rfind('/')]
    weights_path = os.path.join(run_path, 'program', 'scorer', 'weights_estimator', 'weights')
    lemma_weights_file = os.path.join(weights_path, 'lemma_weights.json')
    feats_weights_file = os.path.join(weights_path, 'feats_weights.json')

    total, lemma, pos, feats, head, deprel, semslot, semclass = 0, 0, 0, 0, 0, 0, 0, 0
    try:
        total, lemma, pos, feats, head, deprel, semslot, semclass = main(
            test_file, gold_file, taxonomy, lemma_weights_file, feats_weights_file, score_semantic_only=False
        )

    except Exception as inst:
        print(inst)

    # Write score corresponding to selected task and metric to the output file
    score_file.write(f"set1_score: {total:0.10f}\n")
    score_file.write(f"set2_score: {lemma:0.10f}\n")
    score_file.write(f"set3_score: {pos:0.10f}\n")
    score_file.write(f"set4_score: {feats:0.10f}\n")
    score_file.write(f"set5_score: {head:0.10f}\n")
    score_file.write(f"set6_score: {deprel:0.10f}\n")
    score_file.write(f"set7_score: {semslot:0.10f}\n")
    score_file.write(f"set8_score: {semclass:0.10f}\n")

    # Read the execution time and add it to the scores:
    try:
        metadata = yaml.load(open(os.path.join(input_dir, 'res', 'metadata'), 'r'))
        score_file.write("Duration: %0.6f\n" % metadata['elapsedTime'])
    except:
        score_file.write("Duration: 0\n")

    html_file.close()
    score_file.close()

