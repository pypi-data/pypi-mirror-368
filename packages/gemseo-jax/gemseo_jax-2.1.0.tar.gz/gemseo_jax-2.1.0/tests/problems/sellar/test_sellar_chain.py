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
"""Tests for the chained disciplines of the Sellar problem in JAX."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from gemseo.core.chains.chain import MDOChain
from gemseo.problems.mdo.sellar.sellar_1 import Sellar1
from gemseo.problems.mdo.sellar.sellar_2 import Sellar2
from gemseo.problems.mdo.sellar.sellar_system import SellarSystem
from gemseo.problems.mdo.sellar.utils import get_initial_data
from numpy.random import default_rng
from numpy.testing import assert_allclose

from gemseo_jax.problems.sellar.sellar_chain import JAXSellarChain

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
def numpy_chain(n: int) -> MDOChain:
    """The NumPy version of SobieskiAerodynamics."""
    return MDOChain([
        Sellar1(n=n),
        Sellar2(n=n),
        SellarSystem(n=n),
    ])


@pytest.fixture
def jax_chain(n: int) -> JAXSellarChain:
    """The JAX version of JAXSobieskiAerodynamics."""
    return JAXSellarChain(n=n)


def test_execute(input_data, numpy_chain, jax_chain):
    """Check the execution of JAXSobieskiAerodynamics."""
    numpy_chain.execute(input_data)
    numpy_output_data = numpy_chain.get_output_data()

    jax_chain.execute(input_data)
    jax_output_data = jax_chain.get_output_data()

    for output_name in numpy_chain.output_grammar.names:
        assert_allclose(jax_output_data[output_name], numpy_output_data[output_name])


def test_jacobian(input_data, jax_chain):
    """Check the computation of the Jacobian."""
    jax_chain.check_jacobian(input_data=input_data, threshold=1e-4)
