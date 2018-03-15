"""
Copyright 2017 Neural Networks and Deep Learning lab, MIPT

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re

import numpy as np
from typing import Type

from deeppavlov.core.commands.utils import expand_path
from deeppavlov.core.common.registry import register
from deeppavlov.core.models.component import Component
from deeppavlov.core.models.nn_model import NNModel
from deeppavlov.core.common.errors import ConfigError
from deeppavlov.models.embedders.fasttext_embedder import FasttextEmbedder
from deeppavlov.models.encoders.bow import BoWEncoder
from deeppavlov.models.classifiers.intents.intent_model import KerasIntentModel
from deeppavlov.models.ner.slotfill import DstcSlotFillingNetwork
from deeppavlov.models.tokenizers.spacy_tokenizer import SpacyTokenizer
from deeppavlov.models.trackers.default_tracker import DefaultTracker
from deeppavlov.skills.go_bot.network import GoalOrientedBotNetwork
from deeppavlov.skills.go_bot.templates import Templates, DualTemplate
from deeppavlov.core.common.attributes import check_attr_true
from deeppavlov.core.common.log import get_logger


log = get_logger(__name__)


@register("go_bot")
class GoalOrientedBot(NNModel):
    def __init__(self, template_path,
                 template_type: Type = DualTemplate,
                 bow_encoder: Type = BoWEncoder,
                 tokenizer: Type = SpacyTokenizer,
                 tracker: Type = DefaultTracker,
                 network: Type = GoalOrientedBotNetwork,
                 embedder=None,
                 slot_filler=None,
                 intent_classifier=None,
                 use_action_mask=False,
                 debug=False,
                 save_path=None,
                 word_vocab=None,
                 vocabs=None,
                 **kwargs):

        super().__init__(save_path=save_path, mode=kwargs['mode'])

        self.episode_done = True
        self.use_action_mask = use_action_mask
        self.debug = debug
        self.slot_filler = slot_filler
        self.intent_classifier = intent_classifier
        self.bow_encoder = bow_encoder
        self.embedder = embedder
        self.tokenizer = tokenizer
        self.tracker = tracker
        self.network = network
        self.word_vocab = word_vocab or vocabs['word_vocab']

        template_path = expand_path(template_path)
        log.info("[loading templates from {}]".format(template_path))
        self.templates = Templates(template_type).load(template_path)
        log.info("{} templates loaded".format(len(self.templates)))

        # intialize parameters
        self.db_result = None
        self.n_actions = len(self.templates)
        self.n_intents = 0
        if hasattr(self.intent_classifier, 'n_classes'):
            self.n_intents = self.intent_classifier.n_classes
        self.prev_action = np.zeros(self.n_actions, dtype=np.float32)

        # opt = {
        #    'action_size': self.n_actions,
        #    'obs_size': 4 + len(self.word_vocab) + self.embedder.dim +\
        #    self.tracker.num_features + self.n_actions + self.n_intents
        # }
        # self.network = GoalOrientedBotNetwork(opt)

    def _encode_context(self, context, db_result=None):
        # tokenize input
        tokenized = ' '.join(self.tokenizer([context])[0]).lower().strip()
        if self.debug:
            log.debug("Text tokens = `{}`".format(tokenized))

        # Bag of words features
        bow_features = self.bow_encoder([tokenized], self.word_vocab)[0]
        bow_features = bow_features.astype(np.float32)

        # Embeddings
        emb_features = []
        if callable(self.embedder):
            emb_features = self.embedder([tokenized], mean=True)[0]

        # Intent features
        intent_features = []
        if callable(self.intent_classifier):
            intent_features = self.intent_classifier([tokenized], predict_proba=True).ravel()
            if self.debug:
                log.debug("Predicted intent = `{}`"\
                          .format(self.intent_classifier([tokenized])))

        # Text entity features
        if callable(self.slot_filler):
            self.tracker.update_state(self.slot_filler([tokenized])[0])
            if self.debug:
                log.debug("Slot vals: {}".format(str(self.slot_filler(tokenized))))

        state_features = self.tracker()

        # Other features
        context_features = np.array([(db_result == {}) * 1.,
                                     (self.db_result == {}) * 1.],
                                    dtype=np.float32)

        if self.debug:
            debug_msg = "num bow features = {}, " \
                        "num emb features = {}, " \
                        "num intent features = {}, " \
                        "num state features = {}, " \
                        "num context features = {}, " \
                        "prev_action shape = {}".format(len(bow_features),
                                                        len(emb_features),
                                                        len(intent_features),
                                                        len(state_features),
                                                        len(context_features),
                                                        len(self.prev_action))

            log.debug(debug_msg)

        return np.hstack((bow_features, emb_features, intent_features,
                          state_features, context_features, self.prev_action))

    def _encode_response(self, act):
        return self.templates.actions.index(act)

    def _decode_response(self, action_id):
        """
        Convert action template id and entities from tracker
        to final response.
        """
        template = self.templates.templates[int(action_id)]

        slots = self.tracker.get_state()
        if self.db_result is not None:
            for k, v in self.db_result.items():
                slots[k] = str(v)

        return template.generate_text(slots)

    def _action_mask(self):
        action_mask = np.ones(self.n_actions, dtype=np.float32)
        if self.use_action_mask:
            known_entities = {**self.tracker.get_state(), **(self.db_result or {})}
            for a_id in range(self.n_actions):
                tmpl = str(self.templates.templates[a_id])
                for entity in set(re.findall('#([A-Za-z]+)', tmpl)):
                    if entity not in known_entities:
                        action_mask[a_id] = 0
        return action_mask

    def train_on_batch(self, x, y):
        for contexts, responses in zip(x, y):
            self.reset()
            d_features, d_actions, d_masks = [], [], []
            for context, response in zip(contexts, responses):
                features = self._encode_context(context['text'],
                                                context.get('db_result'))
                if context.get('db_result') is not None:
                    self.db_result = context['db_result']
                d_features.append(features)

                action_id = self._encode_response(response['act'])
                # previous action is teacher-forced here
                self.prev_action *= 0.
                self.prev_action[action_id] = 1.
                d_actions.append(action_id)

                d_masks.append(self._action_mask())

            # self.network.train(d_features, d_actions, d_masks)
            self.network.train_on_batch([d_features, d_masks], d_actions)

    def _infer(self, context, db_result=None, prob=False):
        # TODO: check if prob=True works better
        probs = self.network(
            self._encode_context(context, db_result),
            self._action_mask(),
            prob=True
        )
        pred_id = np.argmax(probs)
        if db_result is not None:
            self.db_result = db_result

        # one-hot encoding seems to work better then probabilities
        if prob:
            self.prev_action = probs
        else:
            self.prev_action *= 0
            self.prev_action[pred_id] = 1

        return self._decode_response(pred_id)

    def _infer_dialog(self, contexts):
        self.reset()
        res = []
        for context in contexts:
            if context.get('prev_resp_act') is not None:
                action_id = self._encode_response(context.get('prev_resp_act'))
                # previous action is teacher-forced
                self.prev_action *= 0.
                self.prev_action[action_id] = 1.

            res.append(self._infer(context['text'], context.get('db_result')))
        return res

    def __call__(self, batch):
        if isinstance(batch[0], str):
            return [self._infer(x) for x in batch]
        return [self._infer_dialog(x) for x in batch]

    def reset(self):
        self.tracker.reset_state()
        self.db_result = None
        self.prev_action = np.zeros(self.n_actions, dtype=np.float32)
        self.network.reset_state()

    def save(self):
        """Save the parameters of the model to a file."""
        self.network.save()

    def shutdown(self):
        self.network.shutdown()
        self.slot_filler.shutdown()

    def load(self):
        pass
