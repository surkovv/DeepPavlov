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

REQ_URLS = {
    'http://lnsigo.mipt.ru/export/deeppavlov_data/go_bot.tar.gz',
    'http://lnsigo.mipt.ru/export/deeppavlov_data/intents.tar.gz',
    'http://lnsigo.mipt.ru/export/deeppavlov_data/ner.tar.gz',
    'http://lnsigo.mipt.ru/export/deeppavlov_data/ner_conll2003_emb.tar.gz',
    'http://lnsigo.mipt.ru/export/deeppavlov_data/error_model.tar.gz',
    'http://lnsigo.mipt.ru/export/deeppavlov_data/ranking.tar.gz',
    'http://lnsigo.mipt.ru/export/embeddings/insurance_v1_word2vec',
    'http://lnsigo.mipt.ru/export/embeddings/glove.6B.100d.txt',
    'http://lnsigo.mipt.ru/export/deeppavlov_data/vocabs.tar.gz',
    'http://lnsigo.mipt.ru/export/deeppavlov_data/slots.tar.gz',
    'http://lnsigo.mipt.ru/export/deeppavlov_data/embeddings/dstc2_fastText_model.bin',
    'http://lnsigo.mipt.ru/export/datasets/dstc2.tar.gz',
    'http://lnsigo.mipt.ru/export/deeppavlov_data/squad_model.tar.gz',
    'http://lnsigo.mipt.ru/export/deeppavlov_data/seq2seq_go_bot.tar.gz',
    'http://lnsigo.mipt.ru/export/deeppavlov_data/ner_ontonotes.tar.gz',
    'http://lnsigo.mipt.ru/export/deeppavlov_data/ner_ontonotes_senna.tar.gz',
    'http://lnsigo.mipt.ru/export/deeppavlov_data/senna.tar.gz'
}

OPT_URLS = {
    'http://lnsigo.mipt.ru/export/deeppavlov_data/embeddings/wiki.en.bin',
    'http://lnsigo.mipt.ru/export/embeddings/wiki-news-300d-1M.vec',
    'http://lnsigo.mipt.ru/export/embeddings/wiki-news-300d-1M-char.vec',
}

ALL_URLS = REQ_URLS.union(OPT_URLS)

EMBEDDING_URLS = {
    'http://lnsigo.mipt.ru/export/deeppavlov_data/embeddings/wiki.en.bin',
    'http://lnsigo.mipt.ru/export/deeppavlov_data/embeddings/dstc2_fastText_model.bin',
    'http://lnsigo.mipt.ru/export/embeddings/insurance_v1_word2vec'
    'http://lnsigo.mipt.ru/export/deeppavlov_data/embeddings/dstc2_fastText_model.bin',
    'http://lnsigo.mipt.ru/export/embeddings/wiki-news-300d-1M.vec',
    'http://lnsigo.mipt.ru/export/embeddings/wiki-news-300d-1M-char.vec',
    'http://lnsigo.mipt.ru/export/embeddings/glove.6B.100d.txt'
}

DATA_URLS = {
    'http://lnsigo.mipt.ru/export/datasets/dstc2.tar.gz',
    'http://lnsigo.mipt.ru/export/datasets/insuranceQA-master.zip'
}
