# Parsers

This directory contains SEMarkup parsers implementation.

The models' description is available at [models.md](models.md).

If you are interested in configuration details like batch size, learning rate, scheduler, etc. see [configs](configs/).

## Usage

The models are implemented using [AllenNLP](https://github.com/allenai/allennlp) framework, so if you want to build your own model based on this code, we hightly recommend reading [AllenNLP guide](https://guide.allennlp.org/) first.

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
