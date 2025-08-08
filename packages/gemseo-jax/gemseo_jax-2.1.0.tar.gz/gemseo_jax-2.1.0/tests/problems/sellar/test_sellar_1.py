# Copyright 2021 ISAE-SUPAERO, https://www.isae-supaero.fr/en/
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
"""Tests for the 1st discipline Sellar problem in JAX."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from gemseo.problems.mdo.sellar.sellar_1 import Sellar1
from gemseo.problems.mdo.sellar.utils import get_initial_data
from numpy.random import default_rng
from numpy.testing import assert_allclose

from gemseo_jax.problems.sellar.sellar_1 import JAXSellar1

if TYPE_CHECKING:
    from gemseo.typing import RealArray


@pytest.fixture(params=[1, 10, 100])
def n(request) -> int:
    """The dimension of the local design variables and coupling variables."""
    return request.param


@pytest.fixture
def input_data(n: int) -> dict[str, RealArray]:
    """An input value for [JAX]Sellar1."""
    r_float = default_rng(12345).random()
    return {
        name: 1.5 * r_float * value for name, value in get_initial_data(n=n).items()
    }


@pytest.fixture
def numpy_discipline(n: int) -> Sellar1:
    """The NumPy version of Sellar1."""
    return Sellar1(n=n)


@pytest.fixture
def jax_discipline(n: int) -> JAXSellar1:
    """The JAX version of Sellar1."""
    return JAXSellar1(n=n)


def test_execute(input_data, numpy_discipline, jax_discipline):
    """Check the execution of JAXSellar1."""
    numpy_discipline.execute(input_data)
    numpy_output_data = numpy_discipline.get_output_data()

    jax_discipline.execute(input_data)
    jax_output_data = jax_discipline.get_output_data()

    for output_name in numpy_discipline.output_grammar.names:
        assert_allclose(jax_output_data[output_name], numpy_output_data[output_name])


def test_jacobian(input_data, jax_discipline):
    """Check the computation of the Jacobian."""
    jax_discipline.check_jacobian(input_data=input_data, threshold=1e-4)
