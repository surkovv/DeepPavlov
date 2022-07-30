from deeppavlov.core.common.registry import register
from deeppavlov.core.models.component import Component
from typing import List

@register("triplets_preprocessor")
class TripletsPreprocessor(Component):

    def __init__(self, **kwargs):
        pass

    def __call__(self, triplets: List[List[List[str]]], true_texts: List['str'] = None,  *args, **kwargs):

        """ Generate jointGT-like triplet sets
        Args:
            triplets: batch of triplet sets
        Returns:
            jointGT-like triplet sets
        """

        result = []
        for tset_id, triplet_set in enumerate(triplets):
            new_set = {}
            new_set['id'] = tset_id
            kbs = {}
            for triplet_id, triplet in enumerate(triplet_set):
                entity_id = "E" + str(triplet_id)
                from_ent, relation, to_ent = triplet
                kbs[entity_id] = [
                    to_ent,
                    to_ent,
                    [
                        [
                            relation,
                            from_ent
                        ]
                    ]
                ]
            new_set['kbs'] = kbs

            if true_texts is None:
                new_set['text'] = "dummy text."
            else:
                new_set['text'] = true_texts[tset_id]

            result.append(new_set)

        return result
