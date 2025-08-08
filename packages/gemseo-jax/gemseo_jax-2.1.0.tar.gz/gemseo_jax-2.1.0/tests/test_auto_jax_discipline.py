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
"""Test functions for the AutoJAXDiscipline."""

from __future__ import annotations

import re

import pytest
from jax.numpy import array
from jax.numpy import power
from jax.numpy import sum as np_sum
from numpy import array as np_array
from numpy import atleast_1d
from numpy.testing import assert_equal

from gemseo_jax.auto_jax_discipline import AutoJAXDiscipline


@pytest.fixture(scope="module")
def function():
    """The function."""

    def my_func(  # noqa: D103
        a: float = 0.0, b: float = 1.0, c: float = 2.0, d: float = 3.0
    ) -> tuple[float, float, float]:
        x = 2 * a + b - c * d
        y = a * b
        z = c * d
        return x, y, z

    return my_func


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
    return {"a": 0.0, "b": 1.0, "c": 2.0, "d": 3.0}


def test_init(function, input_names, output_names, default_inputs):
    """Test initialization."""
    discipline = AutoJAXDiscipline(function)

    assert discipline is not None
    assert set(discipline.input_grammar) == set(input_names)
    assert set(discipline.output_grammar) == set(output_names)
    for input_name in input_names:
        assert_equal(
            discipline.default_input_data[input_name], default_inputs[input_name]
        )


def test_execution(function, input_names, output_names, default_inputs):
    """Test execution."""
    discipline = AutoJAXDiscipline(function)
    output_data = discipline.execute({
        input_name: np_array(input_value)
        for input_name, input_value in default_inputs.items()
    })
    default_outputs = function(**default_inputs)
    for i, output_name in enumerate(output_names):
        assert_equal(output_data[output_name], default_outputs[i])


def test_jacobian(function, input_names, output_names, default_inputs):
    """Test jacobian matrix."""
    discipline = AutoJAXDiscipline(function)
    discipline.execute({"a": atleast_1d(0.0)})
    assert discipline.check_jacobian({"a": np_array([0.0])})


def test_static_args(function, input_names, output_names, default_inputs):
    """Test fixing static args."""
    static_args = {"b": 1.0, "c": 2.0}
    discipline = AutoJAXDiscipline(function, static_args=static_args)
    for input_name in static_args:
        assert input_name not in discipline.input_grammar.names

    default_outputs = function(**default_inputs)
    output_data = discipline.execute({"a": atleast_1d(0.0)})
    for i, output_name in enumerate(output_names):
        assert_equal(output_data[output_name], default_outputs[i])


class Polynomial:  # noqa: D101
    coefficients: list[float]

    def __init__(self, coefficients: list[float]):  # noqa: D107
        self.coefficients = coefficients

    def compute_poly(self, x: float):  # noqa: D102, D103
        terms = array([c * power(x, i) for i, c in enumerate(self.coefficients)])
        return np_sum(terms)


def func_from_obj(x, polynomial):  # noqa: D103
    y = polynomial.compute_poly(x)
    return y  # noqa: RET504


@pytest.mark.parametrize(
    ("coefficients", "expected"), [([0.0, 0.0, 1.0], 4.0), ([0.0, 0.0, 0.0, 1.0], 8.0)]
)
def test_static_obj(coefficients, expected):
    """Test fixing objects as static args."""
    discipline = AutoJAXDiscipline(
        function=func_from_obj,
        static_args={
            "polynomial": Polynomial(coefficients),
            "dummy_arg": None,
        },
    )

    assert "polynomial" not in discipline.input_grammar.names
    assert "polynomial" not in discipline.default_input_data

    assert "dummy_arg" not in discipline.input_grammar.names
    assert "dummy_arg" not in discipline.default_input_data

    input_data = {"x": np_array([2.0])}
    output_data = discipline.execute(input_data)
    assert output_data["y"][0] == expected
    assert discipline.check_jacobian(input_data=input_data, threshold=1e-7)


def formatted_function(x=1.0):
    if x > 0:
        y = -x
        return y  # noqa: RET504
    y = 2 * x
    return y  # noqa: RET504


def wrongly_formatted_function(x=1.0):
    if x > 0:
        y = -x
        return y  # noqa: RET504
    y = 2 * x
    return y, x


def test_wrongly_formatted_function():
    """Test that a wrongly formatted function cannot be used."""
    AutoJAXDiscipline(formatted_function)

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Two return statements use different names: ['y', 'x'] and ['y']."
        ),
    ):
        AutoJAXDiscipline(wrongly_formatted_function)
