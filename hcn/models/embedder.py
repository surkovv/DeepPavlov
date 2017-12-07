from gensim.models import word2vec
import numpy as np
from pathlib import Path

from deeppavlov.common import paths
from deeppavlov.common.registry import register_model
from deeppavlov.models.trainable import Trainable
from deeppavlov.models.inferable import Inferable


@register_model('w2v')
class UtteranceEmbed(Trainable, Inferable):
    def __init__(self, corpus_path, model_dir_path='emb', model_fname='text8.model', dim=300,
                 train_now=False):
        self._corpus_path = corpus_path
        self._model_path = Path(paths.USR_PATH).joinpath(model_dir_path, model_fname)
        self.dim = dim
        self._train_now = train_now

        if self._train_now:
            self.train()
            self.model = word2vec.Word2Vec.load(self._model_path)

        else:
            try:
                self.model = word2vec.Word2Vec.load(str(self._model_path))
            except:
                print("There is no pretrained model, training a new one anyway.")
                self.train()
                self.model = word2vec.Word2Vec.load(str(self._model_path))

    def _encode(self, utterance):
        embs = [self.model[word] for word in utterance.split(' ') if word and word in self.model]
        # average of embeddings
        if len(embs):
            return np.mean(embs, axis=0)
        else:
            return np.zeros([self.dim], np.float32)

    def train(self):
        sentences = word2vec.Text8Corpus(self._corpus_path)

        print(':: creating new word2vec model')
        model = word2vec.Word2Vec(sentences, size=self.dim)

        if not self._model_path.parent.exists():
            Path.mkdir(self._model_path.parent)

        model.save(str(self._model_path))
        print(':: model saved to path')

    def infer(self, utterance):
        return self._encode(utterance)
