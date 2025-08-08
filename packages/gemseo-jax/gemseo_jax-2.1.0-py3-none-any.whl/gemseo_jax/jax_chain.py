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
"""Module for executing a chain of JAXDiscipline's at once in JAX.

The :class:`.MDOCouplingStructure` of the :class:`.JAXDiscipline`s is used to get the
correct sequence of function calls, according to the dependencies among functions.

Note:
    If there is a coupling within disciplines, the resulting chain will be self-coupled,
    i.e., some variables are inputs and outputs to the chain and one chain execution
    corresponds to one fixed-point iteration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from gemseo.core.coupling_structure import CouplingStructure

from gemseo_jax.jax_discipline import JAXDiscipline
from gemseo_jax.jax_discipline import NumberLike

if TYPE_CHECKING:
    from collections.abc import Sequence

DifferentiationMethod = JAXDiscipline.DifferentiationMethod


class JAXChain(JAXDiscipline):
    """A chain of JAX disciplines."""

    __sequence: list[list[tuple[JAXDiscipline]]]
    """The sequence of execution of the JAX disciplines."""

    def __init__(
        self,
        disciplines: Sequence[JAXDiscipline],
        differentiation_method: DifferentiationMethod = DifferentiationMethod.AUTO,
        differentiate_at_execution: bool = False,
        name: str | None = None,
    ) -> None:
        """
        Args:
            disciplines: The JAX disciplines to create the chain over.
        """  # noqa: D205, D212, D415, D417
        self.__sequence = CouplingStructure(disciplines).sequence

        # Generate input and output names according to _output_sequence, this
        # adds coupling variables as inputs (as they may be required before computation)
        input_names = []
        output_names = []
        for mdas_at_priority in self.__sequence:
            for mda_at_mdas in mdas_at_priority:
                for disc in mda_at_mdas:
                    input_names.extend([
                        var
                        for var in disc.input_grammar.names
                        if var not in output_names
                    ])
                    output_names.extend(disc.output_grammar.names)

        default_inputs = {}
        for discipline in disciplines:
            default_inputs.update({
                input_name: input_value
                for input_name, input_value in discipline.default_input_data.items()
                if input_name in input_names
            })

        super().__init__(
            function=self.__compute_all,
            input_names=input_names,
            output_names=output_names,
            default_inputs=default_inputs,
            differentiation_method=differentiation_method,
            differentiate_at_execution=differentiate_at_execution,
            name=name,
        )

        # Add self-coupled variables into differentiated inputs and outputs for MDA
        self_coupled_vars = set(self.input_grammar.names) & set(
            self.output_grammar.names
        )
        self.add_differentiated_inputs(self_coupled_vars)
        self.add_differentiated_outputs(self_coupled_vars)

    def __compute_all(self, input_data: dict[str, NumberLike]) -> dict[str, NumberLike]:
        """Evaluate all functions in the correct sequence.

        Args:
            input_data: The input data.

        Return:
            The output data.
        """
        output_data = {}
        for mdas_at_priority in self.__sequence:
            for mda_at_mdas in mdas_at_priority:
                for disc in mda_at_mdas:
                    disc_outputs = disc.jax_out_func({
                        input_name: {**input_data, **output_data}[input_name]
                        for input_name in disc.input_grammar.names
                    })
                    output_data.update(disc_outputs)
        return output_data
