# Named Entity Recognition (NER)

## NER task

Named Entity Recognition (NER) is one of the most common tasks in natural language processing. 
In most of the cases, NER task can be formulated as: 

_Given a sequence of tokens (words, and maybe punctuation symbols) provide a tag from a
predefined set of tags for each token in the sequence._

For NER task there are some common types of entities used as tags:
- persons
- locations
- organizations
- expressions of time
- quantities
- monetary values 

Furthermore, to distinguish adjacent entities with the same tag many applications use BIO tagging scheme. 
Here "B" denotes beginning of an entity, "I" stands for "inside" and is used for all words comprising the entity except the first one, and "O" means the absence of entity. Example with dropped punctuation:

    Bernhard        B-PER
    Riemann         I-PER
    Carl            B-PER
    Friedrich       I-PER
    Gauss           I-PER
    and             O
    Leonhard        B-PER
    Euler           I-PER

In the example above PER means person tag, and "B-" and "I-" are prefixes identifying 
beginnings and continuations of the entities. Without such prefixes, it is impossible 
to separate Bernhard Riemann from Carl Friedrich Gauss.

## Training data
To train the neural network, you need to have a dataset in the following format:

    EU B-ORG
    rejects O
    the O
    call O
    of O
    Germany B-LOC
    to O
    boycott O
    lamb O
    from O
    Great B-LOC
    Britain I-LOC
    . O
    
    China B-LOC
    says O
    time O
    right O
    for O
    Taiwan B-LOC
    talks O
    . O

    ...

The source text is tokenized and tagged. For each token, there is a tag with BIO 
markup. Tags are separated from tokens with whitespaces. Sentences are separated with empty 
lines.

Dataset is a text file or a set of text files.
The dataset must be split into three parts: train, test, and validation. The train set 
is used for training the network, namely adjusting the weights with gradient descent. The 
validation set is used for monitoring learning progress and early stopping. The test set is 
used for final evaluation of model quality. Typical partition of a dataset into train, validation, and test 
are 80%, 10%, 10%, respectively.


## Configuration of the model

Configuration of the model can be performed in code or in JSON configuration file. To train 
the model you need to specify four groups of parameters:

- **`dataset_reader`**
- **`dataset_iterator`**
- **`chainer`**
- **`train`**

In the subsequent text we show the parameter specification in config file. However, the same notation can be used to specify parameters in code by replacing the JSON with python dictionary.

### Dataset Reader

The dataset reader is a class which reads and parses the data. It returns a dictionary with 
three fields: "train", "test", and "valid". The basic dataset reader is "ner_dataset_reader." 
The dataset reader config part with "ner_dataset_reader" should look like:
```
"dataset_reader": {
    "name": "ner_dataset_reader",
    "data_path": "/home/user/Data/conll2003/"
} 
```

where "name" refers to the basic ner dataset reader class and data_path is the path to the 
folder with three files, namely: "train.txt", "valid.txt", and "test.txt". Each file should
contain data in the format presented in *Training data* section. Each line in the file 
may contain additional information such as POS tags. However, the token must be the first in 
line and NER tag must be the last.

### Dataset Iterator

For simple batching and shuffling you can use "basic_dataset_iterator". The part of the 
configuration file for the dataset looks like:
 ```
"dataset_iterator": {
    "name": "basic_dataset_iterator"
}
```

There is no additional parameters in this part.

### Chainer

The chainer part of the configuration file contains the specification of the neural network 
model and supplementary things such as vocabularies. Chainer should be defined as follows:

```
"chainer": {
    "in": ["x"],
    "in_y": ["y"],
    "pipe": [
      ...
    ],
    "out": ["y_predicted"]
  }
```
The inputs and outputs must be specified in the pipe. "in" means regular input that is used 
for inference and train mode. "in_y" is used for training and usually contains ground truth answers. "out" field stands for model prediction. The model inside the 
pipe must have output variable with name "y_predicted" so that "out" knows where to get 
predictions.

The major part of "chainer" is "pipe". The "pipe" contains network and vocabularies. Firstly 
we define vocabularies needed to build the neural network:

```
"pipe": [
    {
        "id": "word_vocab",
        "name": "default_vocab",
        "fit_on": ["x"],
        "level": "token",
        "save_path": "ner_conll2003_model/word.dict",
        "load_path": "ner_conll2003_model/word.dict"
    },
    {
        "id": "tag_vocab",
        "name": "default_vocab",
        "fit_on": ["y"],
        "level": "token",
        "save_path": "ner_conll2003_model/tag.dict",
        "load_path": "ner_conll2003_model/tag.dict"
    },
    {
        "id": "char_vocab",
        "name": "default_vocab",
        "fit_on": ["x"],
        "level": "char",
        "save_path": "ner_conll2003_model/char.dict",
        "load_path": "ner_conll2003_model/char.dict"
    },
    ...
]
```
Parameters for the vocabulary are:

