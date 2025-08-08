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
"""Base discipline for the Sobieski's SSBJ use case."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from gemseo.problems.mdo.sobieski.core.problem import SobieskiProblem
from gemseo.problems.mdo.sobieski.core.utils import SobieskiBase
from jax.numpy import array
from jax.numpy import clip

from gemseo_jax.auto_jax_discipline import AutoJAXDiscipline

if TYPE_CHECKING:
    from collections.abc import Sequence

    from jax import Array


class BaseJAXSobieskiDiscipline(AutoJAXDiscipline):
    """Base discipline for the Sobieski's SSBJ use case."""

    def __init__(self) -> None:  # noqa: D107
        super().__init__(self._jax_func)
        self.default_input_data = SobieskiProblem().get_default_inputs(
            self.io.input_grammar.names
        )
        base = SobieskiBase(SobieskiBase.DataType.FLOAT)
        self.constants = base.constants
        self._coeff_mtrix = array(
            [
                [0.2736, 0.3970, 0.8152, 0.9230, 0.1108],
                [0.4252, 0.4415, 0.6357, 0.7435, 0.1138],
                [0.0329, 0.8856, 0.8390, 0.3657, 0.0019],
                [0.0878, 0.7248, 0.1978, 0.0200, 0.0169],
                [0.8955, 0.4568, 0.8075, 0.9239, 0.2525],
            ],
        )
        (
            self.x_initial,
            self.tc_initial,
            self.half_span_initial,
            self.aero_center_initial,
            self.cf_initial,
            self.mach_initial,
            self.h_initial,
            self.throttle_initial,
            self.lift_initial,
            self.twist_initial,
            self.esf_initial,
        ) = base.get_initial_values()

    @abstractmethod
    def _jax_func(self, *args: Sequence[float]) -> float:
        """The JAX function used by the JAXDiscipline."""

    @staticmethod
    def _compute_polynomial_approximation(
        s_new: Array, s_ref: Array, a0: float, ai: Array, aij: Array
    ) -> Array:
        """Compute the polynomial coefficients.

        These coefficients characterize
        the behavior of certain synthetic variables and function modifiers.

        Args:
            s_new: The current values of the independent variables.
            s_ref: The initial values of the independent variables (5 variables at max).

        Returns:
            The value of the synthetic variables or function modifiers.
        """
        s_shifted = clip(s_new / s_ref, 0.75, 1.25) - 1.0
        return a0 + ai @ s_shifted + s_shifted.T @ aij @ s_shifted
