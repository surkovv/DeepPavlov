=================================================
Open Domain Question Answering Skill on Wikipedia
=================================================

Task definition
===============

**Open Domain Question Answering (ODQA)** is a task to find an exact answer
to any question in **Wikipedia** articles. Thus, given only a question, the system outputs
the best answer it can find.
The default ODQA implementation takes a batch of queries as input and returns 5 answers sorted via their score.

Quick Start
===========

Before using the model make sure that all required packages are installed running the command:

.. code:: bash

    python -m deeppavlov install en_odqa_infer_wiki

Training (if you have your own data)

.. code:: python

    from deeppavlov import configs
    from deeppavlov.core.commands.train import train_evaluate_model_from_config

    train_evaluate_model_from_config(configs.doc_retrieval.en_ranker_tfidf_wiki, download=True)
    train_evaluate_model_from_config(configs.squad.multi_squad_noans, download=True)

Building

.. code:: python

    from deeppavlov import configs
    from deeppavlov.core.commands.infer import build_model

    odqa = build_model(configs.odqa.en_odqa_infer_wiki, load_trained=True)

Inference

.. code:: python

    result = odqa(['What is the name of Darth Vader\'s son?'])
    print(result)

Output:

::

    >> Luke Skywalker


Languages
=========

There are pretrained **ODQA** models for **English** and **Russian**
languages in :doc:`DeepPavlov </index/>`.

Models
======

The architecture of **ODQA** skill is modular and consists of two models,
a **ranker** and a **reader**. The **ranker** is based on `DrQA`_ proposed by Facebook Research
and the **reader** is based on `R-NET`_ proposed by Microsoft Research Asia
and its `implementation`_ by Wenxuan Zhou.

Running ODQA
============

.. note::

    About **24 GB of RAM** required.
    It is possible to run on a 16 GB machine, but than swap size should be at least 8 GB.

Training
--------

**ODQA ranker** and **ODQA reader** should be trained separately.
Read about training the **ranker** :ref:`here <ranker_training>`.
Read about training the **reader** in our separate :ref:`reader tutorial <reader_training>`.

Interacting
-----------

When interacting, the **ODQA** skill returns a plain answer to the user's
question.

Run the following to interact with **English ODQA**:

.. code:: bash

    python -m deeppavlov interact en_odqa_infer_wiki -d

Run the following to interact with **Russian ODQA**:

.. code:: bash

    python -m deeppavlov interact ru_odqa_infer_wiki -d

Configuration
=============

The **ODQA** configs suit only model inferring purposes. For training purposes use
the :ref:`ranker configs <ranker_training>` and the :ref:`reader configs <reader_training>`
accordingly.

Comparison
==========

Scores for **ODQA** skill:

+-----------------------------------------------------+----------------+---------------------+---------------------+
|                                                     |                | enwiki (2018-02-11) | enwiki (2016-12-21) |
|                                                     |                +----------+----------+-----------+---------+
| Model                                               | Dataset        |  F1      |   EM     |   F1      |   EM    |
+=====================================================+================+==========+==========+===========+=========+
|:config:`DeepPavlov <odqa/en_odqa_infer_wiki.json>`  |                |  35.89   |  29.21   |  37.83    |  31.26  |
+-----------------------------------------------------+ SQuAD (dev)    +----------+----------+-----------+---------+
|`DrQA`_                                              |                |   \-     |  \-      |   \-      |  27.1   |
+-----------------------------------------------------+                +----------+----------+-----------+---------+
|`R3`_                                                |                |   \-     |  \-      |   37.5    |  29.1   |
+-----------------------------------------------------+----------------+----------+----------+-----------+---------+


EM stands for "exact-match accuracy". Metrics are counted for top 5 documents returned by retrieval module.

References
==========

.. target-notes::

.. _`DrQA`: https://github.com/facebookresearch/DrQA/
.. _`R-NET`: https://www.microsoft.com/en-us/research/publication/mrc/
.. _`implementation`: https://github.com/HKUST-KnowComp/R-Net/
.. _`R3`: https://arxiv.org/abs/1709.00023