- **`id`** - the name of the vocabulary which will be used in other models
- **`name`** - always equal to `"default_vocab"`
- **`fit_on`** - on which part of the data the vocabulary should be fitted (built), 
possible values are ["x"] or ["y"]
- **`level`** - char or token level tokenization
- **`save_path`** - path to a new file to save the vocabulary
- **`load_path`** - path to an existing vocabulary

Vocabularies are used for holding sets of tokens, tags, or characters. They assign indices to 
elements of given sets an allow conversion from tokens to indices and vice versa. Conversion of such kind 
is needed to perform lookup in embeddings matrices and compute cross-entropy between predicted 
probabilities and target values. For each vocabulary "default_vocab" model is used. "fit_on" 
parameter defines on which part of the data the vocabulary is built. [\"x\"] 
stands for the x part of the data (tokens) and [\"y\"] stands for the y part (tags). We can also 
assemble character-level vocabularies by changing the value of "level" parameter: "char" instead of "token".

The network is defined by the following part of JSON config:
```json
"pipe": [
    ...
    {
        "in": ["x"],
        "in_y": ["y"],
        "out": ["y_predicted"],
        "name": "ner",
        "main": true,
        "save_path": "ner_conll2003_model/ner_model",
        "load_path": "ner_conll2003_model/ner_model",
        "word_vocab": "#word_vocab",
        "tag_vocab": "#tag_vocab",
        "char_vocab": "#char_vocab",
        "filter_width": 7,
        "embeddings_dropout": true,
        "n_filters": [
          128,
          128
        ],
        "token_embeddings_dim": 64,
        "char_embeddings_dim": 32,
        "use_batch_norm": true,
        "use_crf": true,
        "learning_rate": 1e-3,
        "dropout_rate": 0.5
    }
]
```

All network parameters are:
- **`in`** - the input to be taken from shared memory. Treated as x. It is used both 
during the training and the inference
- **`in_y`** - the target or y input to be taken from shared memory. This input is used during
 the training.
- **`name`** - the name of the model to be used. In this case we use 'ner' model originally 
imported from deeppavlov.models.ner.ner. We use only 'ner' name relying on the @registry 
decorator.
- **`main`** - (reserved for future use) a boolean parameter defining whether this is the main model. 
- **`save_path`** - path to the new file where the model will be saved
- **`load_path`** - path to a pretrained model from where it will be loaded
- **`token_embeddings_dim`** - token embeddings dimensionality (must agree with embeddings 
if they are provided), typical values are from 100 to 300
- **`word_vocab`** - in this field a link to word vocabulary from the pipe should be provided. To address
the vocabulary we use "#word_vocab" expression, where _word_vocab_ is the name of other vocabulary
defined in the pipe before
- **`net_type`** - type of the network, either 'cnn' or 'rnn'
- **`tag_vocab`** - in this field a link to the tag vocabulary from the pipe should be provided. In this case
"#tag_vocab" reference is used, addressing previously defined tag vocabulary
- **`char_vocab`** - in this field a link to the char vocabulary from the pipe must be provided. In this case
"#char_vocab" reference is used, addressing previously defined char vocabulary
- **`filter_width`** - the width of the convolutional kernel for Convolutional Neural Networks
- **`embeddings_dropout`** - boolean, whether to use dropout on embeddings or not
- **`n_filters`** - a list of output feature dimensionality for each layer. A value `[100, 200]`
means that there will be two layers with 100 and 200 units, respectively. 
- **`token_embeddings_dim`** - dimensionality of token embeddings. If embeddings are trained on
the go, this parameter determines dimensionality of the embedding matrix. If the pre-trained 
embeddings this argument must agree with the dimensionality of pre-trained embeddings
- **`char_embeddings_dim`** - character embeddings dimensionality, typical values are 25 - 100
- **`use_crf`** - boolean, whether to use Conditional Random Fields on top of the network (recommended)
- **`use_batch_norm`** - boolean, whether to use Batch Normalization or not. Affects only CNN networks
- **`use_capitalization`** - boolean, whether to include capitalization binary features to the input 
of the network. If True, a binary feature indicating whether the word starts with a capital 
letter will be concatenated to the word embeddings.
- **`dropout_rate`** - probability of dropping the hidden state, values from 0 to 1. 0.5 
works well in most of the cases
- **`learning_rate`**: learning rate to use during the training (usually from 0.01 to 0.0001)

After the "chainer" part you should specify the "train" part:

```
"train": {
    "epochs": 100,
    "batch_size": 64,

    "metrics": ["ner_f1"],
    "validation_patience": 5,
    "val_every_n_epochs": 5,

    "log_every_n_epochs": 1,
    "show_examples": false
}
```
 
training parameters are:
- **`epochs`** - number of epochs (usually 10 - 100)
- **`batch_size`** - number of samples in a batch (usually 4 - 64)
- **`metrics`** - metrics to validate the model. For NER task we recommend using ["ner_f1"]
- **`validation_patience`** - parameter of early stopping: for how many epochs the training can continue without improvement of metric value on the validation set
- **`val_every_n_epochs`** - how often the metrics should be computed on the validation set
- **`log_every_n_epochs`** - how often the results should be logged
- **`show_examples`** - whether to show results of the network predictions


And now all parts together:
```
{
  "dataset_reader": {
    "name": "ner_dataset_reader",
    "data_path": "conll2003/"
  },
  "dataset_iterator": {
    "name": "basic_dataset_iterator"
  },
  "chainer": {
    "in": ["x"],
    "in_y": ["y"],
    "pipe": [
      {
        "id": "word_vocab",
        "name": "default_vocab",
        "fit_on": ["x"],
		"level": "token",
        "save_path": "ner_conll2003_model/word.dict",
        "load_path": "ner_conll2003_model/word.dict"
      },
      {
        "id": "tag_vocab",
        "name": "default_vocab",
        "fit_on": ["y"],
		"level": "token",
        "save_path": "ner_conll2003_model/tag.dict",
        "load_path": "ner_conll2003_model/tag.dict"
      },
      {
        "id": "char_vocab",
        "name": "default_vocab",
        "fit_on": ["x"],
		"level": "char",
        "save_path": "ner_conll2003_model/char.dict",
        "load_path": "ner_conll2003_model/char.dict"
      },
      {
        "in": ["x"],
        "in_y": ["y"],
        "out": ["y_predicted"],
        "name": "ner",
        "main": true,
        "save_path": "ner_conll2003_model/ner_model",
        "load_path": "ner_conll2003_model/ner_model",
        "word_vocab": "#word_vocab",
        "tag_vocab": "#tag_vocab",
        "char_vocab": "#char_vocab",
        "verbouse": true,
        "filter_width": 7,
        "embeddings_dropout": true,
        "n_filters": [
          128,
          128
        ],
        "token_embeddings_dim": 64,
        "char_embeddings_dim": 32,
        "use_batch_norm": true,
        "use_crf": true,
        "learning_rate": 1e-3,
        "dropout_rate": 0.5
      }
    ],
    "out": ["y_predicted"]
  },
  "train": {
    "epochs": 100,
    "batch_size": 64,
    "metrics": ["ner_f1"],
    "validation_patience": 5,
    "val_every_n_epochs": 5,
    "log_every_n_epochs": 1,
    "show_examples": false
  }
}
```

## Train and use the model

Please see an example of training a NER model and using it for prediction:

```python
from deeppavlov.core.commands.train import train_model_from_config
from deeppavlov.core.commands.infer import interact_model
PIPELINE_CONFIG_PATH = 'configs/ner/ner_conll2003.json'
train_model_from_config(PIPELINE_CONFIG_PATH)
interact_model(PIPELINE_CONFIG_PATH)
```

This example assumes that the working directory is deeppavlov.


## OntoNotes NER

A pre-trained model for solving OntoNotes task can be used as following:
```python
from deeppavlov.core.commands.infer import interact_model
interact_model('deeppavlov/configs/ner/ner_ontonotes.json')
```
Or from command line:

```bash
python deeppavlov/deep.py interact deeppavlov/configs/ner/ner_ontonotes.json
```

Since the model is built with cuDNN version of LSTM, the GPU along with installed cuDNN library needed to run this model.
The F1 scores of this model on test part of OntoNotes is presented in table below.

| Model                      | F1 score         |
|----------------------------|:----------------:|
|DeepPavlov                  |**87.07** ± 0.21  |
|Strubell at al. (2017)   [1]|86.84 ± 0.19      |
|Chiu and Nichols (2016)  [2]|86.19 ± 0.25      |
|Spacy                       |85.85             |
|Durrett and Klein (2014) [3]|84.04             |
|Ratinov and Roth (2009)  [4]|83.45             |

Scores by entity type are presented in the table below:

|Tag     |F1 score|
|------  |:------:|
|TOTAL | 87.07 |
|CARDINAL	|82.80|
|DATE	|84.87|
|EVENT	|68.39    |
|FAC	|68.07|
|GPE	|94.61|
|LANGUAGE	|62.91|
|LAW	|48.27|
|LOC	|72.39|
|MONEY	|87.79|
|NORP	|94.27|
|ORDINAL	|79.53|
|ORG	|85.59|
|PERCENT	|89.41|
|PERSON	|91.67|
|PRODUCT	|58.90|
|QUANTITY	|77.93|
|TIME	|62.50|
|WORK_OF_ART	|53.17|


## Results

The NER network component reproduces the architecture from the paper "_Application of a Hybrid Bi-LSTM-CRF model to the task of Russian Named Entity Recognition_" https://arxiv.org/pdf/1709.09686.pdf, which is inspired by LSTM+CRF architecture from https://arxiv.org/pdf/1603.01360.pdf.

Bi-LSTM architecture of NER network was tested on three datasets:
- Gareev corpus [5] (obtainable by request to authors)
- FactRuEval 2016 [6]
- Persons-1000 [7]

The F1 measure for our model along with the results of other published solutions are provided in the table below:

| Models                | Gareev’s dataset | Persons-1000 | FactRuEval 2016 |
|---------------------- |:----------------:|:------------:|:---------------:|
| Gareev et al. [5]     | 75.05            |              |                 |
| Malykh et al. [8]     | 62.49            |              |                 |
| Trofimov  [13]        |                  | 95.57        |                 |
| Rubaylo et al. [9]    |                  |              | 78.13           |
| Sysoev et al. [10]    |                  |              | 74.67           |
| Ivanitsky et al.  [11]|                  |              | **87.88**       |
| Mozharova et al.  [12]|                  | 97.21        |                 |
| Our (Bi-LSTM+CRF)     | **87.17**        | **99.26**    | 82.10           ||

## Literature
[1] - Strubell at al. (2017) Strubell, Emma, et al. "Fast and accurate entity recognition with iterated dilated convolutions." Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing. 2017.

[2] - Jason PC Chiu and Eric Nichols. 2016. Named entity recognition with bidirectional lstm-cnns. Transactions of the Association for Computational Linguistics, 4:357–370.

[3] - Greg Durrett and Dan Klein. 2014. A joint model for entity analysis: Coreference, typing and linking. Transactions of the Association for Computational Linguistics, 2:477–490.

[4] - Lev Ratinov and Dan Roth. 2009. Design challenges and misconceptions in named entity recognition. In Proceedings of the Thirteenth Conference on Computational Natural Language Learning, pages 147–155. Association for Computational Linguistics.

[5] - Rinat Gareev, Maksim Tkachenko, Valery Solovyev, Andrey Simanovsky, Vladimir Ivanov: Introducing Baselines for Russian Named Entity Recognition. Computational Linguistics and Intelligent Text Processing, 329 -- 342 (2013).

[6] - https://github.com/dialogue-evaluation/factRuEval-2016

[7] - http://ai-center.botik.ru/Airec/index.php/ru/collections/28-persons-1000

[8] - Malykh, Valentin, and Alexey Ozerin. "Reproducing Russian NER Baseline Quality without Additional Data." CDUD@ CLA. 2016.

[9] - Rubaylo A. V., Kosenko M. Y.: Software utilities for natural language information
retrievial. Almanac of modern science and education, Volume 12 (114), 87 – 92.(2016)

[10] - Sysoev A. A., Andrianov I. A.: Named Entity Recognition in Russian: the Power of Wiki-Based Approach. dialog-21.ru

[11] - Ivanitskiy Roman, Alexander Shipilo, Liubov Kovriguina: Russian Named Entities Recognition and Classification Using Distributed Word and Phrase Representations. In SIMBig, 150 – 156. (2016).

[12] - Mozharova V., Loukachevitch N.: Two-stage approach in Russian named entity recognition. In Intelligence, Social Media and Web (ISMW FRUCT), 2016 International FRUCT Conference, 1 – 6 (2016)

[13] - Trofimov, I.V.: Person name recognition in news articles based on the persons- 1000/1111-F collections. In: 16th All-Russian Scientific C onference Digital Libraries: Advanced Methods and Technologies, Digital Collections, RCDL 2014,pp. 217 – 221 (2014).
