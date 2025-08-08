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
import tensorflow.keras as keras
import matplotlib.pyplot as plt

class PlotLosses(keras.callbacks.Callback):
    def __init__(self, train_metric: str = 'loss', val_metric: str = 'val_loss'):
        self.train_metric = train_metric
        self.val_metric = val_metric

    def on_train_begin(self, logs={}):
        self.i = 0
        self.x = []
        self.losses = []
        self.val_losses = []

        self.fig = plt.figure()

        self.logs = []

    def on_epoch_end(self, epoch, logs={}):

        self.logs.append(logs)
        self.x.append(self.i)
        self.losses.append(logs.get(self.train_metric))
        self.val_losses.append(logs.get(self.val_metric))
        self.i += 1

        plt.cla()
        plt.plot(self.x, self.losses, label=self.train_metric)
        plt.plot(self.x, self.val_losses, label=self.val_metric)
        plt.legend()
        plt.gcf().canvas.draw_idle()
        plt.gcf().canvas.start_event_loop(0.3)
        if self.i == 1:
            plt.show(block=False)