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
import numpy as np

def batch_generator(
        X, Y, batch_size: int, shuffle: bool = True,
        return_smaller_last_batch: bool = True):
    indices = np.arange(len(X))
    if shuffle:
        np.random.shuffle(indices)
    batch = []
    for i in indices:
        batch.append(i)
        if len(batch) == batch_size:
            yield X[batch], Y[batch]
            batch = []
    if return_smaller_last_batch and batch:
        yield X[batch], Y[batch]
