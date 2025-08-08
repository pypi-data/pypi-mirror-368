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
"""Test functions for the JAXChain."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Callable

import pytest
from gemseo.disciplines.auto_py import AutoPyDiscipline
from gemseo.mda.gauss_seidel import MDAGaussSeidel
from numpy.testing import assert_allclose

from gemseo_jax.auto_jax_discipline import AutoJAXDiscipline
from gemseo_jax.jax_chain import JAXChain

if TYPE_CHECKING:
    from collections.abc import Sequence


def compute_a(z: float = 2.0) -> float:  # noqa: D103
    a = z + 3
    return a  # noqa: RET504


def compute_b(stat1: float = 3.0) -> float:  # noqa: D103
    b = 2 * stat1
    return b  # noqa: RET504


def compute_c(stat2: float = 2.0) -> float:  # noqa: D103
    c = stat2**2
    return c  # noqa: RET504


def compute_d(a: float = 0.0) -> float:  # noqa: D103
    d = a**3
    return d  # noqa: RET504


def compute_e(b: float = 0.0, c: float = 0.0) -> float:  # noqa: D103
    e = b - c
    return e  # noqa: RET504


def compute_f(d: float = 0.0) -> float:  # noqa: D103
    f = d - 4
    return f  # noqa: RET504


def compute_g(d: float = 0.0) -> float:  # noqa: D103
    g = d + 4
    return g  # noqa: RET504


def compute_h(d: float = 1.0, e: float = 0.0, i: float = 0.0) -> float:  # noqa: D103
    h = e + i / d
    return h  # noqa: RET504


def compute_i(e: float = 0.0, h: float = 0.0) -> float:  # noqa: D103
    i = e - 3 * h
    return i  # noqa: RET504


@pytest.fixture(scope="module")
def functions() -> Sequence[Callable[[float, ..., float], float]]:
    """The functions to create a JAXChain over."""
    return [
        compute_a,
        compute_b,
        compute_c,
        compute_d,
        compute_e,
        compute_f,
        compute_g,
        compute_h,
        compute_i,
    ]


# Priority 0 :
# ['a']
# ['b']
# ['c']
#
# Priority 1 :
# ['d']
# ['e']
#
# Priority 2 :
# ['f']
# ['g']
# ['h', 'i']
# chain inputs     : ['stat1', 'stat2', 'i']
# chain outputs    : ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']


def test_init(functions):
    """Test JAXChain object initialization."""
    JAXChain([AutoJAXDiscipline(f) for f in functions])


def test_coupling_structure(functions):
    """Test if coupling_structure is set."""
    chain = JAXChain([AutoJAXDiscipline(f) for f in functions])
    assert "i" in chain.input_grammar.names
    assert "i" in chain.output_grammar.names


def test_compute_all(functions):
    """Test if compute_all function yields same results as one MDA iteration."""
    n_iter = 15
    coupling_init_guess = 0.0

    chain = JAXChain([AutoJAXDiscipline(f) for f in functions])

    def iterate_coupling(initial_guess, max_iter):
        """Iterate jax_chain.compute_all() to solve coupling."""
        inputs = {"i": initial_guess, "z": 2.0, "stat1": 3.0, "stat2": 2.0}
        outputs = {}
        for _i in range(max_iter):
            outputs = chain._JAXChain__compute_all(inputs)
            inputs["i"] = outputs["i"]
        return outputs

    jax_output_data = iterate_coupling(coupling_init_guess, n_iter)

    mda = MDAGaussSeidel([AutoPyDiscipline(f) for f in functions], max_mda_iter=n_iter)
    np_output_data = mda.execute({
        "stat1": 3.0,
        "stat2": 2.0,
        "i": coupling_init_guess,
    })
    for output_name in chain.output_grammar.names:
        assert_allclose(
            jax_output_data[output_name], np_output_data[output_name], rtol=1e-4
        )


def test_execution(functions):
    """Test JAXDicipline of a JAXChain."""
    chain = JAXChain([AutoJAXDiscipline(f) for f in functions])
    output_data = chain.execute()
    assert chain.check_jacobian(threshold=1e-6, auto_set_step=True)
    jax_output_data = chain.execute({"i": output_data["i"]})

    mda = MDAGaussSeidel([AutoPyDiscipline(f) for f in functions], max_mda_iter=1)
    np_output_data = mda.execute({"stat1": 3.0, "stat2": 2.0, "i": 0.0})
    for output_name in chain.output_grammar.names:
        assert_allclose(
            jax_output_data[output_name], np_output_data[output_name], rtol=1e-4
        )
