from pathlib import Path

from deeppavlov.common import paths
from deeppavlov.common.file import read_json
from deeppavlov.common.params import from_params
from deeppavlov.common.registry import _REGISTRY


def get_model_from_config(config_path, usr_dir_name='USR_DIR'):
    config = read_json(config_path)

    # make a serialization user dir
    root_ = Path(config_path).resolve().parent
    usr_dir_path = root_.joinpath(usr_dir_name)

    paths.USR_PATH = usr_dir_path

    model_config = config['model']
    model_name = model_config['name']
    # NOTE: vocab_path is removed! Does every model need vocab_path as input argument?
    model = from_params(_REGISTRY[model_name], model_config)
    return model


def interact(config_path):
    model = get_model_from_config(config_path)
    model.reset()
    while True:
        model.interact()


