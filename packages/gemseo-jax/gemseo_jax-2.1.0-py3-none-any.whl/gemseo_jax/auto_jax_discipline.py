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
"""A discipline interfacing a JAX function."""

from __future__ import annotations

import ast
from inspect import getfullargspec
from inspect import getsource
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable

from gemseo.utils.constants import READ_ONLY_EMPTY_DICT

from gemseo_jax.jax_discipline import DataType
from gemseo_jax.jax_discipline import JAXDiscipline
from gemseo_jax.jax_discipline import NumberLike

if TYPE_CHECKING:
    from collections.abc import Mapping


class AutoJAXDiscipline(JAXDiscipline):
    """Automatically wrap a JAX function into a discipline."""

    __static_args: dict[str, Any]
    """The static arguments of the wrapped function."""

    __function: Callable[[DataType], DataType]
    """The modified function with a dictionary as argument and output."""

    __original_function: Callable[[NumberLike, ..., Any, ...], tuple[NumberLike]]
    """The original function."""

    def __init__(
        self,
        function: Callable[[NumberLike, ..., Any, ...], tuple[NumberLike]],
        static_args: Mapping[str, Any] = READ_ONLY_EMPTY_DICT,
        differentiation_method: JAXDiscipline.DifferentiationMethod = JAXDiscipline.DifferentiationMethod.AUTO,  # noqa: E501
        differentiate_at_execution: bool = False,
        name: str | None = None,
    ) -> None:
        """
        Args:
            function: The JAX function.
            static_args: The names and values of the static arguments of the JAX
                function. These arguments are constant at discipline execution.
                The non-numeric arguments can also be included.
        """  # noqa: D205, D212, D415, D417
        arg_names, output_names, default_args = self.__parse_function(function)
        self.__static_args = {
            input_name: input_value
            for input_name, input_value in static_args.items()
            if input_name in arg_names
        }

        input_names = list(set(arg_names) - set(self.__static_args))
        default_inputs = {
            input_name: default_value
            for input_name, default_value in default_args.items()
            if input_name not in self.__static_args
        }
        self.__original_function = function

        super().__init__(
            function=self.__function,
            input_names=input_names,
            output_names=output_names,
            default_inputs=default_inputs,
            differentiation_method=differentiation_method,
            differentiate_at_execution=differentiate_at_execution,
            name=name,
        )

    def __function(self, input_data: DataType) -> DataType:
        output_data = self.__original_function(**input_data, **self.__static_args)
        output_names = list(self.output_grammar.names)
        if len(output_names) == 1:
            return {output_names[0]: output_data}
        return dict(zip(output_names, output_data))

    @staticmethod
    def __parse_function(
        function: Callable,
    ) -> tuple[list[str], list[str], dict[str, Any]]:
        """Parse the inputs and outputs of a function.

        Args:
            function: The function of interest.

        Return:
            The input names, the output names and the default values of the input
            values.
        """
        function_spec = getfullargspec(function)
        arg_names = function_spec.args
        if "self" in arg_names:
            arg_names.remove("self")
        arg_defaults = function_spec.defaults or {}
        n_args_without_defaults = len(arg_names) - len(arg_defaults)
        default_args = {
            arg_names[i + n_args_without_defaults]: arg_defaults[i]
            for i, name in enumerate(arg_defaults)
        }

        output_names = []
        for node in ast.walk(ast.parse(getsource(function).strip())):
            if isinstance(node, ast.Return):
                value = node.value
                if isinstance(value, ast.Tuple):
                    temp_output_names = [elt.id for elt in value.elts]
                else:
                    temp_output_names = [value.id]

                if output_names and output_names != temp_output_names:
                    msg = (
                        "Two return statements use different names: "
                        f"{output_names} and {temp_output_names}."
                    )
                    raise ValueError(msg)
                output_names = temp_output_names
        return arg_names, output_names, default_args
