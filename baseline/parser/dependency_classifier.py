from overrides import override
from copy import deepcopy

from typing import Dict, Tuple

import numpy as np

import torch
from torch import nn
from torch import Tensor
import torch.nn.functional as F

from allennlp.data import Vocabulary
from allennlp.models import Model
from allennlp.nn.activations import Activation
from allennlp.modules.matrix_attention.bilinear_matrix_attention import BilinearMatrixAttention
from allennlp.training.metrics import AttachmentScores
from allennlp.nn.chu_liu_edmonds import decode_mst
from allennlp.nn.util import replace_masked_values, get_range_vector, get_device_of, move_to_device


@Model.register('dependency_classifier')
class DependencyClassifier(Model):
    """
    Dozat and Manning's biaffine dependency classifier.
    I have not found any open-source implementation that can be used as a part
    of a bigger model. Mostly those are standalone parsers that take text
    as input, but we need dependency classifier to take sentence embeddings as input.
    ...so I implemented it on my own.
    It might be not 100% correct, but it does its job.
    """

    def __init__(self,
                 vocab: Vocabulary,
                 in_dim: int, # = embedding dim
                 hid_dim: int,
                 n_rel_classes: int,
                 activation: str,
                 dropout: float):
        super().__init__(vocab)

        mlp = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(in_dim, hid_dim),
            Activation.by_name(activation)(),
            nn.Dropout(dropout)
        )
        self.arc_dep_mlp = deepcopy(mlp)
        self.arc_head_mlp = deepcopy(mlp)
        self.rel_dep_mlp = deepcopy(mlp)
        self.rel_head_mlp = deepcopy(mlp)

        self.arc_attention = BilinearMatrixAttention(hid_dim, hid_dim, use_input_biases=False, label_dim=1)
        self.rel_attention = BilinearMatrixAttention(hid_dim, hid_dim, use_input_biases=True, label_dim=n_rel_classes)

        self.criterion = nn.CrossEntropyLoss()
        self.metric = AttachmentScores()

    def forward(self,
                embeddings: Tensor, # [batch_size, seq_len, embedding_dim]
                arc_labels: Tensor, # [batch_size, seq_len]
                rel_labels: Tensor, # [batch_size, seq_len]
                mask: Tensor        # [batch_size, seq_len]
                ) -> Dict[str, Tensor]:

        # [batch_size, seq_len, hid_dim]
        h_arc_head = self.arc_head_mlp(embeddings)
        h_arc_dep = self.arc_dep_mlp(embeddings)
        h_rel_head = self.rel_head_mlp(embeddings)
        h_rel_dep = self.rel_dep_mlp(embeddings)

        # [batch_size, seq_len, seq_len]
        s_arc = self.arc_attention(h_arc_head, h_arc_dep)
        # Replace masked values along the 3rd dimension with -inf.
        s_arc = replace_masked_values(s_arc, mask[:, None, :], replace_with=-float("inf"))
        # [batch_size, seq_len, seq_len, num_labels]
        s_rel = self.rel_attention(h_rel_head, h_rel_dep).permute(0, 2, 3, 1)

        predicted_arcs, predicted_rels = self.decode(s_arc, s_rel, mask)

        if arc_labels is not None and rel_labels is not None:
            # Now both predicted_arcs and arc_labels have internal format.
            arc_labels = self._conllu_to_internal_arc_format(arc_labels)

            arc_loss, rel_loss = self.loss(s_arc, s_rel, arc_labels, rel_labels, mask)
            self.metric(predicted_arcs, predicted_rels, arc_labels, rel_labels, mask)
        else:
            arc_loss, rel_loss = torch.tensor(0.), torch.tensor(0.)

        # Now both predicted_arcs and arc_labels have conllu format.
        predicted_arcs = self._internal_to_conllu_arc_format(predicted_arcs)

        return {
            'arc_preds': predicted_arcs,
            'rel_preds': predicted_rels,
            'arc_loss': arc_loss,
            'rel_loss': rel_loss
        }

    def decode(self,
               s_arc: Tensor, # [batch_size, seq_len, seq_len]
               s_rel: Tensor, # [batch_size, seq_len, seq_len, num_labels]
               mask: Tensor   # [batch_size, seq_len]
               ) -> Tuple[Tensor, Tensor]:

        if self.training:
            return self.greedy_decode(s_arc, s_rel)
        else:
            return self.mst_decode(s_arc, s_rel, mask)

    def greedy_decode(self,
                      s_arc: Tensor, # [batch_size, seq_len, seq_len]
                      s_rel: Tensor, # [batch_size, seq_len, seq_len, num_labels]
                      ) -> Tuple[Tensor, Tensor]:

        batch_size, _, _ = s_arc.shape

        # Select the most probable arcs.
        # [batch_size, seq_len]
        predicted_arcs = s_arc.argmax(-1)

        # Select the most probable rels for each arc.
        # [batch_size, seq_len, seq_len]
        predicted_rels = s_rel.argmax(-1)

        # Select rels towards predicted arcs.
        # [batch_size, seq_len]
        predicted_rels = predicted_rels.gather(-1, predicted_arcs[:, :, None]).squeeze(-1)

        return predicted_arcs, predicted_rels

    def mst_decode(self,
                   s_arc: Tensor, # [batch_size, seq_len, seq_len]
                   s_rel: Tensor, # [batch_size, seq_len, seq_len, num_labels]
                   mask: Tensor   # [batch_size, seq_len]
                   ) -> Tuple[Tensor, Tensor]:
        batch_size, seq_len, _ = s_arc.shape

        assert get_device_of(s_arc) == get_device_of(s_rel)
        device = get_device_of(s_arc)
        s_arc = s_arc.cpu()
        s_rel = s_rel.cpu()

        # It is the most tricky logic of dependency classifier.
        # If you want to get into it, first visit
        # https://docs.allennlp.org/main/api/nn/chu_liu_edmonds
        # It is not that detailed, so you better look into the source.

        # First, normalize values, as decode_mst expects values to be non-negative.
        s_arc_probs = nn.functional.softmax(s_arc, dim=-1)

        # Next, recall the hack: we use diagonal to store ROOT relation, so
        #
        # s_arc[i,j] = "Probability that j is the head of i" if i != j else "Probability that i is ROOT".
        #
        # However, allennlp's decode_mst defines 'energy' matrix as follows:
        #
        # energy[i,j] = "Score that i is the head of j",
        #
        # which means we have to transpose s_arc at first, so that:
        #
        # s_arc[i,j] = "Score that i is the head of j" if i != j else "Score that i is ROOT".
        #
        s_arc_probs_inv = s_arc_probs.transpose(1, 2)

        # Also note that decode_mst can't handle loops, as it zeroes diagonal out.
        # So, s_arc now:
        #
        # s_arc[i,j] = "Score that i is the head of j".
        #
        # However, decode_mst can produce a tree where root node
        # has a parent, since it knows nothing about root yet.
        # That is, we have to chose the latter explicitly.
        # [batch_size]
        root_idxs = s_arc_probs_inv.diagonal(dim1=1, dim2=2).argmax(dim=-1)

        predicted_arcs = []
        for batch_idx, root_idx in enumerate(root_idxs):
            # Now zero s_arc[i, root_idx] = "Probability that i is the head of root_idx" out.
            energy = s_arc_probs_inv[batch_idx]
            energy[:, root_idx] = 0.0
            # Finally, we are ready to call decode_mst,
            # Note s_arc don't know anything about labels, so we set has_labels=False.
            lengths = mask[batch_idx].sum()
            heads, _ = decode_mst(energy, lengths, has_labels=False)

            # Some vertices may be isolated. Pick heads greedily in this case.
            heads[heads <= 0] = s_arc[batch_idx].argmax(-1)[heads <= 0]
            predicted_arcs.append(heads)

        # [batch_size, seq_len]
        predicted_arcs = torch.from_numpy(np.stack(predicted_arcs)).to(torch.int64)

        # ...and predict relations.
        predicted_rels = s_rel.argmax(-1)
        # Select rels towards predicted arcs.
        # [batch_size, seq_len]
        predicted_rels = predicted_rels.gather(-1, predicted_arcs[:, :, None]).squeeze(-1)

        predicted_arcs = move_to_device(predicted_arcs, device)
        predicted_rels = move_to_device(predicted_rels, device)

        return predicted_arcs, predicted_rels

    def loss(self,
             s_arc: Tensor,       # [batch_size, seq_len, seq_len]
             s_rel: Tensor,       # [batch_size, seq_len, seq_len, num_labels]
             target_arcs: Tensor, # [batch_size, seq_len]
             target_rels: Tensor, # [batch_size, seq_len]
             mask: Tensor         # [batch_size, seq_len]
             ) -> Tuple[Tensor, Tensor]:

        # [mask.sum(), seq_len]
        s_arc = s_arc[mask]
        # [mask.sum()]
        target_arcs = target_arcs[mask]

        # [mask.sum(), seq_len, num_labels]
        s_rel = s_rel[mask]
        # Select the predicted logits towards the correct heads.
        # [mask.sum(), num_labels]
        s_rel = s_rel[torch.arange(len(target_arcs)), target_arcs]
        # [mask.sum()]
        target_rels = target_rels[mask]

        arc_loss = self.criterion(s_arc, target_arcs)
        rel_loss = self.criterion(s_rel, target_rels)

        return arc_loss, rel_loss

    @override
    def get_metrics(self, reset: bool = False) -> Dict[str, float]:
        return self.metric.get_metric(reset)

    ### Private methods ###

    @staticmethod
    def _conllu_to_internal_arc_format(arcs: Tensor) -> Tensor:
        """
        Converts CoNLL-U head labels to internal head labels.
        """
        # Copy tensor, otherwise input arc_labels will be modified.
        arcs = arcs.detach()
        DependencyClassifier._replace_root_id_with_self_id(arcs)
        # At this point, all head labels are greater than zero
        # (since CoNLL-U implies that 'id' tag is greater than zero).
        # However, it's more convenient to have [0, seq_len-1] range rather than [1, seq_len].
        arcs -= 1
        return arcs

    @staticmethod
    def _replace_root_id_with_self_id(arcs: Tensor) -> None:
        """
        Hack: Replace zero head (=ROOT label) with self index for each sentence in a batch.
        NB: Inplace operation.
        """
        roots_indexes = (arcs == 0).nonzero()
        arcs[roots_indexes[:, 0], roots_indexes[:, 1]] = roots_indexes[:, 1] + 1
        return arcs

    @staticmethod
    def _internal_to_conllu_arc_format(arcs: Tensor) -> Tensor:
        """
        Inverse function for _conllu_to_internal_arc_format.
        Converts internal head labels to CoNLL-U head labels.
        """
        arcs += 1
        DependencyClassifier._replace_self_id_with_root_id(arcs)
        return arcs

    @staticmethod
    def _replace_self_id_with_root_id(arcs: Tensor) -> None:
        """
        Inverse function for _replace_root_id_with_self_id.
        """
        batch_size, seq_len = arcs.shape
        id_range = get_range_vector(seq_len, get_device_of(arcs)) + 1
        is_root_mask = (arcs == id_range.expand(batch_size, -1))
        arcs = arcs.masked_fill_(is_root_mask, 0)
        return arcs

