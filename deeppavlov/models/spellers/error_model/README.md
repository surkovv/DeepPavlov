[![License Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](/LICENSE.txt)
![Python 3.6](https://img.shields.io/badge/python-3.6-green.svg)

# Automatic spelling correction component

Automatic spelling correction component is based on
[An Improved Error Model for Noisy Channel Spelling Correction](http://www.aclweb.org/anthology/P00-1037)
by Eric Brill and Robert C. Moore and uses statistics based error model,
a static dictionary and an ARPA language model to correct spelling errors.  
We provide everything you need to build a spelling correction module for russian and english languages
and some guidelines for how to collect appropriate datasets for other languages.

## Usage

#### Config parameters:  
* `name` always equals to `"spelling_error_model"`
* `train_now` — without this flag set to `true` train phase of an error model will be skipped
* `model_file` — name of the file that the model will be saved to and loaded from, defaults to `"error_model.tsv"` 
* `window` — window size for the error model from `0` to `4`, defaults to `1`
* `lm_file` — path to the ARPA language model file. If omitted, all of the dictionary words will be handled as equally probable
* `dictionary` — description of a static dictionary model, instance of (or inherited from) `deeppavlov.vocabs.static_dictionary.StaticDictionary`
    * `name` — `"static_dictionary"` for a custom dictionary or one of two provided:
        * `"russian_words_vocab"` to automatically download and use a list of russian words from [https://github.com/danakt/russian-words/](https://github.com/danakt/russian-words/)  
        * `"wikitionary_100K_vocab"` to automatically download a list of most common words from Project Gutenberg from [Wiktionary](https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists#Project_Gutenberg)
     
    * `dictionary_name` — name of a directory where a dictionary will be built to and loaded from, defaults to `"dictionary"` for static_dictionary
    * `raw_dictionary_path` — path to a file with a line-separated list of dictionary words, required for static_dictionary

A working config could look like this:

```json
{
  "model": {
    "name": "spelling_error_model",
    "model_file": "error_model_en.tsv",
    "train_now": true,
    "window": 1,
    "dictionary": {
      "name": "wikitionary_100K_vocab"
    },
    "lm_file": "/data/data/enwiki_no_punkt.arpa.binary"
  }
}
```

#### Usage example
This model expects a sentence string with space-separated tokens in lowercase as it's input and returns the same string with corrected words.
Here's an example code that will read input data from stdin line by line and output resulting text into stdout:

```python
import json
import sys

from deeppavlov.core.commands.infer import build_model_from_config
from deeppavlov.core.commands.utils import set_usr_dir

CONFIG_PATH = 'deeppavlov/models/spellers/error_model/config_ru_custom_vocab.json'
usr_dir = set_usr_dir(CONFIG_PATH)

with open(CONFIG_PATH) as config_file:
    config = json.load(config_file)

model = build_model_from_config(config)
for line in sys.stdin:
    print(model.infer(line), flush=True)
```

if we save it as `example.py` then it could be used like so:

```bash
cat input.txt | python3 example.py > output.txt
```

## Training

#### Error model

For the training phase config file needs to also include these parameters:

* `dataset` — it should always be set like `"dataset": {"name": "typos_dataset"}`
* `dataset_reader`
    * `name` — `typos_custom_reader` for a custom dataset or one of two provided:
        * `typos_kartaslov_reader` to automatically download and process misspellings dataset for russian language from
         [https://github.com/dkulagin/kartaslov/tree/master/dataset/orfo_and_typos](https://github.com/dkulagin/kartaslov/tree/master/dataset/orfo_and_typos)
        * `typos_wikipedia_reader` to automatically download and process
         [a list of common misspellings from english Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines)
    * `data_path` — required for typos_custom_reader as a path to a dataset file,
     where each line contains a misspelling and a correct spelling of a word separated by a tab symbol

```python
from deeppavlov.core.commands.train import train_model_from_config
from deeppavlov.core.commands.utils import set_usr_dir

MODEL_CONFIG_PATH = 'deeppavlov/models/spellers/error_model/config_ru_custom_vocab.json'
usr_dir = set_usr_dir(MODEL_CONFIG_PATH)
train_model_from_config(MODEL_CONFIG_PATH)
```

#### Language model

This model uses [KenLM](http://kheafield.com/code/kenlm/) to process language models, so if you want to build your own,
we suggest you consult with it's website. We do also provide our own language models for
[english](http://lnsigo.mipt.ru/export/lang_models/en_wiki_no_punkt.arpa.binary.gz) \(5.5GB\) and
[russian](http://lnsigo.mipt.ru/export/lang_models/ru_wiyalen_no_punkt.arpa.binary.gz) \(5GB\) languages.

## Ways to improve

* locate bottlenecks in code and rewrite them in Cython to improve performance
* find a way to add skipped spaces and remove superfluous ones
* find or learn a proper balance between an error model and a language model scores when ranking candidates
* implement [Discriminative Reranking for Spelling Correction](http://www.aclweb.org/anthology/Y06-1009)
by Yang Zhang, Pilian He, Wei Xiang and Mu Li