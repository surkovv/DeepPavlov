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

from deeppavlov.core.common.registry import register
from deeppavlov.core.data.data_learning_iterator import DataLearningIterator


@register('squad_iterator')
class SquadIterator(DataLearningIterator):
    def split(self, *args, **kwargs):
        for dt in ['train', 'valid', 'test']:
            setattr(self, dt, SquadIterator._extract_cqas(getattr(self, dt)))

    @staticmethod
    def _extract_cqas(data):
        """ Extracts context, question, answer, answer_start from SQuAD data

        Args:
            data: data in squad format

        Returns:
            list of (context, question), (answer_text, answer_start)
            answer text and answer_start are lists

        """
        cqas = []
        if data:
            for article in data['data']:
                for par in article['paragraphs']:
                    context = par['context']
                    for qa in par['qas']:
                        q = qa['question']
                        ans_text = []
                        ans_start = []
                        for answer in qa['answers']:
                            ans_text.append(answer['text'])
                            ans_start.append(answer['answer_start'])
                        cqas.append(((context, q), (ans_text, ans_start)))
        return cqas
