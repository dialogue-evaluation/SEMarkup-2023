# Evaluation

This directory contains all the scripts, directly or indirectly related to SEMarkup evaluation.

A summary of the files in the directory:
* *evaluate.py* - evaluation script, scores how similar two SEMarkup-formatted files are,
* *scorer* - the scoring function implementation,
* *validation* - SEMarkup sanity check and test script for evaluation,
* *tag_eraser.py* - script that removes all the SEMarkup tags (except `id` and `form`) from a SEMarkup-formatted file.

## How-to

1. First, install python dependencies:
    ```
    pip install -r requirements.txt
    ```
2. `[Optional]` Read the *scorer/README.md* to get some insights on how scoring works.
3. `[Optional]` Go to *validation* directory to make sure SEMarkup files are correct.
4. Now, you are ready to evaluate.

    Here is how we use it:
    ```
    python evaluate.py train.conllu train.conllu
    ```
    And here is an output:
    ```
    Load lemma weights...
    Load feats weights...
    Build scorer...
    Evaluate...
    34414it [00:39, 876.17it/s] 

    =========================
    Total score: 1.0000
    --------
    Details:
    Lemmatization score: 1.0000
    POS score: 1.0000
    Feats score: 1.0000
    LAS: 1.0000
    UAS: 1.0000
    SemSlot score: 1.0000
    SemClass score: 1.0000
    ```

That's it.
Remember to use `-h` flag if something is unclear.

