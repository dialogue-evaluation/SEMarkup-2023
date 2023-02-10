from overrides import override

from typing import Dict

import torch
from torch import nn
from torch import Tensor

from allennlp.data import Vocabulary
from allennlp.models import Model
from allennlp.nn.activations import Activation
from allennlp.training.metrics import CategoricalAccuracy


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
    def forward(self, embeddings: Tensor, labels: Tensor = None, mask: Tensor = None) -> Dict[str, Tensor]:
        logits = self.classifier(embeddings)
        preds = logits.argmax(-1)

        loss = torch.tensor(0.)
        if labels is not None:
            loss = self.loss(logits, labels, mask)
            self.metric(logits, labels, mask)

        return {'preds': preds, 'loss': loss}

    def loss(self, logits: Tensor, target: Tensor, mask: Tensor) -> Tensor:
        return self.criterion(logits[mask], target[mask])

    @override
    def get_metrics(self, reset: bool = False) -> Dict[str, float]:
        return {"Accuracy": self.metric.get_metric(reset)}

