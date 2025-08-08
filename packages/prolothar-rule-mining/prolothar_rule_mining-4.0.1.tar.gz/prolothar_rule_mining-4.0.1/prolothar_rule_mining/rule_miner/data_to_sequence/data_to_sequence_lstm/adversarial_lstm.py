'''
    This file is part of Prolothar-Rule-Mining (More Info: https://github.com/shs-it/prolothar-rule-mining).

    Prolothar-Rule-Mining is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Prolothar-Rule-Mining is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Prolothar-Rule-Mining. If not, see <https://www.gnu.org/licenses/>.
'''
from typing import List, Tuple
import os
from collections import namedtuple
import tempfile

import numpy as np
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Input, RepeatVector, LSTM, Concatenate, Dense

from prolothar_common.models.dataset import TargetSequenceDataset
from prolothar_common.models.dataset.instance import TargetSequenceInstance

from prolothar_rule_mining.rule_miner.data_to_sequence.data_to_sequence_lstm.base_lstm import BaseLstm
from prolothar_rule_mining.rule_miner.data_to_sequence.data_to_sequence_lstm.batch_generator import batch_generator
from prolothar_rule_mining.rule_miner.data_to_sequence.data_to_sequence_lstm.callbacks import PlotLosses

TrainingHistory = namedtuple('TrainingHistory', ['history'])

class DataToSequenceAdversarialLstm(BaseLstm):
    """
    idea based on the paper
    "A Deep Adversarial Model for Suffix and Remaining Time Prediction of
    Event Sequences" by Taymouri et al.
    """

    def __init__(self, train_dataset: TargetSequenceDataset, end_of_sequence_symbol=-1,
                 epochs=200, early_stopping=True, patience=20,
                 verbose: bool = True, random_seed: int = None,
                 round_limit: int = None,
                 activation_candidates: List[str] = ['tanh', 'relu', 'elu'],
                 optimizer_candidates: List[str] = ['Adamax', 'Adam', 'Nadam', 'Ftrl'],
                 batch_size_candidates: List[int] = [32, 64, 128, 256],
                 dropout_candidates: List[int] = [0.0, 0.1, 0.2, 0.3, 0.4],
                 layers_candidates: List[Tuple[int]] = [(8,8), (16,16), (32, 32), (64, 64)],
                 generator_exclusive_epochs: int = 5):
        super().__init__(
            train_dataset, end_of_sequence_symbol=end_of_sequence_symbol,
            random_seed=random_seed, round_limit=round_limit,
            activation_candidates=activation_candidates,
            optimizer_candidates=optimizer_candidates,
            batch_size_candidates=batch_size_candidates,
            dropout_candidates=dropout_candidates,
            layers_candidates=layers_candidates
        )

        self.__epochs = epochs
        self.__early_stopping = early_stopping
        self.__patience = patience
        self.__verbose = verbose
        self.__generator_exclusive_epochs = max(1, generator_exclusive_epochs - 1)

    def _create_training_function(self):
        def _data_to_sequence_model(X_train, Y_train, X_val, Y_val, params):
            with tempfile.TemporaryDirectory() as tempdir:
                best_model_path = os.path.join(tempdir, 'best_model')
                generator, feature_input, generator_output_layer \
                    = create_generator(X_train, Y_train, params)
                discriminator, discriminator_sequence_model_part_list, discriminator_classificator \
                    = create_discriminator(X_train, Y_train, params)

                sequence_model_part = generator_output_layer
                for lstm_layer in discriminator_sequence_model_part_list:
                    sequence_model_part = lstm_layer(sequence_model_part)
                adverserial_model = discriminator_classificator(Concatenate(axis=1)([
                    sequence_model_part,
                    feature_input
                ]))
                adverserial_model = Model(
                    inputs=[feature_input], outputs=[adverserial_model]
                )
                adverserial_model.compile(loss='binary_crossentropy', optimizer=params['optimizer'])

                train_history = TrainingHistory({
                    'train_loss_generator': [],
                    'val_loss_generator': [],
                    'train_loss_discriminator': [],
                    'train_loss_adversarial': [],
                    'accuracy': [],
                    'val_accuracy': []
                })

                best_val_accuracy = -1
                best_epoch = -1
                callbacks = []
                if self.__verbose:
                    callbacks.append(PlotLosses(
                        train_metric='train_accuracy', val_metric='val_accuracy'))
                for callback in callbacks:
                    callback.on_train_begin()

                for epoch in range(self.__epochs):
                    nr_of_batches = 0
                    train_accuracy = 0
                    generator_loss = 0
                    discriminator_loss = 0
                    adversarial_loss = 0
                    for batch_X, batch_Y in batch_generator(
                            X_train, Y_train, params['batch_size'], return_smaller_last_batch=True):
                        loss, accuracy = generator.train_on_batch({'features': batch_X}, batch_Y)
                        train_accuracy += accuracy
                        generator_loss += loss
                        nr_of_batches += 1
                        train_history.history['train_loss_generator'].append(loss)
                        train_history.history['accuracy'].append(accuracy)

                        if epoch % self.__generator_exclusive_epochs == 0:
                            batch_Y_predicted = generator.predict_on_batch(batch_X)
                            discriminator_Y = np.ones([len(batch_X) * 2, 1])
                            discriminator_Y[:len(batch_Y_predicted)] = 0
                            loss = discriminator.train_on_batch(
                                {
                                    'features': np.repeat(batch_X, 2, axis=0),
                                    'sequence': np.concatenate((batch_Y_predicted, batch_Y))},
                                discriminator_Y)
                            discriminator_loss += loss
                            train_history.history['train_loss_discriminator'].append(loss)

                            loss = adverserial_model.train_on_batch({'features': batch_X}, np.ones([len(batch_X), 1]))
                            adversarial_loss += loss
                            train_history.history['train_loss_adversarial'].append(loss)
                    train_accuracy /= nr_of_batches
                    discriminator_loss /= nr_of_batches
                    adversarial_loss /= nr_of_batches
                    generator_loss /= nr_of_batches

                    val_loss, val_accuracy = generator.evaluate(X_val, Y_val)
                    train_history.history['val_loss_generator'].append(val_loss)
                    train_history.history['val_accuracy'].append(accuracy)
                    if self.__verbose:
                        print(f'epoch {epoch+1} of {self.__epochs}')
                        print(f'val_accuracy: {val_accuracy:.2f}')
                        print(f'generator_loss: {generator_loss:.2f}')
                        if epoch % self.__generator_exclusive_epochs == 0:
                            print(f'discriminator_loss: {discriminator_loss:.2f}')
                            print(f'adversarial_loss: {adversarial_loss:.2f}')
                    if val_accuracy > best_val_accuracy:
                        best_val_accuracy = val_accuracy
                        best_epoch = epoch
                        generator.save_weights(best_model_path)
                    elif self.__early_stopping and epoch - best_epoch > self.__patience:
                        break
                    for callback in callbacks:
                        callback.on_epoch_end(epoch, {
                            'train_accuracy': train_accuracy,
                            'val_accuracy': val_accuracy})

                generator.load_weights(best_model_path)
                return train_history, generator
        return _data_to_sequence_model

