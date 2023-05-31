from conllu.models import Token, TokenList

from overrides import override
from typing import Dict

from allennlp.predictors.predictor import Predictor
from allennlp.common.util import JsonDict
from allennlp.data import Instance


@Predictor.register("morpho_syntax_semantic_predictor")
class MorphoSyntaxSemanticPredictor(Predictor):
    """
    See https://guide.allennlp.org/training-and-prediction#4 for guidance.
    """

    @override(check_signature=False)
    def dump_line(self, output: Dict[str, list]) -> str:
        metadata = output["metadata"]

        tags_iterator = zip(
            output["ids"],
            output["forms"],
            output["lemmas"],
            output["pos"],
            output["feats"],
            output["heads"],
            output["deprels"],
            output["semslots"],
            output["semclasses"],
        )

        tokens = []
        for tok_id, form, lemma, pos, feats, head, deprel, semslot, semclass in tags_iterator:
            token = Token()
            token["id"] = tok_id
            token["form"] = form
            token["lemma"] = lemma
            token["upos"] = pos
            token["xpos"] = '_'
            token["feats"] = feats
            token["head"] = head
            token["deprel"] = deprel
            token["semslot"] = semslot
            token["semclass"] = semclass
            tokens.append(token)

        sentence = TokenList(tokens, metadata)
        serialized_sentence = sentence.serialize()
        return serialized_sentence

