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
"""Tests for utilities."""

from __future__ import annotations

import pytest
from gemseo.core.discipline.discipline import Discipline
from jax.numpy import sqrt
from numpy import array

from gemseo_jax.jax_discipline import DataType
from gemseo_jax.jax_discipline import JAXDiscipline
from gemseo_jax.utils import create_jax_discipline_from_discipline


class DummyDisciplineUsingJAX(Discipline):
    """A dummy discipline using JAX."""

    default_grammar_type = Discipline.GrammarType.SIMPLER

    def __init__(self) -> None:
        super().__init__(name="foo")
        self.io.input_grammar.update_from_names(("in",))
        self.io.output_grammar.update_from_names(("out",))
        self.io.input_grammar.defaults = {"in": array([1.0])}

    def _run(self, input_data: dict[str, DataType]) -> dict[str, DataType]:
        return {"out": 2 * sqrt(input_data["in"])}


@pytest.mark.parametrize("compile_jit", [False, True])
@pytest.mark.parametrize("differentiation_method", JAXDiscipline.DifferentiationMethod)
def test_create_jax_discipline_from_discipline(compile_jit, differentiation_method):
    """Test the function create_jax_discipline_from_discipline."""
    jax_discipline = create_jax_discipline_from_discipline(
        DummyDisciplineUsingJAX(), differentiation_method=differentiation_method
    )
    assert isinstance(jax_discipline, JAXDiscipline)
    assert jax_discipline.name == "foo"

    jax_discipline.add_differentiated_inputs(["in"])
    jax_discipline.add_differentiated_outputs(["out"])

    if compile_jit:
        jax_discipline.compile_jit()

    # Default input value
    jax_discipline.execute()
    assert jax_discipline.io.data["out"] == array([2.0])

    # Custom input value
    jax_discipline.execute({"in": array([3.0])})
    assert jax_discipline.io.data["out"] == array([2.0 * 3**0.5])

    jac = jax_discipline.linearize({"in": array([3.0])})
    assert jac["out"]["in"] == array([[2.0 * 0.5 / 3**0.5]])


def test_create_jax_discipline_from_discipline_name():
    """Test the function create_jax_discipline_from_discipline with custom name."""
    jax_discipline = create_jax_discipline_from_discipline(
        DummyDisciplineUsingJAX(), name="bar"
    )
    assert jax_discipline.name == "bar"
