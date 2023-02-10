# Validation

This directory contains sanity check script for SEMarkup files (*validate_semarkup.py*) and test script for *evaluation.py* (*tests.py*).

## Usage

### Sanity check

SEMarkup sanity check script has two stages.

1. First, it can be used as a standalone script. In that case it checks some basic assumptions about input SEMarkup file, like "XPOS tag must be empty (`_`)" or "head must be either empty (`_`) or non-negative integer, not exceeding max id of a sentence".
    
    One can use it as follows:
    ```
    python validate_semarkup.py train.conllu
    ```
2. The second stage requires an external vocabulary file. In that case, it ensures input SEMarkup file has no tokens out of external vocabulary. The latter can be built out of ground-truth SEMarkup file via *build_vocab.py* script.

    For example, if you have a correct train dataset (*train.conllu*), you can build the external vocabulary using: 
    ```
    python build_vocab.py train.conllu train_vocab.json
    ```
    Now, if you want to make sure *test.conllu* doesn't have OOV tags, just pass it to *validate_semarkup.py* from the first stage, but this time using optional argument:
    ```
    python validate_semarkup.py test.conllu -vocab_file=train_vocab.json
    ```
    Use `grep` command to filter the content if output is too verbose.

### Test

Use *tests.py* to validate evaluation script:
```
python tests.py train.conllu
```
