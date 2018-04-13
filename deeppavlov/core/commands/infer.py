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
from deeppavlov.core.commands.utils import set_deeppavlov_root
from deeppavlov.core.common.chainer import Chainer
from deeppavlov.core.common.file import read_json
from deeppavlov.core.common.registry import REGISTRY

from deeppavlov.core.agent.agent import Agent
from deeppavlov.core.common.params import from_params
from deeppavlov.core.common.log import get_logger


log = get_logger(__name__)


def build_model_from_config(config, mode='infer', load_trained=False, as_component=False):
    set_deeppavlov_root(config)
    if 'chainer' in config:
        model_config = config['chainer']

        model = Chainer(model_config['in'], model_config['out'], model_config.get('in_y'), as_component=as_component)

        for component_config in model_config['pipe']:
            if load_trained and ('fit_on' in component_config or 'in_y' in component_config):
                try:
                    component_config['load_path'] = component_config['save_path']
                except KeyError:
                    log.warning('No "save_path" parameter for the {} component, so "load_path" will not be renewed'
                                .format(component_config.get('name', component_config.get('ref', 'UNKNOWN'))))
            component = from_params(component_config, vocabs=[], mode=mode)

            if 'in' in component_config:
                c_in = component_config['in']
                c_out = component_config['out']
                in_y = component_config.get('in_y', None)
                main = component_config.get('main', False)
                model.append(c_in, c_out, component, in_y, main)

        return model

    model_config = config['model']
    if load_trained:
        try:
            model_config['load_path'] = model_config['save_path']
        except KeyError:
            log.warning('No "save_path" parameter for the model, so "load_path" will not be renewed')

    vocabs = {}
    if 'vocabs' in config:
        for vocab_param_name, vocab_config in config['vocabs'].items():
            v = from_params(vocab_config, mode=mode)
            vocabs[vocab_param_name] = v
    model = from_params(model_config, vocabs=vocabs, mode=mode)
    model.reset()
    return model


def build_agent_from_config(config_path: str):
    config = read_json(config_path)
    skill_configs = config['skills']
    commutator_config = config['commutator']
    return Agent(skill_configs, commutator_config)


def interact_agent(config_path):
    a = build_agent_from_config(config_path)
    commutator = from_params(a.commutator_config)

    models = [build_model_from_config(sk) for sk in a.skill_configs]
    while True:
        # get input from user
        context = input(':: ')

        # check for exit command
        if context == 'exit' or context == 'stop' or context == 'quit' or context == 'q':
            return

        predictions = []
        for model in models:
            predictions.append({model.__class__.__name__: model.infer(context, )})
        idx, name, pred = commutator.infer(predictions, )
        print('>>', pred)

        a.history.append({'context': context, "predictions": predictions,
                          "winner": {"idx": idx, "model": name, "prediction": pred}})
        log.debug("Current history: {}".format(a.history))


def interact_model(config_path):
    config = read_json(config_path)
    model = build_model_from_config(config)

    while True:
        args = []
        for in_x in model.in_x:
            args.append(input('{}::'.format(in_x)))
            # check for exit command
            if args[-1] == 'exit' or args[-1] == 'stop' or args[-1] == 'quit' or args[-1] == 'q':
                return

        if len(args) == 1:
            pred = model(args)
        else:
            pred = model([args])

        print('>>', *pred)
