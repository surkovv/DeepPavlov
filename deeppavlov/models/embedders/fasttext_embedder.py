import os
import copy
import urllib.request
import fasttext
import numpy as np

from pathlib import Path

from deeppavlov.core.common import paths
from deeppavlov.core.common.registry import register
from deeppavlov.core.models.inferable import Inferable


# TODO: add URL of english embeddings
os.environ['EMBEDDINGS_URL'] = ''

@register('fasttext')
class FasttextUtteranceEmbed(Inferable):

    _model_dir_path = ''
    _model_fpath = ''

    @property
    def _model_path(self):
        p = Path(self._model_dir_path).joinpath(self._model_fpath)
        if not p.is_absolute():
            p = Path(paths.USR_PATH).joinpath(p)
        return p

    def __init__(self, model_dir_path, model_fpath, dim=None, fast=True):
        self._model_dir_path = model_dir_path
        self._model_fpath = model_fpath
        self.tok2emb = {}
        self.fast = fast

        self.fasttext_model = None
        if not self._model_path.is_file():
            emb_path = os.environ.get('EMBEDDINGS_URL')
            if not emb_path:
                raise RuntimeError('\n:: <ERR> no fasttext model provided\n')
            try:
                print('Trying to download a pretrained fasttext model'
                      ' from the repository')
                url = urllib.parse.urljoin(emb_path, self._model_fpath)
                urllib.request.urlretrieve(url, self._model_path.as_posix())
                print('Downloaded a fasttext model')
            except Exception as e:
                raise RuntimeError('Looks like the `EMBEDDINGS_URL` variable'
                                   ' is set incorrectly', e)
        print("Found fasttext model", self._model_path)
        self.model = fasttext.FastText(self._model_path.as_posix())
        self.dim = dim or self.model.args['dim']
        if self.dim > self.model.args['dim']:
            raise RuntimeError("Embeddings are too short")

    def __getitem__(self, token):
        if self.fast:
            if token not in self.tok2emb:
                self.tok2emb[token] = self.model[token][:self.dim]
            return self.tok2emb[token]
        return self.model.get_numpy_vector(token)[:self.dim]

    def _encode(self, utterance):
        if self.fast:
            embs = [self.__getitem__(t) for t in utterance.split(' ')]
            if embs:
                return np.mean(embs, axis=0)
            return np.zeros(self.dim, dtype=np.float32)
        return model.get_numpy_sentence_vector(utterance)
        #return model.get_numpy_text_vector(utterance)

    def _emb2str(self, vec):
        string = ' '.join([str(el) for el in vec])
        return string

    def infer(self, utterance):
        return self._encode(utterance)