def create_generator(X_train, Y_train, params):
    feature_input = Input(shape=(X_train.shape[1],), name='features')
    model = RepeatVector(Y_train.shape[1])(feature_input)
    for i in params['layers']:
        model = LSTM(
            i, return_sequences=True, activation=params['activation'],
            dropout=params['dropout'])(model)
    model = Dense(Y_train.shape[2], activation='softmax')(model)
    output = model

    model = Model(inputs=[feature_input], outputs=[output])
    model.compile(loss='categorical_crossentropy', optimizer=params['optimizer'],
                  metrics=['accuracy'])

    return model, feature_input, output

def create_discriminator(X_train, Y_train, params):
    sequence_input = Input(
        shape=(Y_train.shape[1], Y_train.shape[2],),
        name='sequence'
    )
    sequence_model_part = sequence_input
    sequence_model_part_list = []
    for i in params['layers'][:-1]:
        sequence_model_part_list.append(LSTM(
            i, return_sequences=True, activation=params['activation'],
            dropout=params['dropout']))
        sequence_model_part = sequence_model_part_list[-1](sequence_model_part)
    sequence_model_part_list.append(LSTM(
        params['layers'][-1], return_sequences=False, activation=params['activation'],
        dropout=params['dropout']))
    sequence_model_part = sequence_model_part_list[-1](sequence_model_part)

    features_input = Input(shape=(X_train.shape[1],), name='features')

    combined_discriminator_input = Concatenate(
        name='concatenated_input', axis=1)([features_input, sequence_model_part])

    classificator = Dense(1, activation='sigmoid')
    output = classificator(combined_discriminator_input)

    model = Model(inputs=[features_input, sequence_input], outputs=[output])
    model.compile(loss='binary_crossentropy', optimizer=params['optimizer'])

    return model, sequence_model_part_list, classificator
