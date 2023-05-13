from overrides import override
from typing import Dict

import re

import torch
from torch import nn
from torch import Tensor

from allennlp.data import Vocabulary
from allennlp.models import Model
from allennlp.nn.activations import Activation
from allennlp.training.metrics import CategoricalAccuracy

from parser.lemmatize_helper import LemmaRule, predict_lemma_from_rule, DEFAULT_LEMMA_RULE


@Model.register('feed_forward_classifier')
class FeedForwardClassifier(Model):
    """
    A simple classifier composed of two feed-forward layers separated by a nonlinear activation.
    """
    def __init__(self,
                 vocab: Vocabulary,
                 in_dim: int,
                 hid_dim: int,
                 n_classes: int,
                 activation: str,
                 dropout: float):
        super().__init__(vocab)

        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(in_dim, hid_dim),
            Activation.by_name(activation)(),
            nn.Dropout(dropout),
            nn.Linear(hid_dim, n_classes)
        )
        self.criterion = nn.CrossEntropyLoss()
        self.metric = CategoricalAccuracy()

    @override(check_signature=False)
    def forward(self,
                embeddings: Tensor,
                labels: Tensor = None,
                mask: Tensor = None
                ) -> Dict[str, Tensor]:
        logits = self.classifier(embeddings)
        preds = logits.argmax(-1)

        loss = torch.tensor(0.)
        if labels is not None:
            loss = self.loss(logits, labels, mask)
            self.metric(logits, labels, mask)

        return {'logits': logits, 'preds': preds, 'loss': loss}

    def loss(self, logits: Tensor, target: Tensor, mask: Tensor) -> Tensor:
        return self.criterion(logits[mask], target[mask])

    @override
    def get_metrics(self, reset: bool = False) -> Dict[str, float]:
        return {"Accuracy": self.metric.get_metric(reset)}


@Model.register('lemma_classifier')
class LemmaClassifier(FeedForwardClassifier):
    """
    FeedForwardClassifier specialization for lemma classification.
    """

    TOPK_RULES = 5

    def __init__(self,
                 vocab: Vocabulary,
                 in_dim: int,
                 hid_dim: int,
                 n_classes: int,
                 activation: str,
                 dropout: float,
                 dictionary_path: str):
        super().__init__(vocab, in_dim, hid_dim, n_classes, activation, dropout)

        with open(dictionary_path, 'r') as f:
            filetext = f.read()
            dictionary = re.findall("\d+:(.*)", filetext)
            dictionary = set(dictionary)
        self.dictionary = dictionary
        print(f"dictionary size: {len(self.dictionary)}")

    @override
    def forward(self,
                embeddings: Tensor,
                labels: Tensor = None,
                mask: Tensor = None,
                metadata: Dict = None
                ) -> Dict[str, Tensor]:

        output = super().forward(embeddings, labels, mask)
        logits, preds, loss = output['logits'], output['preds'], output['loss']

        # While at inference, try to avoid malformed lemmas using external dictionary.
        if not self.training:
            # Find top most confident lemma rules for each token.
            top_rules = torch.topk(logits, k=TOPK_RULES, dim=-1).indices

            for i in range(len(metadata)):
                tokens = metadata[i]
                tokens_top_rules = top_rules[i]
                for j in range(len(tokens)):
                    word = words[j]
                    word_top_rules = tokens_top_rules[j]
                    # Find the first correct lemma (i.e. a lemma within the dictionary) for the word.
                    for lemma_rule_id in word_top_rules:
                        lemma_rule_str = self.vocab.get_token_from_index(lemma_rule_id, "lemma_rule_labels")

                        # If the most confident lemma rule is "unknown rule",
                        # then there is no sense in looking for better lemma.
                        if lemma_rule_str == DEFAULT_OOV_TOKEN:
                            break
                        # There are also non-dictionary tokens like digits, punctuation, etc.
                        # In such cases we don't want to look for dictionary lemma.
                        if lemma_rule_str == DEFAULT_LEMMA_RULE:
                            break

                        lemma_rule = LemmaRule.from_str(lemma_rule_str)
                        lemma = predict_lemma_from_rule(word, lemma_rule)
                        if lemma in self.dictionary:
                            break

                    # Update predictions with the better lemma.
                    preds[i][j] = lemma_rule_id

        return {'preds': preds, 'loss': loss}

