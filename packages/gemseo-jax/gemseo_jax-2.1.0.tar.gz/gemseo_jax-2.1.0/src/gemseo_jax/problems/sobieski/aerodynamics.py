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
"""Aerodynamics discipline for the Sobieski's SSBJ use case."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Final

import jax
from jax import Array
from jax.numpy import array
from jax.numpy import cos
from jax.numpy import exp
from jax.numpy import radians
from jax.numpy import sqrt
from numpy import array as np_array

from gemseo_jax.problems.sobieski.base import BaseJAXSobieskiDiscipline

if TYPE_CHECKING:
    from collections.abc import Sequence


class JAXSobieskiAerodynamics(BaseJAXSobieskiDiscipline):
    """Aerodynamics discipline for the Sobieski's SSBJ use case."""

    PRESSURE_GRADIENT_LIMIT: Final[float] = 1.04

    def __init__(self) -> None:  # noqa: D107
        super().__init__()
        self.__flag1 = array([[0.95, 1.0, 1.05], [0.95, 1.0, 1.05]])
        self.__bound1 = array([0.25, 0.25])
        self.__flag2 = array([[1.0025, 1.0, 1.0025]])
        self.__bound2 = array([0.25])
        self.__flag3 = array([[0.95, 1.0, 1.05]])
        self.__bound3 = array([0.25])
        self.__esf_cf_initial = array([self.esf_initial, self.cf_initial])
        self.__twist_initial = array([self.twist_initial])
        self.__tc_initial = array([self.tc_initial])
        self.default_input_data["c_4"] = np_array([self.constants[4]])
        self.__a0_fo1 = 1.0
        self.__ai_fo1 = array([0.2, 0.2])
        self.__aij_fo1 = array([[0.0, 0.0], [0.0, 0.0]])
        self.__a0_fo2 = 1.0
        self.__ai_fo2 = array([0.0])
        self.__aij_fo2 = array([[0.02]])
        self.__a0_g2 = 1.0
        self.__ai_g2 = array([0.2])
        self.__aij_g2 = array([[0.0]])

    def _jax_func(
        self,
        x_shared: Sequence[float],
        x_2: Sequence[float],
        y_12: Sequence[float],
        y_32: Sequence[float],
        c_4: Sequence[float],
    ) -> tuple[Array, Array, Array, Array, Array]:
        """Compute the drag and the lift-to-drag ratio.

        Args:
            x_shared: The values of the shared design variables,
                where ``x_shared[0]`` is the thickness/chord ratio,
                ``x_shared[1]`` is the altitude,
                ``x_shared[2]`` is the Mach number,
                ``x_shared[3]`` is the aspect ratio,
                ``x_shared[4]`` is the wing sweep and
                ``x_shared[5]`` is the wing surface area.
            y_12: The coupling variable from the structure disciplines,
                where ``y_12[0]`` is the total aircraft weight
                and ``y_12[1]`` is the wing twist.
            y_32: The coupling variable (engine scale factor)
                from the propulsion discipline,
            x_2: The friction coefficient.
            c_4: The minimum drag coefficient.
                If ``None``, use :meth:`.SobieskiBase.constants`.

        Returns:
            The aerodynamics outputs:
                - ``y_2``: The outputs of the aerodynamics analysis:
                    - ``y_2[0]``: the lift,
                    - ``y_2[1]``: the drag,
                    - ``y_2[2]``: the lift/drag ratio,
                - ``y_21``: The coupling variable (lift) for the structure discipline,
                - ``y_23``: The coupling variable (drag) for the propulsion discipline,
                - ``y_24``: The coupling variable (lift/drag ratio)
                   for the mission discipline,
                - ``g_2``: The pressure gradient to be constrained.
        """
        tc_ratio = x_shared[0]
        altitude = x_shared[1]
        mach = x_shared[2]
        sweep = x_shared[4]
        wing_area = x_shared[5]
        ac_mass = y_12[0]
        twist = y_12[1]
        esf = y_32[0]
        c_f = x_2[0]
        c_4 = c_4[0]

        velocity = jax.lax.cond(
            altitude < 36089.0,
            lambda m, a: m * 1116.39 * sqrt(1 - 6.875e-6 * a),
            lambda m, a: m * 968.1,
            mach,
            altitude,
        )
        rho = jax.lax.cond(
            altitude < 36089.0,
            lambda a: 2.377e-3 * (1 - 6.875e-6 * a) ** 4.2561,
            lambda a: 2.377e-3 * 0.2971 * exp((36089.0 - a) / 20806.7),
            altitude,
        )

        rhov2 = rho * velocity * velocity
        lift_coeff = ac_mass / (0.5 * rhov2 * wing_area)

        # Modification of CDmin for ESF and Cf
        fo1 = self._compute_polynomial_approximation(
            array([esf, c_f]),
            self.__esf_cf_initial,
            self.__a0_fo1,
            self.__ai_fo1,
            self.__aij_fo1,
        )

        # Modification of drag_coeff for wing twist
        fo2 = self._compute_polynomial_approximation(
            array([twist]),
            self.__twist_initial,
            self.__a0_fo2,
            self.__ai_fo2,
            self.__aij_fo2,
        )

        cdmin = (
            c_4 * fo1 + 3.05 * tc_ratio ** (5.0 / 3.0) * (cos(radians(sweep))) ** 1.5
        )
        k_aero = (mach**2 - 1) * cos(radians(sweep)) / (4.0 * sqrt(sweep**2 - 1) - 2)
        drag_coeff = fo2 * (cdmin + k_aero * lift_coeff * lift_coeff)
        drag = 0.5 * rhov2 * drag_coeff * wing_area

        y_2 = array([ac_mass, drag, lift_coeff / drag_coeff])
        y_23 = array([y_2[1]])
        y_24 = array([y_2[2]])
        y_21 = array([y_2[0]])

        # Computation of total drag of A/C
        # adverse pressure gradient
        g_2 = (
            self._compute_polynomial_approximation(
                array([tc_ratio]),
                self.__tc_initial,
                self.__a0_g2,
                self.__ai_g2,
                self.__aij_g2,
            )
            - self.PRESSURE_GRADIENT_LIMIT
        )

        return y_2, y_21, y_23, y_24, g_2
