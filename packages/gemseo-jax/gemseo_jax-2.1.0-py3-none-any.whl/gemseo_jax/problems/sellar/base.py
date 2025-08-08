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
"""A base class for the JAX disciplines of the Sellar MDO problem."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import ClassVar

from gemseo import READ_ONLY_EMPTY_DICT
from gemseo.problems.mdo.sellar.utils import get_initial_data

from gemseo_jax.auto_jax_discipline import AutoJAXDiscipline

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from gemseo.typing import RealArray


class BaseJAXSellar(AutoJAXDiscipline):
    """A base class for the JAX disciplines of the Sellar MDO problem."""

    _INPUT_NAMES: ClassVar[tuple[str, ...]]
    """The names of the inputs."""

    _OUTPUT_NAMES: ClassVar[tuple[str, ...]]
    """The names of the outputs."""

    def __init__(
        self,
        n: int = 1,
        static_args: Mapping[str, Any] = READ_ONLY_EMPTY_DICT,
        differentiation_method: AutoJAXDiscipline.DifferentiationMethod = AutoJAXDiscipline.DifferentiationMethod.AUTO,  # noqa: E501
        differentiate_at_execution: bool = False,
    ) -> None:
        """
        Args:
            n: The size of the local design variables and coupling variables.
        """  # noqa: D205, D212, D415
        super().__init__(
            function=self._jax_func,
            static_args=static_args,
            differentiation_method=differentiation_method,
            differentiate_at_execution=differentiate_at_execution,
        )
        self.default_input_data = get_initial_data(self._INPUT_NAMES, n)

    @abstractmethod
    def _jax_func(self, *args: RealArray) -> RealArray:
        """The JAX function used by the JAXDiscipline.

        Args:
            *args: The input values.
                The discipline input names are the names of these arguments.

        Returns:
            The output value(s) returned as `return variable_1, variable_2, ...`.
                The discipline output names are the names of these variables.
        """
