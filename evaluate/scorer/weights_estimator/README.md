# Weights estimator

Some parts of SEMarkup scoring function are weighted. Weights estimator predicts these weights using statistic collected from external CoNLL-U formatted dataset (we use Russian-SynTagRus UD).

## Usage

1. Download Russian-SynTagRus dataset via _download_syntagrus.sh_ script (or use any other CoNLL-U formatted dataset the features' frequencies will be collected from):
    ```
    bash download_syntagrus.sh
    ```

2. Adjust global variables (namely `IMMUTABLE_POS` and `IMMUTABLE_POS_LEMMA_WEIGHT`) in _weights_estimator.py_ if needed.

3. Run _weights_estimator.py_ which takes CoNLL-U formatted dataset as input and dumps weights to json files.

    Example:
    ```
    $ python3 weights_estimator.py ru_syntagrus.conllu weights/lemma_weights.json weights/feats_weights.json
    ```
    Use `-h` flag for help.

4. Now you are ready to pass json files to _evaluate.py_ script.

## Details on weighting

### Lemma

**Problem**: Immutable word are easies to lemmatize than mutable ones.

**Idea**: We want immutable words to influence lemmatization score less than mutable words, i.e. the former to have less lemma weight than the latter.

To accomplish it, one have to answer two questions:

1. How to know whether a word is mutable or not?
2. How to weight words?

We make it this way:

1. There is a certain set of POS tags for Russian (namely `ADP`, `CCONJ`, `INTJ`, `PART`, `PUNCT`, `SCONJ`, `SYM` and `X`) such that if word's POS is on the list, then the word is immutable (note that converse is false: if word has a POS out of the list, it doesn't mean the word is mutable, so we likely miss some cases within this approach).

2. We tried to use statistical approach at first, but it was lack of evidence, so we ended up setting lemmatization weights manually to the values of `0.7` for mutable and `0.3` for immutable words.

So, weighting function for lemmatization looks as follows:

$$\large
LemmaWeight(word) = 
\begin{cases}
    0,3 & \text{if $word$'s POS } \in \lbrace \text{\normalsize ADP, CCONJ, INTJ, PART, PUNCT, SCONJ, SYM, X} \rbrace, \\
    0,7 & \text{otherwise}
\end{cases}
$$

### Grammatical features

**Problem**: Grammatical categories are imbalanced (`Animacy` has two grammemes, whereas `Case` has eight), which means some categories are easies to predict than others (as for example, the chance of correct grammeme prediction of `Animacy` is four times higher than that of `Case`).

**Idea**: We want big grammatical categories to influence score greater than small ones, as they are harder to guess.

The solution is straightforward: we calculate the size of each grammatical category encountered in a dataset and set its weight equal to its size. Thus, the very weighting function is simple:

$$\large
FeatsWeight(Category) = \lbrace \text{size of } Category \rbrace
$$

(you can see the weights at [feats_weights.json](weights/feats_weights.json)).
