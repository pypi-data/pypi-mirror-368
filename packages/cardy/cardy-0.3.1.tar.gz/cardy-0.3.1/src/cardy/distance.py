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

from munkres import Munkres, make_cost_matrix

from .types import CardSort

__all__ = ("distance", "max_distance", "norm_distance")


def distance[T](sort1: CardSort[T], sort2: CardSort[T]) -> int:
    """Computes the edit distance between the two given card sorts."""
    if not sort1 and not sort2:
        return 0

    weights = [
        [len(group1 & group2) for group2 in sort2]
        for group1 in sort1
    ]
    cost_matrix = make_cost_matrix(weights)
    total = sum([
        weights[row][col]
        for row, col in Munkres().compute(cost_matrix)
    ])
    return sum(len(g) for g in sort1) - total


def max_distance[T](sort: CardSort[T], *, num_groups: int = None) -> int:
    """
    Computes the maximum edit distance any other card sort could be to the
    given card sort
    """
    if num_groups is None:
        num_groups = max(len(g) for g in sort)
    weights = []
    for group in sort:
        k = len(group) - len(group) // num_groups
        weights.append([
            k - 1 if i < len(group) % num_groups else k
            for i in range(num_groups)
        ])
    return sum([
        weights[row][col]
        for row, col in Munkres().compute(weights)
    ])


def norm_distance[T](
      probe: CardSort[T],
      sort: CardSort[T],
      *,
      num_groups: int = None,
) -> float:
    """
    Computes the normalised edit distance between the given probe sort and
    card sort.

    If `num_groups` is not given, the number of groups will be unbounded.
    """
    if num_groups is None:
        num_groups = max(len(g) for g in probe)
    return distance(probe, sort) / max_distance(probe, num_groups=num_groups)
