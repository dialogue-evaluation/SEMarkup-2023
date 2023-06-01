# Parsers

Here you can find details about the SEMarkup parsers: their quality, architecture and implementation, as well as a usage guide.

## Table of Contents
1. [Models](#models)
    1. [Base model](#base-models)
    2. [Top-k dictionary lemmatization](#baseline-modifications)
    3. [Training notes](#training-notes)
2. [Implementation notes](#implementation-notes)
3. [Usage](#usage)

## Models

### Base model

The base model for SEMarkup-2023 task is a multi-task BERT-encoded tagger. It is based on Anastasyev's [Joint Morpho-Syntactic Parser](https://www.dialog-21.ru/media/5069/anastasyevdg-147.pdf) (a GramEval2020 winner) extended with semantic tags, and has the following structure:

![img](/img/BaselineArchitecture.png)

#### Encoder

We use pre-trained [rubert-tiny](https://huggingface.co/cointegrated/rubert-tiny) (which is 15 times smaller than a well-known [DeepPavlov's RuBERT](https://huggingface.co/DeepPavlov/rubert-base-cased)) as an encoder, for it is fast yet quite effective.

#### Classifiers

As SEMarkup-2023 consists of multiple tags, the model has few heads:

* **Lemma classifier** is a nonlinear feed-forward classifier predicting lemmatization rules.
    
    > Anastasyev D. G.: It is based on modification rules that have to be applied to a word to obtain its lemma. Only three spelling modification types might be applied: cut N symbols from the prefix of the word, cut N symbols from its suffix and append a specific sequence of symbols to its suffix.
    
    Since scoring function is case-insensitive, the other three modifications ("lower", "capitalize", "upper") introduced in the paraer, are omitted.
    
* **POS&Feats classifier** is a feed-forward classifier predicting joint POS and grammatical features.

    > Anastasyev D. G.: The POS tag and morphological features were simply concatenated (e.g., `NOUN|Animacy=Inan|Case=Gen|Gender=Masc|Number=Plur`) and model had to perform multiclass classification with a significant number of classes.

* **Syntax classifier** is [Dozat and Manning's](https://arxiv.org/abs/1611.01734) biaffine dependency classifier.

* **Semslot classifier** and **Semclass classifier** are another two nonlinear feed-forward classifiers, simply predicting semslot and semclass tags.

The configuration file for the model: [baseline.jsonnet](configs/baseline.jsonnet)

#### Quality*

|         Encoder                 |  Total | Lemma  |  POS   | Features |  UAS   |  LAS   | SemSlot | SemClass |
| :-----------------------------: | :----: | :----: | :----: | :------: | :----: | :----: | :-----: | :------: |
| xlm-roberta-base                | 95.05% | 97.33% | 98.80% |  96.76%  | 93.50% | 89.79% |  94.30% |  94.83%  |
| rubert-base-cased               | 95.04% | 97.10% | 98.83% |  96.77%  | 93.64% | 89.88% |  94.24% |  94.89%  |
| rubert-tiny2                    | 93.04% | 96.45% | 98.50% |  95.76%  | 90.48% | 86.18% |  90.54% |  93.35%  |
| rubert-tiny (_baseline_)        | 92.17% | 96.10% | 98.19% |  95.32%  | 90.03% | 85.59% |  87.79% |  92.17%  |

\* - Hard track. Base track quality can be obtained from the former as a subset of scores.

### Top-k dictionary lemmatization

The baseline lemmatization approach frequently produces malformed lemmas, e.g. _введенного_ — _введсти_, _второму_ — _вторый_.
It is suggested to use an external dictionary of correct lemmas in order to reduce the number of such 'glitches'.

The idea is simple: we now allow lemmatizer to choose the best lemma out of top-k most probable lemmas (not only one, as it was before).
To be more specific, during the inference we look at the top-k highest-scored lemmas. If the most probable lemma is present in the external dictionary, then it is the answer. Otherwise, go to the second most probable lemma and check if it is present in the dictionary, and so on.

Here is an example for input token _бытует_ and top-5 predicted lemmas. Note that we chose the fourth one, since first three lemmas are out of the dictionary:
```
Token: бытует
   бытуть
   бытевать
   бытуют
-> бытовать  (correct)
   быть
```

If none of the top-k lemmas is found on the dictionary, the first one is chosen as the answer. This move is explained by the fact that the ground-truth lemma might be out of the dictionary, for example _историко-краеведческий_, so the most probable lemma may still be correct, even though it is not on the dictionary:
```
Token: историко-краеведческий
-> историко-краеведческий  (correct)
   историко-краеведческ
   историко-краеведческй
   историко-краеведческая
   историко-краеведческа
```

With that said, it might be a good reason not to set $k$ too high, for the probability to encounter dictionary (bit not a correct one!) lemma increases. For example, suppose the sixth most probable lemma in the example above is _история_, then if we set $k$ to 10, the _история_ will be choosen as an answer, for it is the dictionary lemma:
```
Token: историко-краеведческий
   историко-краеведческий  (correct)
   историко-краеведческ
   историко-краеведческй
   историко-краеведческая
   историко-краеведческа
-> история                 (wrong)
```

We suggest setting $k$ to 5 or 10.

The configuration file for the model: [topk-lemma.jsonnet](configs/topk-lemma.jsonnet)

#### Quality

The test scores for $k = 10$.

|         Encoder                 |  Total | Lemma  |  POS   | Features |  UAS   |  LAS   | SemSlot | SemClass |
| :-----------------------------: | :----: | :----: | :----: | :------: | :----: | :----: | :-----: | :------: |
| xlm-roberta-base                | 95.09% | 97.66% | 98.80% |  96.76%  | 93.50% | 89.79% |  94.30% |  94.83%  |
| rubert-tiny2                    | 93.15% | 97.21% | 98.50% |  95.76%  | 90.48% | 86.18% |  90.54% |  93.35%  |

### Training notes

The models are trained in a multi-task manner, i.e. each head has its own loss, and the resulting loss is the sum of the losses. Also, we use slanted triangular learning rate scheduler along with gradual unfreezing and discriminative fine-tuning. 

We splitted the base dataset (*train.conllu*) into train and validation parts (using *misc/train_val_split.py* script) so that train is 80% and validation is 20% of the base dataset size.

## Implementation notes

The models are implemented using [AllenNLP](https://github.com/allenai/allennlp) framework. Ones who are not familiar with the framework should read [AllenNLP guide](https://guide.allennlp.org/) first. It takes some time, but totaly worth it.

Whether you understand the way AllenNLP operates or not, you can go to the [configs](configs/) for configuration details like number of parameters in classifiers, batch size, learning rate, scheduler parameters and etc. It is quite intuitive, but one might need to know the way AllenNLP operates in order to fully understand it.

## Usage

We use AllenNLP command line tools to train and evaluate parsers. Run `allennlp --help` for details.

### Train
```
allennlp train configs/baseline.jsonnet \
    --serialization-dir serialization_dir \
    --include-package src
```

### Predict
```
allennlp predict serialization_dir/model.tar.gz train.conllu \
    --output-file predictions.txt \
    --include-package src \
    --predictor morpho_syntax_semantic_predictor \
    --use-dataset-reader
```
