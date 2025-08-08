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

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import RepeatVector, LSTM, GRU, Dense
from tensorflow.keras.callbacks import EarlyStopping

from prolothar_common.models.dataset import TargetSequenceDataset

from prolothar_rule_mining.rule_miner.data_to_sequence.data_to_sequence_lstm.base_lstm import BaseLstm
from prolothar_rule_mining.rule_miner.data_to_sequence.data_to_sequence_lstm.callbacks import PlotLosses

class DataToSequenceLstm(BaseLstm):

    def __init__(self, train_dataset: TargetSequenceDataset, end_of_sequence_symbol=-1,
                 epochs=200, early_stopping=True, patience=20, min_delta: float = 0,
                 verbose: bool = True, random_seed: int = None,
                 round_limit: int = None,
                 activation_candidates: List[str] = ['tanh', 'relu', 'elu'],
                 optimizer_candidates: List[str] = ['Adamax', 'Adam', 'Nadam', 'Ftrl'],
                 batch_size_candidates: List[int] = [32, 64, 128, 256],
                 dropout_candidates: List[int] = [0.0, 0.1, 0.2, 0.3, 0.4],
                 layers_candidates: List[Tuple[int]] = [(8,8), (16,16), (32, 32), (64, 64)],
                 recurrent_layer: str = 'LSTM'):
        super().__init__(
            train_dataset, end_of_sequence_symbol=end_of_sequence_symbol,
            random_seed=random_seed, round_limit=round_limit,
            activation_candidates=activation_candidates,
            optimizer_candidates=optimizer_candidates,
            batch_size_candidates=batch_size_candidates,
            dropout_candidates=dropout_candidates,
            layers_candidates=layers_candidates
        )

        self.__early_stopping = early_stopping
        self.__patience = patience
        self.__verbose = verbose
        self.__min_delta = min_delta

        if recurrent_layer == 'LSTM':
            self.__recurrent_layer = LSTM
        elif recurrent_layer == 'GRU':
            self.__recurrent_layer = GRU
        else:
            raise ValueError('unknown recurrent layer type "%s"' % recurrent_layer)

        self.__epochs = epochs

    def _create_training_function(self):
        def _data_to_sequence_model(X_train, Y_train, X_val, Y_val, params):
            model = Sequential()
            model.add(RepeatVector(Y_train.shape[1], input_shape=(X_train.shape[1],)))
            for i in params['layers']:
                model.add(self.__recurrent_layer(
                    i, return_sequences=True, activation=params['activation'],
                    dropout=params['dropout']))
            model.add(Dense(
                Y_train.shape[2], activation='softmax'))

            model.compile(loss='categorical_crossentropy', optimizer=params['optimizer'],
                          metrics=['categorical_crossentropy', 'accuracy'])

            callbacks = []
            if self.__verbose:
                callbacks.append(PlotLosses())

            if self.__early_stopping:
                early_stopping_monitor = EarlyStopping(
                    monitor='val_loss', min_delta=self.__min_delta,
                    patience=self.__patience, verbose=self.__verbose,
                    mode='auto', restore_best_weights=True)
                callbacks.append(early_stopping_monitor)

            train_history = model.fit(
                X_train, Y_train, epochs=self.__epochs, validation_data=(X_val, Y_val),
                batch_size=params['batch_size'], verbose=self.__verbose,
                callbacks=callbacks, shuffle=True)

            return train_history, model
        return _data_to_sequence_model

