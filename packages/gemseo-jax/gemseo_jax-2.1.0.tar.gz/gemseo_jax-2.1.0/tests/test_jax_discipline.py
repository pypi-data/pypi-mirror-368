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
"""Test functions for the JAXDiscipline."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Callable

import pytest
from chex import assert_max_traces
from gemseo import configure_logger
from numpy import array
from numpy.testing import assert_equal

from gemseo_jax.jax_discipline import JAXDiscipline
from gemseo_jax.jax_discipline import NumberLike

if TYPE_CHECKING:
    from collections.abc import Mapping

# Import this if prints are uncommented from test_jacobian_diff_inouts
# from jax import make_jaxpr


@pytest.fixture(scope="module")
def function() -> Callable[[Mapping[str, NumberLike]], Mapping[str, NumberLike]]:
    """A function computing linear combinations."""

    def my_function(input_data: Mapping[str, NumberLike]):
        """A function computing linear combinations.

        Args:
            input_data: The input data.

        Returns:
            The output data.
        """
        a = input_data["a"]
        b = input_data["b"]
        c = input_data["c"]
        d = input_data["d"]

        x = 2 * a + b - c * d
        y = a * b
        z = c * d
        return {"x": x, "y": y, "z": z}

    return my_function


@pytest.fixture(scope="module")
def input_names() -> list[str]:
    """The input names."""
    return ["a", "b", "c", "d"]


@pytest.fixture(scope="module")
def output_names() -> list[str]:
    """The output names."""
    return ["x", "y", "z"]


@pytest.fixture(scope="module")
def default_inputs() -> dict[str, float]:
    """The default input values."""
    # The mix of scalar, mono-dimensional and multidimensional input variables
    # generates scalar, mono-dimensional and multidimensional variables,
    # which allows to test the robustness of execute() and compute_jacobian().
    return {"a": 0.0, "b": array([1.0]), "c": 2.0, "d": array([3.0, 3.0])}


def test_init(function, input_names, output_names, default_inputs):
    """Test JAXDiscipline object initialization."""
    discipline = JAXDiscipline(function, input_names, output_names, default_inputs)
    assert discipline is not None
    assert set(discipline.input_grammar) == set(input_names)
    assert set(discipline.output_grammar) == set(output_names)
    for input_name in input_names:
        assert_equal(
            discipline.default_input_data[input_name], default_inputs[input_name]
        )


def test_execution(function, input_names, output_names, default_inputs):
    """Test JAXDiscipline execution."""
    discipline = JAXDiscipline(function, input_names, output_names, default_inputs)
    output_data = discipline.execute()
    default_outputs = function(default_inputs)

    for output_name in output_names:
        assert_equal(output_data[output_name], default_outputs[output_name])


def test_jacobian(function, input_names, output_names, default_inputs):
    """Test JAXDiscipline Jacobian computation."""
    discipline_auto = JAXDiscipline(function, input_names, output_names, default_inputs)
    discipline_auto.execute()
    assert discipline_auto.check_jacobian()

    discipline_fwd = JAXDiscipline(
        function,
        input_names,
        output_names,
        default_inputs,
        differentiation_method="forward",
    )
    assert discipline_fwd.check_jacobian()

    discipline_rev = JAXDiscipline(
        function,
        input_names,
        output_names,
        default_inputs,
        differentiation_method="reverse",
    )
    assert discipline_rev.check_jacobian()


def test_differentiate_at_execution(
    function, input_names, output_names, default_inputs
):
    """Test JAXDiscipline with Jacobian computation at every iteration."""
    discipline_nodiff = JAXDiscipline(
        function, input_names, output_names, default_inputs
    )
    discipline_nodiff.execute()
    assert not discipline_nodiff._has_jacobian

    discipline_nodiff._compute_jacobian()
    assert discipline_nodiff._has_jacobian

    discipline_diff = JAXDiscipline(
        function,
        input_names,
        output_names,
        default_inputs,
        differentiate_at_execution=True,
    )
    discipline_diff.execute()
    assert discipline_diff._has_jacobian


def test_execution_pre_run(function, input_names, output_names, default_inputs):
    r"""Test the JAXDiscipline execution with pre-run compilation.

    We use :func:`chex.assert_max_traces` to ensure the JAX function is not traced
    before we perform a pre-run. Also, after the pre-run we ensure that :func:`.execute`
    does not perform any extra tracing (re-compilation).
    """
    discipline = JAXDiscipline(function, input_names, output_names, default_inputs)
    assert_max_traces(function, 0)
    discipline.compile_jit(False)
    assert_max_traces(function, 0)
    discipline.compile_jit()
    assert_max_traces(function, 1)
    discipline.execute()
    assert_max_traces(function, 1)


def test_jacobian_diff_inouts(function, input_names, output_names, default_inputs):
    """Test the JAXDiscipline Jacobian computation with differentiated inputs/outputs.

    This test checks that the discipline correctly computes the Jacobian when some
    inputs and outputs are filtered. It also tests that the discipline can be used to
    compute the Jacobian at different points.
    """
    configure_logger()
    discipline = JAXDiscipline(function, input_names, output_names, default_inputs)
    discipline.compile_jit()
    assert discipline.check_jacobian()

    discipline.add_differentiated_inputs(["c", "d"])
    discipline.add_differentiated_outputs(["z"])
    discipline.compile_jit()
    assert discipline.check_jacobian(input_names=["c", "d"], output_names=["z"])

    # Check at different point with Jacobian filter
    assert discipline.check_jacobian(
        input_data={
            "a": array([0.0]),
            "b": array([2.0]),
            "c": array([4.0]),
            "d": array([6.0, 6.0]),
        },
        input_names=["c", "d"],
        output_names=["z"],
    )

    # Test adding all variables to filtering
    discipline.add_differentiated_inputs(input_names)
    discipline.add_differentiated_outputs(output_names)
    assert discipline.check_jacobian(
        input_names=input_names,
        output_names=output_names,
    )


def test_jacobian_filter(function, input_names, output_names, default_inputs):
    r"""Test filtering of Jacobian for some inputs/outputs.

    We use :func:`chex.assert_max_traces` to ensure the JAX function is traced after a
    jit compilation with pre-run. Then, when we filter the Jacobian for some variables,
    a recompilation of the discipline :func:`.jax_out_func` but not of the original
    function (just a filtered version of it). Finally, when we add all variables to
    Jacobian calculation, :func:`.jax_out_func` is recompiled and so is the original
    function, as there is no filter when dealing with all variables.
    """
    discipline = JAXDiscipline(function, input_names, output_names, default_inputs)
    discipline.compile_jit()
    assert_max_traces(function, 1)

    discipline.add_differentiated_inputs([input_names[-1]])
    discipline.add_differentiated_outputs([output_names[-1]])
    assert_max_traces(function, 1)

    discipline.add_differentiated_inputs(input_names)
    discipline.add_differentiated_outputs(output_names)
    assert_max_traces(function, 2)
