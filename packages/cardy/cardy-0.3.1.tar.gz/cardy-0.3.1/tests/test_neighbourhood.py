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

from cardy import neighbourhood, norm_distance
from utils import test

SORTS = {
    0: ({1, 2, 3}, {4, 5}),
    1: ({1, 2, 3}, {4, 5}, set()),
    2: ({1, 2}, {3}, {4, 5}),
    3: ({1, 2}, {3, 4}, {5}),
    4: ({1, 2, 4}, {3, 5},),
}


@test
def zero_neighbourhoods_only_include_equivalent_card_sorts():
    assert neighbourhood(0, SORTS[0], SORTS) == {0, 1}
    assert neighbourhood(0, SORTS[2], SORTS) == {2}
    assert neighbourhood(0, ({1, 2, 3, 4, 5},), SORTS) == set()


@test
def zero_norm_neighbourhoods_only_include_equivalent_card_sorts():
    dist = lambda l, r: norm_distance(l, r, num_groups=3)
    assert neighbourhood(0, SORTS[0], SORTS, distance=dist) == {0, 1}
    assert neighbourhood(0, SORTS[2], SORTS, distance=dist) == {2}
    assert neighbourhood(0, ({1, 2, 3, 4, 5},), SORTS, distance=dist) == set()


@test
def neighbourhoods_are_returned_when_sorts_have_different_distances():
    assert neighbourhood(1, SORTS[0], SORTS) == {0, 1, 2}
    assert neighbourhood(2, SORTS[0], SORTS) == {0, 1, 2, 3, 4}
    assert neighbourhood(2, ({1, 2, 3, 4, 5},), SORTS) == {0, 1, 4}
    assert neighbourhood(3, ({1, 2, 3, 4, 5},), SORTS) == {0, 1, 2, 3, 4}


@test
def neighbourhoods_are_returned_when_sorts_have_different_norm_distances():
    dist = lambda l, r: norm_distance(l, r, num_groups=3)
    assert neighbourhood(1 / 3, SORTS[0], SORTS, distance=dist) \
           == {0, 1, 2}
    assert neighbourhood(2 / 3, SORTS[0], SORTS, distance=dist) \
           == {0, 1, 2, 3, 4}
    assert neighbourhood(2 / 3, ({1, 2, 3, 4, 5},), SORTS, distance=dist) \
           == {0, 1, 4}
    assert neighbourhood(3 / 3, ({1, 2, 3, 4, 5},), SORTS, distance=dist) \
           == {0, 1, 2, 3, 4}