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
"""Mission discipline for the Sobieski's SSBJ use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

import jax
from jax.numpy import log
from jax.numpy import sqrt

from gemseo_jax.problems.sobieski.base import BaseJAXSobieskiDiscipline

if TYPE_CHECKING:
    from collections.abc import Sequence


class JAXSobieskiMission(BaseJAXSobieskiDiscipline):
    """Mission discipline for the Sobieski's SSBJ use case."""

    def _jax_func(
        self,
        x_shared: Sequence[float],
        y_14: Sequence[float],
        y_24: Sequence[float],
        y_34: Sequence[float],
    ) -> float:
        """Compute the range.

        Args:
            x_shared: The shared design variables.
            y_14: The total aircraft weight ``y_14[0]`` and the fuel weight ``y_14[1]``.
            y_24: The lift-over-drag ratio.
            y_34: The specific fuel consumption.

        Returns:
            The range.
        """
        altitude = x_shared[1]
        mach = x_shared[2]
        w_t = y_14[0]
        w_f = y_14[1]
        cl_cd = y_24[0]
        sfc = y_34[0]
        sqrt_theta = jax.lax.cond(
            altitude < 36089.0,
            lambda x: sqrt(1 - 6.875e-06 * x),
            lambda x: sqrt(0.7519),
            altitude,
        )
        y_4 = ((mach * cl_cd) * 661.0 * sqrt_theta / sfc) * log(w_t / (w_t - w_f))
        return y_4  # noqa: RET504
