from deeppavlov.common.file import read_json
from deeppavlov.common.registry import _REGISTRY
from deeppavlov.common.params import from_params
from deeppavlov.models.trainable import Trainable

from deeppavlov.commands.utils import set_vocab_path, build_agent_from_config, set_usr_dir, USR_DIR


# TODO pass paths to local model configs to agent config.

def get_data(skill_config, dataset_config, vocab_path):
    dataset_name = dataset_config['name']
    data_path = skill_config['data_path']

    data_reader = from_params(_REGISTRY[dataset_name], dataset_config)
    data = data_reader.read(data_path)
    data_reader.save_vocab(data, vocab_path)
    return data


def train_agent_models(config_path: str):
    set_usr_dir(config_path, USR_DIR)
    a = build_agent_from_config(config_path)

    for skill_config in a.skill_configs:
        vocab_path = set_vocab_path()
        model_config = skill_config['model']
        model_name = model_config['name']

        if issubclass(_REGISTRY[model_name], Trainable):
            data = get_data(skill_config, skill_config['dataset_reader'], vocab_path)

            model = from_params(_REGISTRY[model_name], model_config, vocab_path=vocab_path)

            # TODO if has TFModel as attribute
            # TODO is model.train_now
            num_epochs = skill_config['num_epochs']
            num_tr_data = skill_config['num_train_instances']
            model.train(data, num_epochs, num_tr_data)
        else:
            print('Model {} is not an instance of Trainable, skip training.'.format(model_name))
            pass
            # raise NotImplementedError("This model is not an instance of TFModel class."
            #                           "Only TFModel instances can train for now.")


def train_model_from_config(config_path: str, usr_dir_name=USR_DIR):
    # make a serialization user dir
    usr_dir_path = set_usr_dir(config_path, usr_dir_name)

    config = read_json(config_path)
    vocab_path = usr_dir_path.joinpath('vocab.txt')

    data = get_data(config, config['dataset_reader'], vocab_path)

    model_config = config['model']
    model_name = model_config['name']
    model = from_params(_REGISTRY[model_name], model_config, vocab_path=vocab_path)

    num_epochs = config['num_epochs']
    num_tr_data = config['num_train_instances']

    ####### Train
    # TODO do batching in the train script.
    model.train(data, num_epochs, num_tr_data)

    # The result is a saved to user_dir trained model.
