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

from pytest import approx
from cardy import distance, max_distance, norm_distance
from utils import test


@test
def empty_card_sorts_have_a_distance_of_zero():
    assert distance((), ()) == 0


@test
def equivalent_card_sorts_have_an_edit_distance_of_zero():
    assert distance(({1},), ({1},)) == 0
    assert distance(({1}, {2}), ({1}, {2})) == 0
    assert distance(({2}, {1}), ({1}, {2})) == 0
    assert distance(
        ({1, 2, 3}, {4}, {5, 6}),
        ({4}, {1, 2, 3}, {5, 6}),
    ) == 0


@test
def empty_groups_are_ignored_when_computing_distances():
    assert distance(({1}, {2}, set()), ({1}, {2})) == 0
    assert distance(({1}, {2}), ({1}, set(), {2})) == 0


@test
def single_card_displacements_have_an_edit_distance_of_one():
    assert distance(({1, 2}, {3}), ({1}, {2, 3})) == 1
    assert distance(({1}, {2}, {3}), ({1}, {2, 3})) == 1
    assert distance(({1}, {2, 3}), ({1, 2, 3},)) == 1


@test
def distance_between_card_sorts_is_computed_for_multiple_moves():
    assert distance(
        ({1, 2, 3}, {4, 5, 6}, {7, 8, 9}),
        ({1, 2}, {3, 4}, {5, 6, 7}, {8, 9}),
    ) == 3
    assert distance(
        ({1, 2}, {3, 4}, {5, 6, 7}, {8, 9}),
        ({1, 2, 3}, {4, 5, 6}, {7, 8, 9}),
    ) == 3


@test
def maximum_edit_distance_is_computed_for_card_sorts():
    sort = (
        {"a1", "a2", "a3"},
        {"b1", "b2", "b3", "b4", "b5"},
        {"c1", "c2", "c3", "c4", "c5"},
        {"d1", "d2", "d3", "d4"},
    )
    assert max_distance(sort) == 13
    assert max_distance(sort, num_groups=4) == 12


@test
def normalised_edit_distance_is_computed_for_card_sorts():
    sort1 = (
        {"a1", "a2", "a3"},
        {"b1", "b2", "b3", "b4", "b5"},
        {"c1", "c2", "c3", "c4", "c5"},
        {"d1", "d2", "d3", "d4"},
    )
    sort2 = (
        {"a1", "b1", "b5", "c1", "c5", "d1"},
        {"a2", "b2", "c2", "d2"},
        {"a3", "b3", "c3", "d3"},
        {"b4", "c4", "d4"},
    )
    sort3 = (
        {"a1", "b1", "c1", "d1"},
        {"a2", "b2", "c2", "d2"},
        {"a3", "b3", "c3", "d3"},
        {"b4", "c4", "d4"},
        {"b5", "c5"},
    )
    sort4 = (
        {"a1", "a2"},
        {"a3", "b1", "b2", "b3", "b4", "b5"},
        {"c1", "c2", "c3", "c4", "c5"},
        {"d1", "d2", "d3", "d4"},
    )
    assert norm_distance(sort1, sort2, num_groups=4) == 1
    assert norm_distance(sort1, sort3) == 1
    assert norm_distance(sort1, sort4, num_groups=4) == approx(1 / 12)
