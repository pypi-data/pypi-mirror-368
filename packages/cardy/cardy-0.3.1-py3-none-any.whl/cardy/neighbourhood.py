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

from collections.abc import Mapping, Callable

from .distance import distance as edit_distance
from .types import CardSort

__all__ = ("neighbourhood",)


def neighbourhood[K, T](
      d: float,
      probe: CardSort[T],
      sorts: Mapping[K, CardSort[T]],
      *,
      distance: Callable[[T, T], float] = edit_distance,
) -> set[K]:
    """
    Returns the d-neighbourhood of the given probe sort in the sorts iterable.

    The probe sort does not need to be one of the given sorts and will not be
    included in the result if it is not.

    :param d: The max distance neighbourhood elements and the probe
    :param probe: The sort at the centre of the neighbourhood
    :param sorts: A collection of sorts to search for the neighbourhood in
    :param distance: An edit distance function
    :return: The d-neighbourhood of the given probe
    """
    return {key for key, sort in sorts.items() if distance(probe, sort) <= d}
