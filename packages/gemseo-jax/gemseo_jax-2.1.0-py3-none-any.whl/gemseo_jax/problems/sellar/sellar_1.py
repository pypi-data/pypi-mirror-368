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
"""The first discipline of the Sellar problem in JAX."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from gemseo import READ_ONLY_EMPTY_DICT
from gemseo.problems.mdo.sellar.variables import GAMMA
from gemseo.problems.mdo.sellar.variables import X_1
from gemseo.problems.mdo.sellar.variables import X_SHARED
from gemseo.problems.mdo.sellar.variables import Y_1
from gemseo.problems.mdo.sellar.variables import Y_2
from jax.numpy import absolute
from jax.numpy import sqrt

from gemseo_jax.problems.sellar.base import BaseJAXSellar

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from gemseo.typing import RealArray


class JAXSellar1(BaseJAXSellar):
    """The discipline to compute the coupling variable :math:`y_1` in JAX."""

    _INPUT_NAMES: ClassVar[tuple[str, str, str, str]] = (X_1, X_SHARED, Y_2, GAMMA)

    _OUTPUT_NAMES: ClassVar[tuple[str]] = (Y_1,)

    __k: float
    """The shared coefficient controlling the coupling strength."""

    def __init__(
        self,
        n: int = 1,
        k: float = 1.0,
        static_args: Mapping[str, Any] = READ_ONLY_EMPTY_DICT,
        differentiation_method: BaseJAXSellar.DifferentiationMethod = BaseJAXSellar.DifferentiationMethod.AUTO,  # noqa: E501
        differentiate_at_execution: bool = False,
    ) -> None:
        """
        Args:
            k: The shared coefficient controlling the coupling strength.
        """  # noqa: D205, D212, D415
        self.__k = k
        super().__init__(
            n,
            static_args=static_args,
            differentiation_method=differentiation_method,
            differentiate_at_execution=differentiate_at_execution,
        )

    def _jax_func(
        self, y_2: RealArray, x_1: RealArray, x_shared: RealArray, gamma: RealArray
    ) -> RealArray:
        """Compute the value of the coupling variable `y_1`.

        Args:
            y_2: The value of the coupling variable `y_2`.
            x_1: The value of the local design variable 1.
            x_shared: The value of the shared design variables.
            gamma: The value of the tunable parameter of the 1st discipline.

        Returns:
            The value of the coupling variable `y_1`.
        """
        y_1_sq = x_shared[0] ** 2 + x_shared[1] + x_1 - gamma * self.__k * y_2
        y_1 = sqrt(absolute(y_1_sq))
        return y_1  # noqa: RET504
