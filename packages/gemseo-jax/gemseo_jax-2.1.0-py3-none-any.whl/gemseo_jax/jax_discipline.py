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

from datetime import timedelta
from logging import getLogger
from timeit import default_timer
from typing import TYPE_CHECKING
from typing import Callable
from typing import Union

import jax
from gemseo.core.discipline.discipline import Discipline
from jax import Array as JAXArray
from jax import jacfwd
from jax import jacrev
from jax import jit
from jax.numpy import atleast_2d
from numpy import array as np_array
from numpy import atleast_1d as np_atleast_1d
from numpy.typing import NDArray
from strenum import StrEnum

if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Mapping
    from collections.abc import Sequence

    from gemseo.typing import StrKeyMapping

LOGGER = getLogger(__name__)
NumberLike = Union[float, NDArray, JAXArray]
DataType = dict[str, NumberLike]

jax.config.update("jax_enable_x64", True)


class JAXDiscipline(Discipline):
    """A discipline interfacing a JAX function."""

    class DifferentiationMethod(StrEnum):
        """The method to compute the Jacobian."""

        AUTO = "auto"
        FORWARD = "forward"
        REVERSE = "reverse"

    jax_out_func: Callable[[DataType], DataType]
    """The JAX function to compute the outputs from the inputs."""

    __jax_jac_func: Callable[[DataType], DataType]
    """The JAX function to compute the Jacobian from the inputs."""

    __sizes: dict[str, int]
    """The sizes of the input and output variables."""

    __differentiation_method: DifferentiationMethod
    """The method to use when computing the Jacobian."""

    __differentiate_at_execution: bool
    """Whether to calculate the Jacobian at every execution."""

    __jac_shape: dict[str, dict[str, int]]
    """The shapes of the jacobian."""

    default_grammar_type = Discipline.GrammarType.SIMPLER
    default_cache_type = Discipline.CacheType.SIMPLE

    def __init__(
        self,
        function: Callable[[DataType], DataType],
        input_names: Sequence[str],
        output_names: Sequence[str],
        default_inputs: Mapping[str, NumberLike],
        differentiation_method: DifferentiationMethod = DifferentiationMethod.AUTO,
        differentiate_at_execution: bool = False,
        name: str | None = None,
    ) -> None:
        """Initialize the JAXDiscipline.

        Args:
            function: The JAX function that takes a dictionary
                ``{input_name: input_value, ...}`` as argument and returns a dictionary
                ``{output_name: output_value, ...}``.
            input_names: The names of the input variables.
            output_names: The names of the output variables.
            default_inputs: The default values of the input variables.
            differentiation_method: The method to compute the Jacobian.
            differentiate_at_execution: Whether to compute the Jacobian when executing
                the discipline.
        """  # noqa: D205, D212, D415
        super().__init__(name=name)
        self.input_grammar.update_from_names(input_names)
        self.output_grammar.update_from_names(output_names)
        self.default_input_data = {
            input_name: np_array(input_value)
            if isinstance(input_value, JAXArray)
            else input_value
            for input_name, input_value in default_inputs.items()
        }
        self.__differentiate_at_execution = differentiate_at_execution
        self.jax_out_func = function
        self.__differentiation_method = differentiation_method
        self.__jax_jac_func = self.__create_jacobian_function(self.jax_out_func)
        self.__sizes = {}
        self.__jac_shape = {}

    @property
    def __create_jacobian_function(self) -> Callable:
        """The JAX transformation to apply on jax_out_func."""
        if self.__differentiation_method == self.DifferentiationMethod.AUTO:
            if len(self._differentiated_output_names) < len(
                self._differentiated_input_names
            ):
                return jacrev
            return jacfwd
        if self.__differentiation_method == self.DifferentiationMethod.FORWARD:
            return jacfwd
        return jacrev

    def add_differentiated_inputs(
        self,
        input_names: Iterable[str] = (),
    ) -> None:
        """
        Notes:
            The Jacobian is also filtered to view non-differentiated static.
        """  # noqa: D205, D212, D415
        old_differentiated_inputs = self._differentiated_input_names.copy()
        super().add_differentiated_inputs(input_names=input_names)
        refilter = any(
            input_name not in old_differentiated_inputs
            for input_name in self._differentiated_input_names
        )
        if refilter:
            self._filter_jacobian()

    def add_differentiated_outputs(
        self,
        output_names: Iterable[str] = (),
    ) -> None:
        """
        Notes:
            The Jacobian is also filtered to view non-differentiated static.
        """  # noqa: D205, D212, D415
        old_differentiated_outputs = self._differentiated_output_names.copy()
        super().add_differentiated_outputs(output_names=output_names)
        refilter = any(
            output_name not in old_differentiated_outputs
            for output_name in self._differentiated_output_names
        )
        if refilter:
            self._filter_jacobian()

    def _filter_jacobian(self) -> None:
        """Filter jacobian call."""
        f_call = self.jax_out_func

        if all(
            name in self._differentiated_input_names
            for name in self.input_grammar.names
        ) and all(
            name in self._differentiated_output_names
            for name in self.output_grammar.names
        ):
            jac_filtered = self.__create_jacobian_function(f_call)
        else:
            # Here we make a custom jacobian, which takes all inputs, but returns the
            # jac of diff inouts only
            def jac_filtered(
                input_data: dict[str, NumberLike],
            ) -> dict[str, dict[str, NumberLike]]:
                diff = {
                    var: val
                    for var, val in input_data.items()
                    if var in self._differentiated_input_names
                }
                non_diff = {
                    var: val
                    for var, val in input_data.items()
                    if var not in self._differentiated_input_names
                }

                # For that, we manually make a filtered function, which takes only diff
                # inputs, fill non-diff data from input_data and returns only diff outs
                # Doing so, statically fixes the non-diff data for the jacobian call
                # (jacobian uses a part of the entire computation graph), but the
                # input_data of the non-diff ins are updated at each __jax_jac_func
                def f_filtered(
                    diff_ins: dict[str, NumberLike],
                ) -> dict[str, NumberLike]:
                    all_ins = {**diff_ins, **non_diff}
                    f_out = f_call(all_ins)
                    return {
                        var: f_out[var] for var in self._differentiated_output_names
                    }

                jac_func = self.__create_jacobian_function(f_filtered)
                return jac_func(diff)

        self.__jax_jac_func = jac_filtered

    def compile_jit(
        self,
        pre_run: bool = True,
    ) -> None:
        """Apply jit compilation over function and jacobian.

        Args:
            pre_run: Whether to call jitted callables once to trigger compilation and
                log times.

        Warning:
            Calling
            [add_differentiated_inputs][gemseo_jax.jax_discipline.JAXDiscipline.add_differentiated_inputs]
            and
            [add_differentiated_outputs][gemseo_jax.jax_discipline.JAXDiscipline.add_differentiated_outputs]
            must be done before calling
            [compile_jit][gemseo_jax.jax_discipline.JAXDiscipline.compile_jit].
        """
        self.jax_out_func = jit(self.jax_out_func)
        self.__jax_jac_func = jit(self.__jax_jac_func)
        if pre_run:
            self._jit_pre_run()

    def _jit_pre_run(self) -> None:
        """Call jitted callables once to trigger compilation and log times."""
        # todo: fill sizes here instead of first run
        t0 = default_timer()
        self.execute()
        t1 = default_timer()
        self.linearize()
        t2 = default_timer()

        LOGGER.info(
            "Compilation of the output function %s: %s seconds.",
            self.name,
            timedelta(seconds=t1 - t0),
        )
        LOGGER.info(
            "Compilation of the Jacobian function %s: %s seconds.",
            self.name,
            timedelta(seconds=t2 - t1),
        )

        self._fill_sizes()

    def _fill_sizes(self) -> None:
        """Fill sizes from local_data."""
        self.__sizes = {
            var_name: 1 if isinstance(var_value, float) else var_value.size
            for var_name, var_value in self.io.data.items()
        }
        self.__jac_shape = {
            output_name: {
                input_name: (self.__sizes[output_name], self.__sizes[input_name])
                for input_name in self._differentiated_input_names
            }
            for output_name in self._differentiated_output_names
        }

    def _run(self, input_data: StrKeyMapping) -> StrKeyMapping | None:
        # A jax function checks for a plain dictionary, thus we cast the input_data.
        output_data = self.jax_out_func(dict(input_data))

        # Cast back into numpy
        self.io.update_output_data({
            output_name: np_atleast_1d(output_data[output_name])
            for output_name in self.output_grammar.names
        })

        # This must still be checked in case discipline is not pre-run
        if not self.__sizes:
            self._fill_sizes()

        # Compute jacobian at each jax_out_func if linearize at every run
        if self.__differentiate_at_execution:
            self._compute_jacobian()

    def _compute_jacobian(
        self,
        input_names: Iterable[str] = (),
        output_names: Iterable[str] = (),
    ) -> None:
        jac_out = self.__jax_jac_func({
            var: self.io.data[var] for var in self.input_grammar.names
        })

        # Cast back into NumPy 2d arrays:
        # Usually we expect a Jacobian matrix
        # as a matrix with as many rows as output dimension,
        # and as many columns as input dimension.
        # However,
        # as soon as one item in the input-output pair is one-dimensional (a scalar),
        # JAX returns a vector instead of a matrix.
        # If both are one-dimensional it simply returns a scalar.
        # Here we must go through the dict turning results into 2d NumPy arrays,
        # except for one-dimensional inputs,
        # as the resulting vector must be further transposed into a column matrix.
        self.jac = {
            output_name: {
                input_name: atleast_2d(jac_array).reshape((-1, 1))
                if self.__sizes[input_name] == 1
                else atleast_2d(jac_array)
                for input_name, jac_array in inner_dict.items()
            }
            for output_name, inner_dict in jac_out.items()
        }
        self._has_jacobian = True
