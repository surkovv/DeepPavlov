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
import tensorflow as tf
from overrides import overrides
from copy import deepcopy
import inspect

from deeppavlov.core.common.attributes import check_attr_true
from deeppavlov.core.common.registry import register
from deeppavlov.core.data.utils import tokenize_reg
from deeppavlov.models.ner.network import NerNetwork
from deeppavlov.core.models.tf_model import TFModel


@register('ner')
class NER(TFModel):
    def __init__(self, **kwargs):
        self.opt = deepcopy(kwargs)
        vocabs = self.opt.pop('vocabs')
        self.opt.update(vocabs)

        # Find all input parameters of the network init
        network_parameter_names = list(inspect.signature(NerNetwork.__init__).parameters)
        # Fill all provided parameters from opt
        network_parameters = {par: self.opt[par] for par in network_parameter_names if par in self.opt}

        self.sess = tf.Session()
        network_parameters['sess'] = self.sess
        self._net = NerNetwork(**network_parameters)

        # Find all parameters for network train
        train_parameters_names = list(inspect.signature(NerNetwork.train_on_batch).parameters)
        # Fill all provided parameters from opt
        train_parameters = {par: self.opt[par] for par in train_parameters_names if par in self.opt}
        self.train_parameters = train_parameters

        # Try to load the model (if there are some model files the model will be loaded from them)
        super().__init__(**kwargs)
        if self.load_path is not None:
            self.load()

    def train_on_batch(self, batch_x, batch_y):
        self._net.train_on_batch(batch_x, batch_y, **self.train_parameters)

    @overrides
    def __call__(self, batch, *args, **kwargs):
        if isinstance(batch[0], str):
            batch = [tokenize_reg(utterance) for utterance in batch]
        return self._net.predict_on_batch(batch)

    def shutdown(self):
        self._net.shutdown()
