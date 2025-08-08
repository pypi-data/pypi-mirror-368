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
from typing import Iterable

import time
from random import Random
import numpy as np

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Concatenate, Reshape
from tensorflow.keras.layers import Dense, LSTM, BatchNormalization
from tensorflow.keras.optimizers import Nadam, Adam, SGD, Adagrad
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from prolothar_common.models.eventlog import EventLog, Trace
from prolothar_rule_mining.models.event_flow_graph import EventFlowGraph

from prolothar_rule_mining.rule_miner.next_event_prediction.eventlog_iterator import eventlog_iterator


class DeepGenerator:
    """
    uses the architecture of https://github.com/AdaptiveBProcess/GenerativeLSTM
    for next event prediction
    """

    def __init__(self, categorical_attribute_names: Iterable[str],
                 numerical_attribute_names: Iterable[str],
                 activity_embedding_size: int = 4,
                 trace_features_embedding_size: int = 4,
                 event_features_embedding_size: int = 4,
                 layer_size: int = 10,
                 batch_size: int = 32,
                 nr_of_epochs: int = 50,
                 patience: int = 50,
                 random_seed: int = None):
        self.__categorical_attribute_names = set(categorical_attribute_names)
        self.__numerical_attribute_names = set(numerical_attribute_names)
        self.__activity_embedding_size = activity_embedding_size
        self.__trace_features_embedding_size = trace_features_embedding_size
        self.__event_features_embedding_size = event_features_embedding_size
        self.__layer_size = layer_size
        self.__batch_size = batch_size
        self.__nr_of_epochs = nr_of_epochs
        self.__patience = patience
        if random_seed is not None:
            self.__random_seed = random_seed
        else:
            self.__random_seed = time.time()

        self.__activity_to_int = None
        self.__int_to_activity = None
        self.__max_sequence_length = None
        self.__attribute_category_int_dict = {}
        self.__attribute_min_max_dict = {}
        self.__model = None
        self.__trace_categorical_feature_names = None
        self.__trace_numerical_feature_names = None
        self.__event_categorical_feature_names = None
        self.__event_numerical_feature_names = None
        self.__used_input_keys = None

    def __transform_eventlog(self, eventlog: EventLog) -> np.ndarray:
        self.__activity_to_int = {
            activity: i+1 for i,activity in enumerate(eventlog.compute_activity_set())
        }
        self.__activity_to_int[EventFlowGraph().source.event] = len(self.__activity_to_int)
        self.__activity_to_int[EventFlowGraph().sink.event] = len(self.__activity_to_int)
        self.__int_to_activity = {
            i: activity for activity, i in self.__activity_to_int.items()
        }
        self.__max_sequence_length = max(len(trace) for trace in eventlog)

        self.__learn_features(eventlog)

        prefixes = []
        next_activities = []
        trace_categorical_features = []
        trace_numerical_features = []
        event_categorical_features = []
        event_numerical_features = []

        for trace, next_activity in eventlog_iterator(eventlog):
            prefixes.append(self.__trace_to_activity_vector(trace))
            next_activities.append(self.__activity_to_one_hot_vector(next_activity))
            self.__append_trace_features(
                trace_categorical_features, trace_numerical_features, trace)
            self.__append_event_features(
                event_categorical_features, event_numerical_features, trace)

        return (
            np.array(prefixes), np.array(next_activities),
            np.array(trace_categorical_features), np.array(trace_numerical_features),
            np.array(event_categorical_features), np.array(event_numerical_features)
        )

    def __activity_to_one_hot_vector(self, activity: str) -> np.ndarray:
        vector = [0] * len(self.__activity_to_int)
        vector[self.__activity_to_int[activity] - 1] = 1
        return np.array(vector)

    def __trace_to_activity_vector(self, trace: Trace):
        return np.array([
            [self.__activity_to_int.get(trace.events[i].activity_name, 0)]
            if i < len(trace) else [0]
            for i in range(self.__max_sequence_length + 1)
        ])

    def __append_trace_features(
            self, trace_categorical_features, trace_numerical_features, trace: Trace):
        trace_categorical_features.append([])
        for attribute_name in self.__trace_categorical_feature_names:
            trace_categorical_features[-1].append(
                self.__category_to_int(attribute_name, trace.attributes[attribute_name]))
        trace_numerical_features.append([])
        for attribute_name in self.__trace_numerical_feature_names:
            trace_numerical_features[-1].append(
                self.__normalize(attribute_name, trace.attributes[attribute_name]))
        trace_categorical_features[-1] = [trace_categorical_features[-1]] * (self.__max_sequence_length + 1)
        trace_numerical_features[-1] = [trace_numerical_features[-1]] * (self.__max_sequence_length + 1)
        trace_categorical_features[-1] = trace_categorical_features[-1][:self.__max_sequence_length + 1]
        trace_numerical_features[-1] = trace_numerical_features[-1][:self.__max_sequence_length + 1]

    def __append_event_features(
            self, event_categorical_features, event_numerical_features, trace: Trace):
        categorial_features = []
        numerical_features = []
        for event in trace.events:
            categorial_features.append([])
            for attribute_name in self.__event_categorical_feature_names:
                categorial_features[-1].append(
                    self.__category_to_int(attribute_name, event.attributes.get(attribute_name, None)))
            numerical_features.append([])
            for attribute_name in self.__event_numerical_feature_names:
                numerical_features[-1].append(
                    self.__normalize(attribute_name, event.attributes.get(attribute_name, None)))
        for _ in range(self.__max_sequence_length + 1 - len(trace)):
            categorial_features.append([0] * len(self.__event_categorical_feature_names))
            numerical_features.append([0] * len(self.__event_numerical_feature_names))
        categorial_features = categorial_features[:self.__max_sequence_length + 1]
        event_numerical_features = event_numerical_features[:self.__max_sequence_length + 1]
        event_categorical_features.append(categorial_features)
        event_numerical_features.append(numerical_features)

    def __category_to_int(self, attribute_name, category):
        return self.__attribute_category_int_dict[attribute_name].get(category, 0)

    def __normalize(self, attribute_name, value) -> float:
        if value is None:
            return 0
        min_value, max_value = self.__attribute_min_max_dict[attribute_name]
        return (value - min_value) / (max_value - min_value)

    def __learn_features(
            self, eventlog: EventLog):
        trace_categorical_feature_names = set()
        trace_numerical_feature_names = set()
        event_categorical_feature_names = set()
        event_numerical_feature_names = set()
        for trace in eventlog:
            for attribute_name, attribute_value in trace.attributes.items():
                if attribute_name in self.__categorical_attribute_names:
                    trace_categorical_feature_names.add(attribute_name)
                    self.__learn_category_to_int(attribute_name, attribute_value)
                elif attribute_name in self.__numerical_attribute_names:
                    event_numerical_feature_names.add(attribute_name)
                    self.__learn_scaler(attribute_name, attribute_value)
            for event in trace.events:
                for attribute_name, attribute_value in event.attributes.items():
                    if attribute_name in self.__categorical_attribute_names:
                        event_categorical_feature_names.add(attribute_name)
                        self.__learn_category_to_int(attribute_name, attribute_value)
                    elif attribute_name in self.__numerical_attribute_names:
                        event_numerical_feature_names.add(attribute_name)
                        self.__learn_scaler(attribute_name, attribute_value)
        self.__trace_categorical_feature_names = list(trace_categorical_feature_names)
        self.__trace_numerical_feature_names = list(trace_numerical_feature_names)
        self.__event_categorical_feature_names = list(event_categorical_feature_names)
        self.__event_numerical_feature_names = list(event_numerical_feature_names)

    def __learn_category_to_int(self, attribute_name: str, attribute_value):
        category_to_int_dict = self.__attribute_category_int_dict.get(attribute_name, None)
        if category_to_int_dict is None:
            category_to_int_dict = {}
            self.__attribute_category_int_dict[attribute_name] = category_to_int_dict

        integer = category_to_int_dict.get(attribute_value, None)
        if integer is None:
            category_to_int_dict[attribute_value] = len(category_to_int_dict)

    def __learn_scaler(self, attribute_name: str, attribute_value):
        min_value, max_value = self.__attribute_min_max_dict.get(
            attribute_name, (float('inf'), float('-inf')))
        self.__attribute_min_max_dict[attribute_name] = (
            min(min_value, attribute_value), max(max_value, attribute_value)
        )

    def __create_model(
            self, prefixes,
            trace_categorical_features, trace_numerical_features,
            event_categorical_features, event_numerical_features) -> Model:
        activities_input = Input(shape=(prefixes.shape[1], ), name='activities_input')
        activity_embedding = Embedding(
            len(self.__activity_to_int),
            self.__activity_embedding_size,
            input_length=prefixes.shape[1],
            name='activity_embedding')(activities_input)

        input_layers = [activity_embedding]
        inputs = [activities_input]
        if trace_categorical_features.shape[2] > 0:
            categorical_trace_input = self.__create_categorical_trace_input(
                trace_categorical_features)
            inputs.append(categorical_trace_input)
            input_layers.append(self.__create_trace_features_embedding(
                trace_categorical_features, categorical_trace_input))
        if len(trace_numerical_features) >= 3 and trace_numerical_features.shape[2] > 0:
            numerical_trace_input = Input(
                shape=(
                    trace_numerical_features.shape[1],
                    trace_numerical_features.shape[2],
                ),
                name='numerical_trace_input'
            )
            input_layers.append(numerical_trace_input)
            inputs.append(numerical_trace_input)
        if event_categorical_features.shape[2] > 0:
            categorical_event_input = self.__create_categorical_event_input(
                event_categorical_features)
            input_layers.append(self.__create_event_features_embedding(
                event_categorical_features, categorical_event_input))
            inputs.append(categorical_event_input)
        if len(event_numerical_features) >= 3 and event_numerical_features.shape[2] > 0:
            numerical_event_input = Input(
                shape=(
                    event_numerical_features.shape[1],
                    event_numerical_features.shape[2],
                ),
                name='numerical_event_input'
            )
            input_layers.append(numerical_event_input)
            inputs.append(numerical_event_input)

        merged_input = Concatenate(name='concatenated_input', axis=2)(input_layers)

        layer_one = LSTM(self.__layer_size,
                kernel_initializer='glorot_uniform',
                return_sequences=True,
                dropout=0.2)(merged_input)

        batch_normalization_layer_one = BatchNormalization()(layer_one)

        layer_activity_prediction = LSTM(self.__layer_size,
                kernel_initializer='glorot_uniform',
                return_sequences=False,
                dropout=0.2)(batch_normalization_layer_one)

        activity_output = Dense(len(self.__activity_to_int),
                       activation='softmax',
                       kernel_initializer='glorot_uniform',
                       name='activity_output')(layer_activity_prediction)

        model = Model(
            inputs=inputs,
            outputs=[activity_output]
        )

        model.compile(
            loss={'activity_output': 'categorical_crossentropy'},
            optimizer=Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, amsgrad=False))

        return model

    def __create_categorical_trace_input(self, trace_categorical_features) -> Input:
        return Input(
            shape=(
                trace_categorical_features.shape[1],
                trace_categorical_features.shape[2],
            ),
            name='categorical_trace_input'
        )

    def __create_trace_features_embedding(
            self, trace_categorical_features, categorical_trace_input):
        trace_features_embedding = Embedding(
            128,
            self.__trace_features_embedding_size,
            input_length=trace_categorical_features.shape[1],
            name='trace_features_embedding')(categorical_trace_input)
        return Reshape((
            trace_categorical_features.shape[1],
            trace_categorical_features.shape[2] * self.__trace_features_embedding_size
        ))(trace_features_embedding)

    def __create_categorical_event_input(self, event_categorical_features) -> Input:
        return Input(
            shape=(
                event_categorical_features.shape[1],
                event_categorical_features.shape[2],
            ),
            name='categorical_event_input'
        )

    def __create_event_features_embedding(
            self, event_categorical_features, categorical_event_input):
        event_features_embedding = Embedding(
            128,
            self.__event_features_embedding_size,
            input_length=event_categorical_features.shape[1],
            name='event_features_embedding')(categorical_event_input)
        return Reshape((
            event_categorical_features.shape[1],
            event_categorical_features.shape[2] * self.__event_features_embedding_size
        ))(event_features_embedding)

    def train(self, eventlog: EventLog):
        prefixes, next_activities, trace_categorical_features,\
            trace_numerical_features, event_categorical_features, \
                event_numerical_features = self.__transform_eventlog(eventlog)

        model = self.__create_model(
            prefixes,
            trace_categorical_features, trace_numerical_features,
            event_categorical_features, event_numerical_features)

        Random(self.__random_seed).shuffle(prefixes)
        Random(self.__random_seed).shuffle(next_activities)
        Random(self.__random_seed).shuffle(trace_categorical_features)
        Random(self.__random_seed).shuffle(trace_numerical_features)
        Random(self.__random_seed).shuffle(event_categorical_features)
        Random(self.__random_seed).shuffle(event_numerical_features)

        val_split_idx = int(len(prefixes) * 0.2)
        train_prefixes = prefixes[val_split_idx:]
        train_trace_categorical_features = trace_categorical_features[val_split_idx:]
        train_trace_numerical_features = trace_numerical_features[val_split_idx:]
        train_event_categorical_features = event_categorical_features[val_split_idx:]
        train_event_numerical_features = event_numerical_features[val_split_idx:]
        train_next_activities = next_activities[val_split_idx:]
        val_prefixes = prefixes[:val_split_idx]
        val_trace_categorical_features = trace_categorical_features[:val_split_idx]
        val_trace_numerical_features = trace_numerical_features[:val_split_idx]
        val_event_categorical_features = event_categorical_features[:val_split_idx]
        val_event_numerical_features = event_numerical_features[:val_split_idx]
        val_next_activities = next_activities[:val_split_idx]

        early_stopping = EarlyStopping(monitor='val_loss', patience=self.__patience)

        lr_reducer = ReduceLROnPlateau(monitor='val_loss',
                                       factor=0.5,
                                       patience=10,
                                       verbose=0,
                                       mode='auto',
                                       min_delta=0.0001,
                                       cooldown=0,
                                       min_lr=0)

        training_input = {
            key: data for key, data in {
                'activities_input': train_prefixes,
                'categorical_trace_input': train_trace_categorical_features,
                'numerical_trace_input': train_trace_numerical_features,
                'categorical_event_input': train_event_categorical_features,
                'numerical_event_input': train_event_numerical_features
            }.items() if len(data) >= 3 and data.shape[2] > 0
        }
        self.__used_input_keys = training_input.keys()
        validation_input = {
            key: data for key, data in {
                'activities_input': val_prefixes,
                'categorical_trace_input': val_trace_categorical_features,
                'numerical_trace_input': val_trace_numerical_features,
                'categorical_event_input': val_event_categorical_features,
                'numerical_event_input': val_event_numerical_features
            }.items() if len(data) >= 3 and data.shape[2] > 0
        }

        model.fit(
            training_input,
            {
                'activity_output': train_next_activities,
            },
            validation_data=(
                validation_input,
                {
                    'activity_output': val_next_activities,
                },
            ),
            verbose=2,
            callbacks=[early_stopping, lr_reducer],
            batch_size=self.__batch_size,
            epochs=self.__nr_of_epochs)

        self.__model = model

    def predict(self, trace: Trace) -> str:
        activities_input = np.array([self.__trace_to_activity_vector(trace)])

        trace_categorical_features = []
        trace_numerical_features = []
        self.__append_trace_features(
            trace_categorical_features, trace_numerical_features, trace)
        trace_categorical_features = np.array(trace_categorical_features)
        trace_numerical_features = np.array(trace_numerical_features)

        event_categorical_features = []
        event_numerical_features = []
        self.__append_event_features(
            event_categorical_features, event_numerical_features, trace)
        event_categorical_features = np.array(event_categorical_features)
        event_numerical_features = np.array(event_numerical_features)

        inputs = [activities_input]
        if 'categorical_trace_input' in self.__used_input_keys:
            inputs.append(trace_categorical_features)
        if 'numerical_trace_input' in self.__used_input_keys:
            inputs.append(trace_numerical_features)
        if 'categorical_event_input' in self.__used_input_keys:
            inputs.append(event_categorical_features)
        if 'numerical_event_input' in self.__used_input_keys:
            inputs.append(event_numerical_features)

        prediction = self.__model(inputs, training=False)
        return self.__int_to_activity[np.argmax(prediction) + 1]

