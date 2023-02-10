import sys
import numpy as np

from tqdm import tqdm

# zip `strict` is only available starting Python 3.10.
from more_itertools import zip_equal

from typing import Iterable, List, Tuple, Dict, Optional

from scorer.taxonomy import Taxonomy
from semarkup import Sentence, SemarkupToken


class SEMarkupScorer:
    def __init__(self,
                 taxonomy_file: str,
                 semclasses_out_of_taxonomy: set,
                 lemma_weights: Dict[str, float] = None,
                 feats_weights: Dict[str, float] = None):
        self.taxonomy = Taxonomy(taxonomy_file)
        self.semclasses_out_of_taxonomy = set(semclasses_out_of_taxonomy)
        self.lemma_weights = lemma_weights
        self.feats_weights = feats_weights

    def score_lemma(self, test: SemarkupToken, gold: SemarkupToken) -> float:
        ignore_case_and_yo = lambda word: word.lower().replace('ё', 'е')
        score = ignore_case_and_yo(test.lemma) == ignore_case_and_yo(gold.lemma)

        if self.lemma_weights is not None:
            score *= self.lemma_weights[gold.pos]
        assert 0. <= score <= 1.
        return score

    def score_pos(self, test: SemarkupToken, gold: SemarkupToken) -> float:
        score = test.pos == gold.pos
        assert 0. <= score <= 1.
        return score

    def score_feats(self, test: SemarkupToken, gold: SemarkupToken) -> float:
        correct_feats_weighted_sum = np.sum([
            (self.feats_weights[gram_cat] if self.feats_weights is not None else 1)
            * (gold.feats[gram_cat] == test.feats[gram_cat])
            for gram_cat in gold.feats
            if gram_cat in test.feats
        ])
        gold_feats_weighted_sum = np.sum([
            (self.feats_weights[gram_cat] if self.feats_weights is not None else 1)
            for gram_cat in gold.feats
        ])
        assert correct_feats_weighted_sum <= gold_feats_weighted_sum

        # Penalize test if it is longer than gold.
        # If there were no such penalty, one could simply predict all grammatical categories
        # existing for each token and score would not get any worse.
        # It's not what we expect from a good morphology classifier, so use penalty.
        penalty = 1 / (1 + max(len(test.feats) - len(gold.feats), 0))

        if len(gold.feats) == 0:
            # Gold is empty.
            if len(test.feats) == 0:
                # Test is also empty.
                score = 1.
            else:
                # Test not empty
                score = 0.
        else:
            assert gold_feats_weighted_sum != 0
            score = penalty * correct_feats_weighted_sum / gold_feats_weighted_sum

        assert 0. <= score <= 1.
        return score

    def score_head(self, test: SemarkupToken, gold: SemarkupToken) -> float:
        score = test.head == gold.head
        assert 0. <= score <= 1.
        return score

    def score_deprel(self, test: SemarkupToken, gold: SemarkupToken) -> float:
        score = (test.head == gold.head) and (test.deprel == gold.deprel)
        assert 0. <= score <= 1.
        return score

    def score_semslot(self, test: SemarkupToken, gold: SemarkupToken) -> float:
        score = test.semslot == gold.semslot
        assert 0. <= score <= 1.
        return score

    def score_semclass(self, test: SemarkupToken, gold: SemarkupToken) -> float:
        # Handle extra cases.
        if gold.semclass in self.semclasses_out_of_taxonomy:
            return test.semclass == gold.semclass

        assert self.taxonomy.has_semclass(gold.semclass), \
            f"Unknown gold semclass encountered: {gold.semclass}"
        if not self.taxonomy.has_semclass(test.semclass):
            return 0.

        semclasses_distance = self.taxonomy.calc_path_length(test.semclass, gold.semclass)

        # If distance is 0 then test_semclass == gold_semclass, so score is 1.
        # If they are different, the penalty is proportional to their distance.
        # If they are in different trees, then distance is inf, so score is 0.
        score = 1 / (1 + semclasses_distance)
        assert 0. <= score <= 1.
        return score

    def score_sentences(self,
                        test_sentences: Iterable[Sentence],
                        gold_sentences: Iterable[Sentence]) -> Tuple[float]:
        # Grammatical scores.
        # Use 'list' and 'np.sum' instead of 'int' and '+=' for numerical stability.
        lemma_scores = []
        pos_scores = []
        feats_scores = []
        # Syntax scores (UAS and LAS, in fact).
        head_scores = []
        deprel_scores = []
        # Semantic scores.
        semslot_scores = []
        semclass_scores = []

        # 'lemma' scores are weighted.
        # Why? The idea here is quite natural:
        # We want immutable parts of speech (which are relatively easy to lemmatize) to affect
        # lemmatization score less than mutable ones (which are, obviously, harder to lemmatize).
        #
        # As a result, lemmatization per-token scores can be greater than 1.0
        # (for example, lemma_scores[10] can be equal to 10).
        #
        # However, we expect average dataset scores to be in [0.0..1.0] range,
        # so we also accumulate gold per-token scores and use them for
        # final normalization. This way we get 1.0 score if all test and gold lemmas are equal,
        # and a lower score otherwise.
        lemma_gold_scores = []

        for test_sentence, gold_sentence in tqdm(zip_equal(test_sentences, gold_sentences), file=sys.stdout):
            assert test_sentence.sent_id == gold_sentence.sent_id, \
                f"Test and gold sentence id mismatch at test_sentence.sent_id={test_sentence.sent_id}."

            assert len(test_sentence) == len(gold_sentence), \
                f"Error at sent_id={test_sentence.sent_id} : Sentences must have equal number of tokens."

            for test_token, gold_token in zip_equal(test_sentence, gold_sentence):

                assert test_token.form == gold_token.form, \
                    f"Error at sent_id={test_sentence.sent_id} : Sentence tokens mismatched."

                # Score test_token.
                lemma_score = self.score_lemma(test_token, gold_token)
                pos_score = self.score_pos(test_token, gold_token)
                feats_score = self.score_feats(test_token, gold_token)
                head_score = self.score_head(test_token, gold_token)
                deprel_score = self.score_deprel(test_token, gold_token)
                semslot_score = self.score_semslot(test_token, gold_token)
                semclass_score = self.score_semclass(test_token, gold_token)

                # Accumulcate test scores.
                lemma_scores.append(lemma_score)
                pos_scores.append(pos_score)
                feats_scores.append(feats_score)
                head_scores.append(head_score)
                deprel_scores.append(deprel_score)
                semslot_scores.append(semslot_score)
                semclass_scores.append(semclass_score)

                # Score gold.
                lemma_gold_score = self.score_lemma(gold_token, gold_token)

                # Accumulate gold scores.
                lemma_gold_scores.append(lemma_gold_score)

        # Average per-token scores over all tokens in all sentences.
        # Note that we cannot just average lemma_scores, for they are weighted.
        lemma_avg_score = np.sum(lemma_scores) / np.sum(lemma_gold_scores)
        pos_avg_score = np.mean(pos_scores)
        feats_avg_score = np.mean(feats_scores)
        head_avg_score = np.mean(head_scores)
        deprel_avg_score = np.mean(deprel_scores)
        semslot_avg_score = np.mean(semslot_scores)
        semclass_avg_score = np.mean(semclass_scores)

        assert 0. <= lemma_avg_score <= 1.
        assert 0. <= pos_avg_score <= 1.
        assert 0. <= feats_avg_score <= 1.
        assert 0. <= head_avg_score <= 1.
        assert 0. <= deprel_avg_score <= 1.
        assert 0. <= semslot_avg_score <= 1.
        assert 0. <= semclass_avg_score <= 1.

        return (
            lemma_avg_score,
            pos_avg_score,
            feats_avg_score,
            head_avg_score,
            deprel_avg_score,
            semslot_avg_score,
            semclass_avg_score
        )


# TODO: Unit Tests

