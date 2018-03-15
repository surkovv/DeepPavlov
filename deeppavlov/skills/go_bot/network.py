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
import json
import numpy as np
import tensorflow as tf
from tensorflow.contrib.layers import xavier_initializer

from deeppavlov.core.common.registry import register
from deeppavlov.core.models.tf_model import TFModel
from deeppavlov.core.common.log import get_logger


log = get_logger(__name__)


@register('go_bot_rnn')
class GoalOrientedBotNetwork(TFModel):
    GRAPH_PARAMS = ["hidden_size", "action_size", "dense_size", "obs_size"]
    def __init__(self, **params):
        # initialize parameters
        self._init_params(params)
        # build computational graph
        self._build_graph()
        # initialize session
        self.sess = tf.Session()

        self.sess.run(tf.global_variables_initializer())

        super().__init__(**params)
        if tf.train.checkpoint_exists(str(self.save_path.resolve())):
        #TODO: save/load params to json, here check compatability
            log.info("[initializing `{}` from saved]".format(self.__class__.__name__))
            self.load()
        else:
            log.info("[initializing `{}` from scratch]".format(self.__class__.__name__))

        self.reset_state()

    def __call__(self, features, action_mask, prob=False):
        # TODO: make input list
        probs, prediction, state = \
            self.sess.run(
                [self._probs, self._prediction, self._state],
                feed_dict={
                    self._dropout: 1.,
                    self._features: [[features]],
                    self._initial_state: (self.state_c, self.state_h),
                    self._action_mask: [[action_mask]]
                }
            )
        self.state_c, self._state_h = state
        if prob:
            return probs
        return prediction

    def train_on_batch(self, x: list, y: list):
        features, action_mask = x
        action = y
        self._train_step(features, action, action_mask)

    def _init_params(self, params):
        self.opt = params
        self.opt['dropout_rate'] = params.get('dropout_rate', 1.)
        self.opt['dense_size'] = params.get('dense_size', self.opt['hidden_size'])

        self.learning_rate = self.opt['learning_rate']
        self.dropout_rate = self.opt['dropout_rate']
        self.hidden_size = self.opt['hidden_size']
        self.action_size = self.opt['action_size']
        self.obs_size = self.opt['obs_size']
        self.dense_size = self.opt['dense_size']

    def _build_graph(self):

        self._add_placeholders()

        # build body
        _logits, self._state = self._build_body()

        # probabilities normalization : elemwise multiply with action mask
        self._probs = tf.multiply(tf.squeeze(tf.nn.softmax(_logits)),
                                  self._action_mask,
                                  name='probs')

        # loss, train and predict operations
        self._prediction = tf.argmax(self._probs, axis=-1, name='prediction')
        _loss_tensor = \
            tf.losses.sparse_softmax_cross_entropy(logits=_logits,
                                                   labels=self._action)
        self._loss = tf.reduce_mean(_loss_tensor, name='loss')
        self._train_op = self.get_train_op(self._loss, self.learning_rate, clip_norm=2.)

    def _add_placeholders(self):
        # TODO: make batch_size != 1
        self._dropout = tf.placeholder_with_default(1.0, shape=[])
        _initial_state_c = \
            tf.placeholder_with_default(np.zeros([1, self.hidden_size], np.float32),
                                        shape=[1, self.hidden_size])
        _initial_state_h = \
            tf.placeholder_with_default(np.zeros([1, self.hidden_size], np.float32),
                                        shape=[1, self.hidden_size])
        self._initial_state = tf.nn.rnn_cell.LSTMStateTuple(_initial_state_c,
                                                            _initial_state_h)
        self._features = tf.placeholder(tf.float32, [1, None, self.obs_size],
                                        name='features')
        self._action = tf.placeholder(tf.int32, [1, None],
                                      name='ground_truth_action')
        self._action_mask = tf.placeholder(tf.float32, [None, None, self.action_size],
                                           name='action_mask')

    def _build_body(self):
        # input projection
        _units = tf.nn.dropout(self._features, self._dropout)
        _units = tf.layers.dense(_units,
                                 self.dense_size,
                                 kernel_initializer=xavier_initializer())

        # recurrent network unit
        _lstm_cell = tf.nn.rnn_cell.LSTMCell(self.hidden_size)
        _output, _state = tf.nn.dynamic_rnn(_lstm_cell,
                                            _units,
                                            initial_state=self._initial_state)
 
        # output projection
        # TODO: try multiplying logits to action_mask
        _logits = tf.layers.dense(_output,
                                  self.action_size,
                                  kernel_initializer=xavier_initializer())
        return _logits, _state

    def load(self, *args, **kwargs):
        super().load(*args, **kwargs)
        self.load_params()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.save_params()

    def save_params(self):
        path = str(self.save_path.with_suffix('.json').resolve())
        log.info('[saving parameters to {}]'.format(path))
        with open(path, 'w') as fp:
            json.dump(self.opt, fp)

    def load_params(self):
        path = str(self.load_path.with_suffix('.json').resolve())
        log.info('[loading parameters from {}]'.format(path))
        with open(path, 'r') as fp:
            params = json.load(fp)
        for p in self.GRAPH_PARAMS:
            if self.opt[p] != params[p]:
                raise ValueError("`{}` parameter must be equal to "
                                 "saved model parameter value `{}`"\
                                 .format(p, params[p]))

    def reset_state(self):
        # set zero state
        self.state_c = np.zeros([1, self.hidden_size], dtype=np.float32)
        self.state_h = np.zeros([1, self.hidden_size], dtype=np.float32)

    def _train_step(self, features, action, action_mask):
        _, loss_value, prediction = \
            self.sess.run(
                [ self._train_op, self._loss, self._prediction ],
                feed_dict={
                    self._dropout: self.dropout_rate,
                    self._features: [features],
                    self._initial_state: (self.state_c, self.state_h),
                    self._action: [action],
                    self._action_mask: [action_mask]
                }
            )
        return loss_value, prediction

    def shutdown(self):
        self.sess.close()
