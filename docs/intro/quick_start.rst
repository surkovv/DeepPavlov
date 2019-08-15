QuickStart
------------

There is a bunch of great pre-trained NLP models in DeepPavlov. Each model is
determined by its config file.

List of models is available on :doc:`the doc page </features/overview>` or in
the ``deeppavlov.configs`` (Python):

    .. code:: python
        
        from deeppavlov import configs

When you're decided on the model (+ config file), there are two ways to train,
evaluate and infer it:

* via `Command line interface (CLI)`_ and
* via `Python`_.

Before making choice of an interface, install model's package requirements
(CLI):

    .. code:: bash
        
        python -m deeppavlov install <config_path>

    * where ``<config_path>`` is path to the chosen model's config file (e.g.
      ``deeppavlov/configs/ner/slotfill_dstc2.json``) or just name without
      `.json` extension (e.g. ``slotfill_dstc2``)


Command line interface (CLI)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get predictions from a model interactively through CLI, run

    .. code:: bash
        
        python -m deeppavlov interact <config_path> [-d]

    * ``-d`` downloads required data -- pretrained model files and embeddings
      (optional).

You can train it in the same simple way:

    .. code:: bash
        
        python -m deeppavlov train <config_path> [-d]

    Dataset will be downloaded regardless of whether there was ``-d`` flag or
    not.

    To train on your own data you need to modify dataset reader path in the
    `train section doc <configuration.html#Train-config>`__. The data format is
    specified in the corresponding model doc page. 

There are even more actions you can perform with configs:

    .. code:: bash
        
        python -m deeppavlov <action> <config_path> [-d]

    * ``<action>`` can be
        * ``download`` to download model's data (same as ``-d``),
        * ``train`` to train the model on the data specified in the config file,
        * ``evaluate`` to calculate metrics on the same dataset,
        * ``interact`` to interact via CLI,
        * ``riseapi`` to run a REST API server (see :doc:`docs
          </integrations/rest_api>`),
        * ``risesocket`` to run a socket API server (see :doc:`docs
          </integrations/socket_api>`),
        * ``interactbot`` to run as a Telegram bot (see :doc:`docs
          </integrations/telegram>`),
        * ``interactmsbot`` to run a Miscrosoft Bot Framework server (see
          :doc:`docs </integrations/ms_bot>`),
        * ``predict`` to get prediction for samples from `stdin` or from
          `<file_path>` if ``-f <file_path>`` is specified.
    * ``<config_path>`` specifies path (or name) of model's config file
    * ``-d`` downloads required data


Python
~~~~~~

To get predictions from a model interactively through Python, run

    .. code:: python
        
        from deeppavlov import build_model

        model = build_model(<config_path>, download=True)

        # get predictions for 'input_text1', 'input_text2'
        model(['input_text1', 'input_text2'])

    * where ``download=True`` downloads required data from web -- pretrained model
      files and embeddings (optional),
    * ``<config_path>`` is path to the chosen model's config file (e.g.
      ``"deeppavlov/configs/ner/ner_ontonotes_bert_mult.json"``) or
      ``deeppavlov.configs`` attribute (e.g.
      ``deeppavlov.configs.ner.ner_ontonotes_bert_mult`` without quotation marks).

You can train it in the same simple way:

    .. code:: python
        
        from deeppavlov import train_model 

        model = train_model(<config_path>, download=True)

    * ``download=True`` downloads pretrained model, therefore the pretrained
      model will be, first, loaded and then train (optional).

    Dataset will be downloaded regardless of whether there was ``-d`` flag or
    not.

    To train on your own data you need to modify dataset reader path in the
    `train section doc <configuration.html#Train-config>`__. The data format is
    specified in the corresponding model doc page. 

You can also calculate metrics on the dataset specified in your config file:

    .. code:: python
        
        from deeppavlov import evaluate_model 

        model = evaluate_model(<config_path>, download=True)

There are also available integrations with various messengers, see
:doc:`Telegram Bot doc page </integrations/telegram>` and others in the
Integrations section for more info.

