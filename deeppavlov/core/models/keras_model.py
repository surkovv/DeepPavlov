from abc import abstractmethod
from pathlib import Path

import tensorflow as tf
import keras.metrics
import keras.optimizers
from typing import Dict
from overrides import overrides
from .tf_backend import TfModelMeta
from keras import backend as K
from keras.models import Model
from keras.layers import Dense, Input

from deeppavlov.core.models.trainable import Trainable
from deeppavlov.core.models.inferable import Inferable
from deeppavlov.core.common.attributes import check_attr_true, run_alt_meth_if_no_path
from deeppavlov.core.common.file import save_json, read_json
from deeppavlov.core.common.errors import ConfigError


class KerasModel(Trainable, Inferable, metaclass=TfModelMeta):
    """
    Class builds keras model
    """

    def __init__(self, opt: Dict, **kwargs):
        """
        Method initializes model using parameters from opt
        Args:
            opt: model parameters
            *args:
            **kwargs:
        """
        self.opt = opt
        ser_path = self.opt.get('ser_path', None)
        ser_dir = self.opt.get('ser_dir', 'intents')
        ser_file = self.opt.get('ser_file', 'intent_cnn')
        train_now = self.opt.get('train_now', False)

        super().__init__(ser_path=ser_path,
                         ser_dir=ser_dir,
                         ser_file=ser_file,
                         train_now=train_now)

        self.sess = self._config_session()
        K.set_session(self.sess)

    def _config_session(self):
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        config.gpu_options.visible_device_list = '0'
        return tf.Session(config=config)

    def init_model_from_scratch(self, model_name, optimizer_name,
                                lr, decay, loss_name, metrics_names=None, add_metrics_file=None,
                                loss_weights=None,
                                sample_weight_mode=None, weighted_metrics=None,
                                target_tensors=None):
        """
        Method initializes model from scratch with given params
        Args:
            model_name: name of model function described as a method of this class
            optimizer_name: name of optimizer from keras.optimizers
            lr: learning rate
            decay: learning rate decay
            loss_name: loss function name (from keras.losses)
            metrics_names: names of metrics (from keras.metrics) as one string
            add_metrics_file: file with additional metrics functions
            loss_weights: optional parameter as in keras.model.compile
            sample_weight_mode: optional parameter as in keras.model.compile
            weighted_metrics: optional parameter as in keras.model.compile
            target_tensors: optional parameter as in keras.model.compile

        Returns:
            compiled model with given network and learning parameters
        """
        print('[ Initializing model from scratch ]')

        model_func = getattr(self, model_name, None)
        if callable(model_func):
            model = model_func(params=self.opt)
        else:
            raise AttributeError("Model {} is not defined".format(model_name))

        optimizer_func = getattr(keras.optimizers, optimizer_name, None)
        if callable(optimizer_func):
            optimizer_ = optimizer_func(lr=lr, decay=decay)
        else:
            raise AttributeError("Optimizer {} is not callable".format(optimizer_name))

        loss_func = getattr(keras.losses, loss_name, None)
        if callable(loss_func):
            loss = loss_func
        else:
            raise AttributeError("Loss {} is not defined".format(loss_name))

        metrics_names = metrics_names.split(' ')
        metrics_funcs = []
        for i in range(len(metrics_names)):
            metrics_func = getattr(keras.metrics, metrics_names[i], None)
            if callable(metrics_func):
                metrics_funcs.append(metrics_func)
            else:
                metrics_func = getattr(add_metrics_file, metrics_names[i], None)
                if callable(metrics_func):
                    metrics_funcs.append(metrics_func)
                else:
                    raise AttributeError("Metric {} is not defined".format(metrics_names[i]))

        model.compile(optimizer=optimizer_,
                      loss=loss,
                      metrics=metrics_funcs,
                      loss_weights=loss_weights,  # None
                      sample_weight_mode=sample_weight_mode,  # None
                      weighted_metrics=weighted_metrics,  # None
                      target_tensors=target_tensors)  # None
        return model

    @overrides
    def load(self, model_name, optimizer_name,
             lr, decay, loss_name, metrics_names=None, add_metrics_file=None, loss_weights=None,
             sample_weight_mode=None, weighted_metrics=None, target_tensors=None):
        """
        Method initiliazes model from saved params and weights
        Args:
            model_name: name of model function described as a method of this class
            optimizer_name: name of optimizer from keras.optimizers
            lr: learning rate
            decay: learning rate decay
            loss_name: loss function name (from keras.losses)
            metrics_names: names of metrics (from keras.metrics) as one string
            add_metrics_file: file with additional metrics functions
            loss_weights: optional parameter as in keras.model.compile
            sample_weight_mode: optional parameter as in keras.model.compile
            weighted_metrics: optional parameter as in keras.model.compile
            target_tensors: optional parameter as in keras.model.compile

        Returns:
            model with loaded weights and network parameters from files
            but compiled with given learning parameters
        """
        if self.ser_path.is_dir():
            opt_path = "{}/{}_opt.json".format(self.ser_path, self._ser_file)
            weights_path = "{}/{}.h5".format(self.ser_path, self._ser_file)
        else:
            opt_path = "{}_opt.json".format(self.ser_path)
            weights_path = "{}.h5".format(self.ser_path)

        if Path(opt_path).exists() and Path(weights_path).exists():

            print('___Initializing model from saved___'
                  '\nModel weights file is %s.h5'
                  '\nNetwork parameters are from %s_opt.json' % (self._ser_file, self._ser_file))

            self.opt = read_json(opt_path)

            model_func = getattr(self, model_name, None)
            if callable(model_func):
                model = model_func(params=self.opt)
            else:
                raise AttributeError("Model {} is not defined".format(model_name))

            print("Loading weights from `{}{}`".format(self._ser_file, '.h5'))
            model.load_weights(weights_path)

            optimizer_func = getattr(keras.optimizers, optimizer_name, None)
            if callable(optimizer_func):
                optimizer_ = optimizer_func(lr=lr, decay=decay)
            else:
                raise AttributeError("Optimizer {} is not callable".format(optimizer_name))

            loss_func = getattr(keras.losses, loss_name, None)
            if callable(loss_func):
                loss = loss_func
            else:
                raise AttributeError("Loss {} is not defined".format(loss_name))

            metrics_names = metrics_names.split(' ')
            metrics_funcs = []
            for i in range(len(metrics_names)):
                metrics_func = getattr(keras.metrics, metrics_names[i], None)
                if callable(metrics_func):
                    metrics_funcs.append(metrics_func)
                else:
                    metrics_func = getattr(add_metrics_file, metrics_names[i], None)
                    if callable(metrics_func):
                        metrics_funcs.append(metrics_func)
                    else:
                        raise AttributeError("Metric {} is not defined".format(metrics_names[i]))

            model.compile(optimizer=optimizer_,
                          loss=loss,
                          metrics=metrics_funcs,
                          loss_weights=loss_weights,
                          sample_weight_mode=sample_weight_mode,
                          weighted_metrics=weighted_metrics,
                          target_tensors=target_tensors)
            return model
        else:
            return self.init_model_from_scratch(model_name, optimizer_name,
                                                lr, decay, loss_name, metrics_names=metrics_names,
                                                add_metrics_file=add_metrics_file,
                                                loss_weights=loss_weights,
                                                sample_weight_mode=sample_weight_mode,
                                                weighted_metrics=weighted_metrics,
                                                target_tensors=target_tensors)

    @abstractmethod
    def train_on_batch(self, batch):
        """
        Method trains the model on a single batch of data
        Args:
            batch: tuple of (x,y) where x, y - lists of samples and their labels

        Returns:
            metrics values on a given batch
        """
        pass

    @abstractmethod
    @check_attr_true('train_now')
    def train(self, dataset, *args):
        """
        Method trains the model on a given data as a single batch
        Args:
            dataset: dataset instance

        Returns:
            metrics values on a given data
        """
        pass

    @overrides
    def save(self):
        """
        Method saves the model parameters into <<fname>>_opt.json (or <<ser_file>>_opt.json)
        and model weights into <<fname>>.h5 (or <<ser_file>>.h5)
        Args:
            fname: file_path to save model. If not explicitly given seld.opt["ser_file"] will be used

        Returns:
            nothing
        """
        if self.ser_path.is_dir():
            opt_path = "{}/{}_opt.json".format(self.ser_path, self._ser_file)
            weights_path = "{}/{}.h5".format(self.ser_path, self._ser_file)
        else:
            opt_path = "{}_opt.json".format(self.ser_path)
            weights_path = "{}.h5".format(self.ser_path)
        print("[ saving model: {} ]".format(opt_path))
        self.model_path.mkdir(parents=True, exist_ok=True)
        self.model.save_weights(weights_path)

        save_json(self.opt, opt_path)

        return True

    def mlp(self, opt):
        """
        Example of model function
        Build the un-compiled multilayer perceptron model
        Args:
            opt: dictionary of parameters

        Returns:
            un-compiled Keras model
        """
        inp = Input(shape=opt['inp_shape'])
        output = inp
        for i in range(opt['n_layers']):
            output = Dense(opt['layer_size'], activation='relu')(output)
        output = Dense(1, activation='softmax')(output)
        model = Model(inputs=inp, outputs=output)
        return model

    @abstractmethod
    def reset(self):
        pass
