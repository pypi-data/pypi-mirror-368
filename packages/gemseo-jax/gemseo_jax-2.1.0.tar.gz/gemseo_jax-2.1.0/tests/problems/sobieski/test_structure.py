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
"""Tests for JAXSobieskiStructure."""

from __future__ import annotations

import pytest
from gemseo.problems.mdo.sobieski.core.design_space import SobieskiDesignSpace
from gemseo.problems.mdo.sobieski.disciplines import SobieskiStructure
from numpy.testing import assert_allclose

from gemseo_jax.problems.sobieski.structure import JAXSobieskiStructure


@pytest.fixture(scope="module")
def input_data() -> dict[str, list[float]]:
    """An input value for [JAX]SobieskiStructure."""
    return {
        k: v * (1 + (1 + index) / 10)
        for index, (k, v) in enumerate(
            SobieskiDesignSpace().get_current_value(as_dict=True).items()
        )
        if k in ["x_shared", "y_21", "y_31", "x_1", "c_0", "c_1", "c_2"]
    }


@pytest.fixture(scope="module")
def numpy_discipline() -> SobieskiStructure:
    """The NumPy version of SobieskiStructure."""
    return SobieskiStructure()


@pytest.fixture(scope="module")
def jax_discipline() -> JAXSobieskiStructure:
    """The JAX version of JAXSobieskiStructure."""
    return JAXSobieskiStructure()


def test_execute(numpy_discipline, jax_discipline, input_data):
    """Check the execution of JAXSobieskiStructure."""
    numpy_discipline.execute(input_data)
    numpy_output_data = numpy_discipline.get_output_data()
    jax_discipline.execute(input_data)
    jax_output_data = jax_discipline.get_output_data()
    for output_name in numpy_discipline.output_grammar.names:
        assert_allclose(jax_output_data[output_name], numpy_output_data[output_name])


def test_jacobian(jax_discipline, input_data):
    """Check the computation of the Jacobian."""
    jax_discipline.check_jacobian(input_data=input_data, threshold=1e-4)
