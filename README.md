[![License Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/deepmipt/DeepPavlov/blob/master/LICENSE)
![Python 3.6](https://img.shields.io/badge/python-3.6-green.svg)

<p align="center">
 <img src="http://ipavlov.ai/img/ipavlov_logo.png" width="20%" height="20%">
</p>

# DeepPavlov
## We are in a really early Alfa release. You have to be ready to hard adventures.
An open-source conversational AI library, built on TensorFlow and Keras, and designed for
 * NLP and dialog systems research
 * implementation and evaluation of complex conversational systems
 
Our goal is to provide researchers with:
 * a framework for implementing and testing their own dialog models with subsequent sharing of that models
 * set of predefined NLP models / dialog system components (ML/DL/Rule-based) and pipeline templates
 * benchmarking environment for conversational models and systematized access to relevant datasets
 
and AI-application developers with:
 * framework for building conversational software
 * tools for application integration with adjacent infrastructure (messengers, helpdesk software etc.)
 * Licensed under the Apache License, Version 2.0.

## Features
 * [Goal-oriented dialog agent](deeppavlov/skills/go_bot/README.md) is based on Hybrid Code Networks (HCNs) architecture from [Jason D. Williams, Kavosh Asadi, Geoffrey Zweig, Hybrid Code Networks: practical and efficient end-to-end dialog control with supervised and reinforcement learning – 2017](https://arxiv.org/abs/1702.03274). It allows to predict responses in the goal-oriented task dialogue. The model is quite customizable: embeddings, slot filler and intent classifier can be used or not on demand.

 * [Slot filling component](deeppavlov/models/ner/README.md) is based on neural Named Entity Recognition network and fuzzy Levenshtein search to extract normalized slot values from the text. The NER network component reproduces architecture from the paper [Application of a Hybrid Bi-LSTM-CRF model to the task of Russian Named Entity Recognition](https://arxiv.org/pdf/1709.09686.pdf), which is inspired by LSTM+CRF architecture from https://arxiv.org/pdf/1603.01360.pdf.

 * [Intent classification component](https://github.com/deepmipt/DeepPavlov/blob/master/deeppavlov/models/classifiers/intents/README.md) is based on shallow-and-wide Convolutional Neural Network architecture from [Kim Y. Convolutional neural networks for sentence classification – 2014](https://arxiv.org/pdf/1408.5882). The model allows multilabel classification of sentences.

 * [Automatic spelling correction component](models/spellers/error_model/README.md) is based on [An Improved Error Model for Noisy Channel Spelling Correction by Eric Brill and Robert C. Moore](http://www.aclweb.org/anthology/P00-1037) and uses statistics based error model, a static dictionary and an ARPA language model to correct spelling errors.
 
 * [Pre-trained embeddings library](pretrained-vectors.md). Pre-trained on joint [Russian Wikipedia](https://ru.wikipedia.org/wiki/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0) and [Lenta.ru](https://lenta.ru/) corpora word vectors for Russian language. 

### Contents

 * [Installation](#installation)
 * [Quick start](#quick-start)
 * [Support](#support)
 * [The Team](#the-team)
 * [License](#license)
 * [Deeppavlov overview](#deeppavlov-overview)
    * [Project modules](#project-modules)
    * [Config](#config)
    * [DatasetReader](#datasetreader)
    * [Dataset](#dataset)
    * [Vocab](#vocab)
    * [Model](#model)
    * [Training](#training)
    * [Inferring](#inferring)
 * [Pre-trained models](#pre-trained-models)
    * [Dialogue Bot for goal-oriented task](#dialogue-bot-for-goal-oriented-task)
    * [Neural Model for Intent Classification](#neural-model-for-intent-classification)
    * [Neural Named Entity Recognition](#neural-named-entity-recognition)
    * [Automatic Spelling Correction](#automatic-spelling-correction)

## Installation
1. Create a virtual environment with `Python 3.6`
2. Activate the environment.
3. Clone the repo
   ```
   git clone https://github.com/deepmipt/DeepPavlov.git
   ```
3. `cd` to the project root.
4. Install the requirements:
    ```
    python install.py
    ```
5. If there were errors during installation, try to run the previous command again.

## Quick start
With the purpose to interact with our pre-trained models, they should be downloaded first:

```
cd deeppavlov/
python download.py [-all]
```
* `[-all]` option is not required for basic examples; it will download **all** our pre-trained models.

* Warning! `[-all]` requires about 10 GB of free space on disk.

Then the models can be interacted or trained with the following command:

```
python deep.py <mode> <path_to_config>
```

* `<mode>` can be 'train', 'interact' or 'interactbot'
* `<path_to_config>` should be a path to an NLP pipeline json config

For 'interactbot' mode you should specify Telegram bot token in `-t` parameter or in `TELEGRAM_TOKEN` environment variable.


Available model configs are:

*skills/go_bot/config.json*

*models/classifiers/intents/config_dstc2.json*

*models/ner/config.json*

*models/spellers/error_model/config_en.json*


## Support & collaboration

If you have any questions, bug reports or feature requests, please feel free to post on our [Github Issues](https://github.com/deepmipt/DeepPavlov/issues) page. Please tag your issue with 'bug', 'feature request', or 'question'.  Also we’ll be glad to see your pull-requests to add new datasets, models, embeddings and e.t.c.

## The Team

DeepPavlov is built and maintained by [Neural Networks and Deep Learning Lab](https://mipt.ru/english/research/labs/neural-networks-and-deep-learning-lab) at [MIPT](https://mipt.ru/english/) within [iPavlov](http://ipavlov.ai/) project (part of [National Technology Initiative](https://asi.ru/eng/nti/)) and in partnership with [Sberbank](http://www.sberbank.com/).

<p align="center">
<img src="http://ipavlov.ai/img/ipavlov_footer.png" width="50%" height="50%"></img>
</p>

## License

DeepPavlov is Apache 2.0 - licensed.

---

## DeepPavlov overview

### Project modules

<table>
<tr>
    <td><b> deeppavlov.core.commands </b></td>
    <td> basic training and inferring functions  </td>
</tr>
<tr>
    <td><b> deeppavlov.core.common </b></td>
    <td> registration and classes initialization functionality, class method decorators </td>
</tr>
<tr>
    <td><b> deeppavlov.core.data </b></td>
    <td> basic <b><i>Dataset</i></b>, <b><i>DatasetReader</i></b> and <b><i>Vocab</i></b> classes </td>
</tr>
<tr>
    <td><b> deeppavlov.core.models </b></td>
    <td> abstract model classes and interfaces </td>
</tr>
<tr>
    <td><b> deeppavlov.dataset_readers </b></td>
    <td> concrete <b><i>DatasetReader</i></b> classes </td>
</tr>
<tr>
    <td><b> deeppavlov.datasets </b></td>
    <td> concrete <b><i>Dataset</i></b> classes </td>
</tr>
<tr>
    <td><b> deeppavlov.models </b></td>
    <td> concrete <b><i>Model</i></b> classes </td>
</tr>
<tr>
    <td><b> deeppavlov.skills </b></td>
    <td> <b><i>Skill</i></b> classes. Skills are dialog models.</td>
</tr>
<tr>
    <td><b> deeppavlov.vocabs </b></td>
    <td> concrete <b><i>Vocab</i></b> classes </td>
</tr>
</table>

### Config

An NLP pipeline config is a JSON file, which consists of four required elements:

```javascript
{
  "dataset_reader": {
  },
  "dataset": {
  },
  "vocabs": {
  },
  "model": {
  }
}
```

Each class in the config has `name` parameter, which is its registered codename
 and can have any other parameters, repeating its `__init__()` method arguments.
 Default values of `__init__()` arguments will be overridden with the config values
 during class instance initialization.

### DatasetReader

`DatasetReader` class reads data and returns it in a specified format.
A concrete `DatasetReader` class should be inherited from base
`deeppavlov.data.dataset_reader.DatasetReader` class and registered with a codename:

```python
@register('dstc2_datasetreader')
class DSTC2DatasetReader(DatasetReader):
```

### Dataset

`Dataset` forms needed sets of data ('train', 'valid', 'test') and forms data batches.
A concrete `Dataset` class should be registered and can be inherited from
`deeppavlov.data.dataset_reader.Dataset` class. `deeppavlov.data.dataset_reader.Dataset`
is not an abstract class and can be used as `Dataset` as well.

### Vocab

`Vocab` is a trainable class, which forms and serialize vocabs. Vocabs index any data.
For example, tokens to indices and backwards, chars to indices, classes to indices, etc.
It can index X (features) and y (answers) types of data. A concrete `Vocab` class
should be registered and can be inherited from `deeppavlov.data.vocab.DefaultVocabulary` class.
`deeppavlov.data.vocab.DefaultVocabulary` is not an abstract class and can be used as `Vocab` as well.

### Model

`Model` is the main class which rules the training/inferring process and feature generation.
If a model requires other models to produce features, they need to be passed in its constructor
and config. All models can be nested as much as needed. For example, a skeleton of
`deeppavlov.skills.go_bot.go_bot.GoalOrientedBot` consists of 11 separate model classes,
3 of which are neural networks:

```javascript
{
  "model": {
    "name": "go_bot",
    "network": {
      "name": "go_bot_rnn"
    },
    "slot_filler": {
      "name": "dstc_slotfilling",
      "ner_network": {
         "name": "ner_tagging_network",
      }
    },
    "intent_classifier": {
      "name": "intent_model",
      "embedder": {
        "name": "fasttext"
      },
      "tokenizer": {
        "name": "nltk_tokenizer"
      }
    },
    "embedder": {
      "name": "fasttext"
    },
    "bow_encoder": {
      "name": "bow"
    },
    "tokenizer": {
      "name": "spacy_tokenizer"
    },
    "tracker": {
      "name": "featurized_tracker"
    }
  }
}
```

All models should be registered and inherited from `deeppavlov.core.models.inferable.Inferable`
or from both `Inferable` and `deeppavlov.core.models.trainable.Trainable` interfaces.
Models inherited from `Trainable` interface can be trained. Models inherited from `Inferable`
interface can be only inferred. Usually `Inferable` models are rule-based models or
pre-trained models that we import from third-party libraries (like `NLTK`, `Spacy`, etc.).

### Training

All models inherited from `deeppavlov.core.models.trainable.Trainable` interface can be trained.
The training process should be described in `train()` method:

 ```python
 @register("my_model")
 class MyModel(Inferable, Trainable):

    def train(*args, **kwargs):
        """
        Implement training here.
        """
 ```

All parameters for training which can be changed during experiments (like *num of epochs*,
*batch size*, *patience*, *learning rate*, *optimizer*) should be passed to a model's
`__init__()`. The default parameters values from `__init__()` are overridden with JSON config values.
To change these values, there is no need to rewrite the code, only the config should be changed.

The training process is managed by `train_now` attribute. If `train_now` is *True*,
a model is being trained. This parameter is useful when using `Vocab`, because in a single
model run some vocabs can be trained, while some only inferred by other models in pipeline.
The training parameters in JSON config can look like this:

```javascript
{
  "model": {
    "name": "my_model",
    "train_now": true,
    "optimizer": "Adam",
    "learning_rate": 0.2,
    "num_epochs": 1000
  }
}
```

Training is triggered by `deeppavlov.core.commands.train.train_model_from_config()` function.

### Inferring

All models inherited from `deeppavlov.core.models.inferable.Inferable` interface can be inferred.
The `infer()` method should return what a model can do. For example, a *tokenizer* should return
*tokens*, a *NER recognizer* should return *recognized entities*, a *bot* should return a *replica*.
A particular format of returned data should be defined in `infer()`.

Inferring is triggered by `deeppavlov.core.commands.train.infer_model_from_config()` function.
There is no need in s separate JSON for inferring. `train_now` parameter is ignored during
inferring.

## Pre-trained models

The suggested in [Quick start](#quick-start) configs are available for the following models.

### Dialogue Bot for goal-oriented task

A dialog agent based on Hybrid Code Network pre-trained for restaurant recommendation task.
[Details](https://github.com/deepmipt/DeepPavlov/tree/master/deeppavlov/skills/go_bot)

### Neural Model for Intent Classification

A model for user intent classification for restaurant recommendation task.
[Details](https://github.com/deepmipt/DeepPavlov/tree/master/deeppavlov/models/classifiers/intents)

### Neural Named Entity Recognition

A model for entities recognition in restaurant recommendation task.
[Details](https://github.com/deepmipt/DeepPavlov/tree/master/deeppavlov/models/ner)

### Automatic Spelling Correction

A spelling correction model, currently available for English and Russian languages.
[Details](https://github.com/deepmipt/DeepPavlov/tree/master/deeppavlov/models/spellers/error_model)
