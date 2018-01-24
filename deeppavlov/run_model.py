from deeppavlov.core.commands.train import train_model_from_config
from deeppavlov.core.commands.infer import interact_model
from deeppavlov.core.commands.utils import set_usr_dir, get_usr_dir

# HCN
# skills/hcn/config.json

# HCN_new
# skills/hcn_new/config.json

# Speller
# models/spellers/error_model/config_en.json
# models/spellers/error_model/config_ru.json
# models/spellers/error_model/config_ru_custom_vocab.json

# Intents classifier
# models/classifiers/intents/config.json

# NER
# models/ner/config.json

try:
    # PIPELINE_CONFIG_PATH = 'models/ner/ner_config.json'
    PIPELINE_CONFIG_PATH = 'skills/hcn_new/config.json'
    set_usr_dir(PIPELINE_CONFIG_PATH)
    train_model_from_config(PIPELINE_CONFIG_PATH)
    interact_model(PIPELINE_CONFIG_PATH)
# remove if usr_dir is empty:
finally:
    usr_dir = get_usr_dir()
    if not list(usr_dir.iterdir()):
        usr_dir.rmdir()
