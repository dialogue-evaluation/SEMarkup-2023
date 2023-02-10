# Baseline model

This is a baseline model for SEMarkup-2023 task.

Here you can find details about the model quality, implementation, as well as a usage guide.

## Quality

**Base track**

| Total | UAS   | SemSlot | SemClass |
| :---: | :---: | :-----: | :------: |
| 90.0% | 90.0% |  87.8%  |  92.2%   |

**Hard track**

| Total | Lemma | POS   | Features |  UAS  |  LAS   | SemSlot | SemClass |
| :---: | :---: | :---: | :------: | :---: | :----: | :-----: | :------: |
| 92.2% | 96.1% | 98.2% |  95.3%   | 90.0% |  85.6% |  87.8%  |  92.2%   |

## Architecture

The model is a multi-task BERT-encoded tagger. It is based on Anastasyev's [Joint Morpho-Syntactic Parser](https://www.dialog-21.ru/media/5069/anastasyevdg-147.pdf) (a GramEval2020 winner) extended with semantic tags, and has the following structure:

![img](/img/BaselineArchitecture.png)

### Encoder

We use pre-trained [rubert-tiny](https://huggingface.co/cointegrated/rubert-tiny) (which is 15 times smaller than a well-known [DeepPavlov's RuBERT](https://huggingface.co/DeepPavlov/rubert-base-cased)) as an encoder, for it is fast yet quite effective.

### Classifiers

As SEMarkup-2023 consists of multiple tags, the model has few heads:

* **Lemma classifier** is a nonlinear feed-forward classifier predicting lemmatization rules.
    
    > Anastasyev D. G.: It is based on modification rules that have to be applied to a word to obtain its lemma. Only three spelling modification types might be applied: cut N symbols from the prefix of the word, cut N symbols from its suffix and append a specific sequence of symbols to its suffix.
    
    Since scoring function is case-insensitive, the other three modifications ("lower", "capitalize", "upper") introduced in the paraer, are omitted.
    
* **POS&Feats classifier** is a feed-forward classifier predicting joint POS and grammatical features.

    > Anastasyev D. G.: The POS tag and morphological features were simply concatenated (e.g., `NOUN|Animacy=Inan|Case=Gen|Gender=Masc|Number=Plur`) and model had to perform multiclass classification with a significant number of classes.

* **Syntax classifier** is [Dozat and Manning's](https://arxiv.org/abs/1611.01734) biaffine dependency classifier.

* **Semslot classifier** and **Semclass classifier** are another two nonlinear feed-forward classifiers, simply predicting semslot and semclass tags.

### Training

The whole model is learned in a multi-task manner, i.e. each head has its own loss, and the resulting loss is the sum of the losses. Also, we use slanted triangular learning rate scheduler along with gradual unfreezing and discriminative fine-tuning. 

We splitted the base dataset (*train.conllu*) into train and validation parts (using *misc/train_val_split.py* script) so that train is 80% and validation is 20% of the base dataset size.

## Implementation

The model is implemented using AllenNLP framework. Ones who are not familiar with the framework should read [AllenNLP guide](https://guide.allennlp.org/) at first. It takes some time, but totaly worth it.

Whether you understand the way AllenNLP operates or not, you can go to the [tiny.jsonnet](https://github.com/houcha/SEMarkup-2023-Baseline/blob/main/baseline/parser/configs/tiny.jsonnet) for configuration details like number of parameters in classifiers, batch size, learning rate, scheduler parameters and etc. It is quite intuitive, but one might need to know how AllenNLP works in order to fully understand it.

## Usage

We use AllenNLP command line tools for training, validating and testing. Once again, see AllenNLP guide for details or use `-h` flag for hints.

### Train

```
allennlp train parser/configs/tiny.jsonnet \
    --serialization-dir serialization_dir \
    --include-package parser
```

### Predict

```
allennlp predict serialization_dir/model.tar.gz train.conllu \
    --output-file predictions.txt \
    --include-package parser \
    --predictor morpho_syntax_semantic_predictor \
    --use-dataset-reader
```
