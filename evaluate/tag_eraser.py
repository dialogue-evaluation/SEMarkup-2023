import argparse
from tqdm import tqdm

from semarkup import parse_semarkup, write_semarkup


def main(input_file_path: str, output_file_path: str) -> None:
    with open(input_file_path, "r") as file:
        sentences = parse_semarkup(file, incr=False)

    for sentence in tqdm(sentences):
        for token in sentence:
            token["lemma"] = "_"
            token["upos"] = "_"
            token["xpos"] = "_"
            token["feats"] = "_"
            token["head"] = "_"
            token["deprel"] = "_"
            token["semslot"] = "_"
            token["semclass"] = "_"

    write_semarkup(output_file_path, sentences)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Remove true tags from SEMarkup file, leaving `id` and `form` intact.'
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Input file in SEMarkup format.'
    )
    parser.add_argument(
        'output_file',
        type=str,
        help='Output file in SEMarkup with true tags removed.'
    )
    args = parser.parse_args()

    main(args.input_file, args.output_file)

