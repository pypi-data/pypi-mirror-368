# Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""Tests for the Sobieski's Supersonic Business Jet MDO benchmark written in JAX."""

from __future__ import annotations

import pytest
from gemseo.problems.mdo.sobieski.core.design_space import SobieskiDesignSpace
from gemseo.problems.mdo.sobieski.disciplines import SobieskiMission

from gemseo_jax.problems.sobieski.mission import JAXSobieskiMission


@pytest.fixture(scope="module")
def input_data() -> dict[str, list[float]]:
    """A input value for [JAX]SobieskiMission."""
    return {
        k: v * (1 + (1 + index) / 10)
        for index, (k, v) in enumerate(
            SobieskiDesignSpace().get_current_value(as_dict=True).items()
        )
        if k in ["x_shared", "y_14", "y_24", "y_34"]
    }


@pytest.fixture(scope="module")
def numpy_discipline() -> SobieskiMission:
    """The NumPy version of SobieskiMission."""
    return SobieskiMission()


@pytest.fixture(scope="module")
def jax_discipline() -> JAXSobieskiMission:
    """The JAX version of SobieskiMission."""
    return JAXSobieskiMission()


def test_execute(numpy_discipline, jax_discipline, input_data):
    """Check the execution of JAXSobieskiMission."""
    numpy_discipline.execute(input_data)
    jax_discipline.execute(input_data)
    assert numpy_discipline.io.data["y_4"] == jax_discipline.io.data["y_4"]


def test_jacobian(jax_discipline, input_data):
    """Check the computation of the Jacobian."""
    jax_discipline.check_jacobian(input_data=input_data, threshold=1e-4)
