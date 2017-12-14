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

import numpy as np

import tensorflow as tf
from tensorflow.contrib.layers import xavier_initializer

from deeppavlov.common.registry import register_model
from deeppavlov.models.tf_model import TFModel


@register_model('hcn-rnn')
class HybridCodeNetworkModel(TFModel):

    def __init__(self, **params):
        self.opt = params
        self._model_dir_path = params['model_dir_path']
        self._model_fpath = params['model_fpath']

        # initialize parameters
        self._init_params()
        # build computational graph
        self._build_graph()
        # initialize session
        self.sess = tf.Session()
        # reload graph weights if `pretrained_model` present
        if self.opt.get('pretrained_model') is not None:
#TODO: save/load params to json, here check compatability
#
            self.load(self.opt['pretrained_model'])
        else:
            self.sess.run(tf.global_variables_initializer())
        self.reset_state()

    def _run_sess(self):
        pass

    def _init_params(self, params=None):
        params = params or self.opt
        self.learning_rate = params['learning_rate']
        self.n_epoch = params['epoch_num']
        self.n_hidden = params['hidden_dim']
        self.n_actions = params['action_size']
        self.obs_size = params['obs_size']

    def _build_graph(self):
        tf.reset_default_graph()

        self._add_placeholders()

        # build body
        _logits = self._build_body()

        # loss, train and predict operations
        self._prediction = tf.argmax(self._probs, axis=0, name='prediction')
        self._loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
            logits=_logits, labels=self._action, name='loss'
        )
        self._step = tf.Variable(0, trainable=False, name='global_step')
        self._train_op = tf.train.AdadeltaOptimizer(self.learning_rate)\
            .minimize(self._loss, global_step=self._step, name='train_op')

    def _add_placeholders(self):
        self._features = tf.placeholder(tf.float32, [1, self.obs_size],
                                        name='features')
        self._state_c = tf.placeholder(tf.float32, [1, self.n_hidden],
                                       name='state_c')
        self._state_h = tf.placeholder(tf.float32, [1, self.n_hidden],
                                       name='state_h')
        self._action = tf.placeholder(tf.int32,
                                      name='ground_truth_action')
        self._action_mask = tf.placeholder(tf.float32, [self.n_actions],
                                           name='action_mask')

    def _build_body(self):
        # input projection
        _Wi = tf.get_variable('Wi', [self.obs_size, self.n_hidden],
                              initializer=xavier_initializer())
        _bi = tf.get_variable('bi', [self.n_hidden],
                              initializer=tf.constant_initializer(0.))

        # add relu/tanh here if necessary
        _projected_features = tf.matmul(self._features, _Wi) + _bi

        _lstm_f = tf.contrib.rnn.LSTMCell(self.n_hidden, state_is_tuple=True)
        _lstm_op, self._next_state = _lstm_f(inputs=_projected_features,
                                             state=(self._state_c,
                                                    self._state_h))

        # reshape LSTM's state tuple (2,128) -> (1,256)
        _state_reshaped = tf.concat(axis=1,
                                    values=(self._next_state.c,
                                            self._next_state.h))

        # output projection
        _Wo = tf.get_variable('Wo', [self.n_hidden, self.n_actions],
                              initializer=xavier_initializer())
        _bo = tf.get_variable('bo', [self.n_actions],
                              initializer=tf.constant_initializer(0.))
        # get logits
        _logits = tf.matmul(_state_reshaped, _Wo) + _bo
        # probabilities normalization : elemwise multiply with action mask
        self._probs = tf.multiply(tf.squeeze(tf.nn.softmax(_logits)),
                                  self._action_mask,
                                  name='probs')
        return _logits

    def reset_state(self):
        # set zero state
        self.state_c = np.zeros([1, self.n_hidden], dtype=np.float32)
        self.state_h = np.zeros([1, self.n_hidden], dtype=np.float32)

    def _train_step(self, features, action, action_mask):
        _, loss_value, self.state_c, self.state_h, prediction = \
            self.sess.run(
                [
                    self._train_op, self._loss, self._next_state.c,
                    self._next_state.h, self._prediction
                ],
                feed_dict={
                    self._features: features.reshape([1, self.obs_size]),
                    self._action: [action],
                    self._state_c: self.state_c,
                    self._state_h: self.state_h,
                    self._action_mask: action_mask
                }
            )
        return loss_value[0], prediction

    def _forward(self, features, action_mask):
        probs, prediction, self.state_c, self.state_h = \
            self.sess.run(
                [
                    self._probs, self._prediction, self._next_state.c,
                    self._next_state.h
                ],
                feed_dict={
                    self._features: features.reshape([1, self.obs_size]),
                    self._state_c: self.state_c,
                    self._state_h: self.state_h,
                    self._action_mask: action_mask
                }
            )
        return probs, prediction

    def __exit__(self, type, value, traceback):
        self.sess.close()
