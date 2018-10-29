# Copyright 2017 Neural Networks and Deep Learning lab, MIPT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import Counter, defaultdict, Iterable
from itertools import chain
from pathlib import Path

import numpy as np

from deeppavlov.core.common.registry import register
from deeppavlov.core.common.errors import ConfigError
from deeppavlov.core.common.log import get_logger
from deeppavlov.core.models.estimator import Estimator
from deeppavlov.core.data.utils import zero_pad, is_str_batch, flatten_str_batch

log = get_logger(__name__)


@register('simple_vocab')
class SimpleVocabulary(Estimator):
    """Implements simple vocabulary."""
    def __init__(self,
                 special_tokens=tuple(),
                 default_token=None,
                 max_tokens=2**30,
                 min_freq=0,
                 pad_with_zeros=False,
                 unk_token=None,
                 *args,
                 **kwargs):
        super().__init__(**kwargs)
        self.special_tokens = special_tokens
        self.default_token = default_token
        self._max_tokens = max_tokens
        self._min_freq = min_freq
        self._pad_with_zeros = pad_with_zeros
        self.unk_token = unk_token
        self.reset()
        if self.load_path:
            self.load()

    def fit(self, *args):
        # return None
        self.reset()
        tokens = chain(*args)
        # filter(None, <>) -- to filter empty tokens
        self.freqs = Counter(filter(None, flatten_str_batch(tokens)))
        for special_token in self.special_tokens:
            self._t2i[special_token] = self.count
            self._i2t.append(special_token)
            self.count += 1
        for token, freq in self.freqs.most_common()[:self._max_tokens]:
            if freq >= self._min_freq:
                self._t2i[token] = self.count
                self._i2t.append(token)
                self.count += 1

    def _add_tokens_with_freqs(self, tokens, freqs):
        self.freqs = Counter()
        self.freqs.update(dict(zip(tokens, freqs)))
        for token, freq in zip(tokens, freqs):
            if freq >= self._min_freq or token in self.special_tokens:
                self._t2i[token] = self.count
                self._i2t.append(token)
                self.count += 1

    def __call__(self, batch, is_top=True, **kwargs):
        if isinstance(batch, Iterable) and not isinstance(batch, str):
            looked_up_batch = [self(sample, is_top=False) for sample in batch]
        else:
            return self[batch]
        if is_top and self._pad_with_zeros and not is_str_batch(looked_up_batch):
            looked_up_batch = zero_pad(looked_up_batch)

        return looked_up_batch

    def save(self):
        log.info("[saving vocabulary to {}]".format(self.save_path))
        with self.save_path.open('wt', encoding='utf8') as f:
            for n in range(len(self)):
                token = self._i2t[n]
                cnt = self.freqs[token]
                f.write('{}\t{:d}\n'.format(token, cnt))

    def load(self):
        self.reset()
        if self.load_path:
            if self.load_path.is_file():
                log.info("[loading vocabulary from {}]".format(self.load_path))
                tokens, counts = [], []
                for ln in self.load_path.open('r', encoding='utf8'):
                    token, cnt = ln.split('\t', 1)
                    tokens.append(token)
                    counts.append(int(cnt))
                self._add_tokens_with_freqs(tokens, counts)
            elif isinstance(self.load_path, Path):
                if not self.load_path.parent.is_dir():
                    raise ConfigError("Provided `load_path` for {} doesn't exist!".format(
                        self.__class__.__name__))
        else:
            raise ConfigError("`load_path` for {} is not provided!".format(self))

    @property
    def len(self):
        return len(self)

    def keys(self):
        return (self[n] for n in range(self.len))

    def values(self):
        return list(range(self.len))

    def items(self):
        return zip(self.keys(), self.values())

    def __getitem__(self, key):
        if isinstance(key, (int, np.integer)):
            return self._i2t[key]
        elif isinstance(key, str):
            return self._t2i[key]
        else:
            raise NotImplementedError("not implemented for type `{}`".format(type(key)))

    def __contains__(self, item):
        return item in self._t2i

    def __len__(self):
        return len(self._i2t)

    def reset(self):
        # default index is the position of default_token
        if self.default_token is not None:
            default_ind = self.special_tokens.index(self.default_token)
        else:
            default_ind = 0
        self.freqs = None
        unk_index = 0
        if self.unk_token in self.special_tokens:
            unk_index = self.special_tokens.index(self.unk_token)
        self._t2i = defaultdict(lambda: unk_index)
        self._i2t = []
        self.count = 0
