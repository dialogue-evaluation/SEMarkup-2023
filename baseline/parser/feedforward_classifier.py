from overrides import override
from typing import Dict, List

import re
import string

import torch
from torch import nn
from torch import Tensor

from allennlp.data.vocabulary import Vocabulary, DEFAULT_OOV_TOKEN
from allennlp.models import Model
from allennlp.nn.activations import Activation
from allennlp.training.metrics import CategoricalAccuracy

from parser.lemmatize_helper import LemmaRule, predict_lemma_from_rule, normalize, DEFAULT_LEMMA_RULE


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
    PUNCTUATION = set(string.punctuation)

    def __init__(self,
                 vocab: Vocabulary,
                 in_dim: int,
                 hid_dim: int,
                 n_classes: int,
                 activation: str,
                 dropout: float,
                 dictionaries: List[Dict[str, str]] = []):

        super().__init__(vocab, in_dim, hid_dim, n_classes, activation, dropout)

        self.dictionary = set()
        for dictionary_info in dictionaries:
            dictionary_path = dictionary_info["path"]
            lemma_match_pattern = dictionary_info["lemma_match_pattern"]
            with open(dictionary_path, 'r') as f:
                txt = f.read()
                lemmas = re.findall(lemma_match_pattern, txt, re.MULTILINE)
                lemmas = set(map(normalize, lemmas))
            self.dictionary |= lemmas

    @override
    def forward(self,
                embeddings: Tensor,
                labels: Tensor = None,
                mask: Tensor = None,
                metadata: Dict = None
                ) -> Dict[str, Tensor]:

        output = super().forward(embeddings, labels, mask)
        logits, preds, loss = output['logits'], output['preds'], output['loss']

        # While at inference, try to avoid malformed lemmas using external dictionary (if provided).
        if not self.training and self.dictionary:
            # Find top most confident lemma rules for each token.
            probs = torch.nn.functional.softmax(logits, dim=-1)
            top_rules = torch.topk(probs, k=LemmaClassifier.TOPK_RULES, dim=-1).indices.cpu().numpy()

            for i in range(len(metadata)):
                tokens = metadata[i]
                tokens_top_rules = top_rules[i]

                for j in range(len(tokens)):
                    token = str(tokens[j])
                    token_top_rules = tokens_top_rules[j]

                    # Lemmatizer usually does well with titles (e.g. 'Вася')
                    # and different kind of dates (like '70-е')
                    # so don't correct the predictions in that case.
                    is_punctuation = lambda word: word in LemmaClassifier.PUNCTUATION
                    is_title = lambda word: word[0].isupper()
                    contains_digit = lambda word: any(char.isdigit() for char in word)
                    if is_punctuation(token) or is_title(token) or contains_digit(token):
                        continue

                    # Find the most probable correct lemma for the word.
                    better_lemma_found = False
                    for lemma_rule_id in token_top_rules:
                        lemma_rule_str = self.vocab.get_token_from_index(lemma_rule_id, "lemma_rule_labels")

                        # If the current most confident lemma rule is "unknown rule",
                        # then lemmatizer has no idea how to lemmatize the token, so interrupt lookup.
                        if lemma_rule_str == DEFAULT_OOV_TOKEN:
                            continue

                        lemma_rule = LemmaRule.from_str(lemma_rule_str)
                        lemma = predict_lemma_from_rule(token, lemma_rule)
                        if normalize(lemma) in self.dictionary:
                            better_lemma_found = True
                            break

                    # Update predictions with the better lemma.
                    if better_lemma_found:
                        preds[i][j] = lemma_rule_id

        return {'preds': preds, 'loss': loss}

