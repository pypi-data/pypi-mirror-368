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
"""The second discipline of the Sellar problem in JAX."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from gemseo import READ_ONLY_EMPTY_DICT
from gemseo.problems.mdo.sellar.variables import ALPHA
from gemseo.problems.mdo.sellar.variables import BETA
from gemseo.problems.mdo.sellar.variables import C_1
from gemseo.problems.mdo.sellar.variables import C_2
from gemseo.problems.mdo.sellar.variables import OBJ
from gemseo.problems.mdo.sellar.variables import X_1
from gemseo.problems.mdo.sellar.variables import X_2
from gemseo.problems.mdo.sellar.variables import X_SHARED
from gemseo.problems.mdo.sellar.variables import Y_1
from gemseo.problems.mdo.sellar.variables import Y_2
from jax.numpy import exp
from jax.numpy import mean

from gemseo_jax.problems.sellar.base import BaseJAXSellar

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from gemseo.typing import RealArray


class JAXSellarSystem(BaseJAXSellar):
    """The discipline to compute the objective and constraints in JAX."""

    _INPUT_NAMES: ClassVar[tuple[str, str, str, str, str, str, str]] = (
        X_SHARED,
        X_1,
        X_2,
        Y_1,
        Y_2,
        ALPHA,
        BETA,
    )

    _OUTPUT_NAMES: ClassVar[tuple[str, str, str]] = (OBJ, C_1, C_2)

    __n: int
    """The size of the local and coupling variables."""

    def __init__(
        self,
        n: int = 1,
        static_args: Mapping[str, Any] = READ_ONLY_EMPTY_DICT,
        differentiation_method: BaseJAXSellar.DifferentiationMethod = BaseJAXSellar.DifferentiationMethod.AUTO,  # noqa: E501
        differentiate_at_execution: bool = False,
    ) -> None:
        """
        Args:
            n: The size of the local design variables and coupling variables.
        """  # noqa: D205, D212, D415
        super().__init__(
            n,
            static_args=static_args,
            differentiation_method=differentiation_method,
            differentiate_at_execution=differentiate_at_execution,
        )
        self.__n = n

    def _jax_func(
        self,
        y_1: RealArray,
        y_2: RealArray,
        x_shared: RealArray,
        x_1: RealArray,
        x_2: RealArray,
        alpha: RealArray,
        beta: RealArray,
    ) -> tuple[RealArray, RealArray, RealArray]:
        """Compute the value of the objective and constraints.

        Args:
            y_1: The value of the coupling variable `y_1`.
            y_2: The value of the coupling variable `y_2`.
            x_shared: The value of the shared design variables.
            x_1: The value of local design variable 1.
            x_2: The value of local design variable 2.
            alpha: The name of the tunable parameter in the constraint 1.
            beta: The name of the tunable parameter in the constraint 2.

        Returns:
            The values of the objective and constraints `c_1` and `c_2`.
        """
        obj = (
            x_shared[1]
            + exp(-mean(y_2))
            + (x_1.dot(x_1) + x_2.dot(x_2) + y_1.dot(y_1)) / self.__n
        )
        c_1 = alpha - y_1**2
        c_2 = y_2 - beta
        return obj, c_1, c_2
