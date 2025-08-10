# Copyright 2025 Cardy Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections.abc import Callable, Collection, Mapping, Set
from typing import Protocol

__all__ = ("CardSort", "CliqueHeuristic")


type CardSort[T] = Collection[Set[T]]


class Selector[T](Protocol):
    def select(self, collection: Collection[T]) -> T:
        ...



class CliqueHeuristic[K, T](Protocol):
    def __call__(
          self,
          d: float,
          candidates: Mapping[K, CardSort[T]],
          *,
          selector: Selector[T] = ...,
          distance: Callable[[T, T], float] = ...,
    ):
        ...
