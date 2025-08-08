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
"""Utilities."""

from typing import Any

from gemseo.core.discipline.discipline import Discipline

from gemseo_jax.jax_discipline import DataType
from gemseo_jax.jax_discipline import JAXDiscipline


class _DisciplineBasedJAXFunction:
    """A JAX function executing a discipline using JAX instead of NumPy and SciPy."""

    __discipline: Discipline
    """The discipline using JAX using JAX instead of NumPy and SciPy."""

    def __init__(self, discipline: Discipline) -> None:
        """
        Args:
            discipline: The discipline using JAX using JAX instead of NumPy and SciPy.
        """  # noqa: D205, D212, D415
        # The use of cache can rely on NumPy and thus breaks the logic of JAX.
        # So we deactivate the cache.
        # It would have been a duplicate anyway
        # because the JAXDiscipline wrapping this discipline has its own cache.
        discipline.set_cache(discipline.CacheType.NONE)
        self.__discipline = discipline

    def __call__(self, input_data: DataType) -> DataType:  # noqa: D102
        return dict(self.__discipline.execute(input_data))


def create_jax_discipline_from_discipline(
    discipline: Discipline, *args: Any, **kwargs: Any
) -> JAXDiscipline:
    """Create a `JAXDiscipline` from a discipline using JAX instead of NumPy and SciPy.

    It will use the same input variables,
    the same output variables
    and the same default input values.

    Args:
        discipline: The discipline using JAX instead of NumPy and SciPy.
        *args: The positional arguments of `JAXDiscipline`,
            except `function`, `input_names`, `output_names` and `default_inputs`.
        **kwargs: The keyword arguments of `JAXDiscipline`.

    Returns:
        The JAX discipline.

    Warning:
        JAX's automatic differentiation works
        with Python control flow and logical operators.
        Using control flow and logical operators with jit
        (see [compile_jit][gemseo_jax.jax_discipline.JAXDiscipline.compile_jit])
        is more complicated.
        If you have any difficulties,
        you can have a look at https://docs.jax.dev/en/latest/control-flow.html.
    """
    return JAXDiscipline(
        _DisciplineBasedJAXFunction(discipline),
        discipline.io.input_grammar,
        discipline.io.output_grammar,
        discipline.io.input_grammar.defaults,
        *args,
        name=kwargs.pop("name", discipline.name),
        **kwargs,
    )
