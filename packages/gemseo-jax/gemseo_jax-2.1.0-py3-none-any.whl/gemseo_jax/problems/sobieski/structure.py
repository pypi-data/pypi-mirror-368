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
"""Structure discipline for the Sobieski's SSBJ use case."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Final

from jax.numpy import array
from jax.numpy import cos
from jax.numpy import log
from jax.numpy import ones
from jax.numpy import radians
from jax.numpy import sqrt
from numpy import array as np_array

from gemseo_jax.problems.sobieski.base import BaseJAXSobieskiDiscipline

if TYPE_CHECKING:
    from collections.abc import Sequence

    from jax import Array


class JAXSobieskiStructure(BaseJAXSobieskiDiscipline):
    """Structure discipline for the Sobieski's SSBJ use case."""

    _STRESS_LIMIT: Final[float] = 1.09
    _TWIST_UPPER_LIMIT: Final[float] = 1.04
    _TWIST_LOWER_LIMIT: Final[float] = 0.8

    def __init__(self) -> None:  # noqa: D107
        super().__init__()
        self.__bound1 = array([0.25, 0.25, 0.25, 0.25])
        self.__flag1 = array(
            [[0.95, 1.0, 1.1], [1.05, 1.0, 0.9], [1.05, 1.0, 0.9], [1.05, 1.0, 0.95]],
        )
        self.__s_initial_for_wing_twist = array(
            [
                self.x_initial,
                self.half_span_initial,
                self.aero_center_initial,
                self.lift_initial,
            ],
        )
        self.__s_initial_for_wing_weight = array([self.x_initial])
        self.__bound_secthick = array([0.008])
        self.__flag_secthick = array([[0.95, 1.0, 1.05]])
        self.__flag_stress = array(
            [
                [1.05, 1.0, 0.9],
                [0.95, 1.0, 1.05],
                [1.05, 1.0, 0.9],
                [0.95, 1.0, 1.05],
                [0.95, 1.0, 1.05],
            ],
        )
        self.__s_initial_for_constraints = array(
            [
                self.tc_initial,
                self.lift_initial,
                self.x_initial,
                self.half_span_initial,
                self.aero_center_initial,
            ],
        )

        self.__loc_ones = ones(5) * 0.1
        self.default_input_data["c_0"] = np_array([self.constants[0]])
        self.default_input_data["c_1"] = np_array([self.constants[1]])
        self.default_input_data["c_2"] = np_array([self.constants[2]])
        self._fww_coeff = 5 / 18 * 2 / 3 * 42.5
        self._a0_y12 = 1.0
        self._ai_y12 = array([0.3, -0.3, -0.3, -0.2])
        self.__aij_y12 = array(
            [
                [0.2, 0.0794, 0.16304, 0.1846],
                [0.0794, -0.2, -0.12714, -0.1487],
                [0.16304, -0.12714, -0.2, -0.07314],
                [0.1846, -0.1487, -0.07314, 0.0],
            ],
        )
        self.__a0_f0 = 1.0
        self.__ai_f0 = array([6.25])
        self.__aij_f0 = array([[0.0]])
        self.__a0_g1 = [1.0, 1.0, 1.0, 1.0, 1.0]
        self.__ai_g1 = [
            array([-0.75, 0.5, -0.75, 0.5, 0.5]),
            array([-0.5, 1 / 3, -0.5, 1 / 3, 1 / 3]),
            array([-0.375, 0.25, -0.375, 0.25, 0.25]),
            array([-0.3, 0.2, -0.3, 0.2, 0.2]),
            array([-0.25, 1 / 6, -0.25, 1 / 6, 1 / 6]),
        ]
        self.__aij_g1 = [
            array(
                [
                    [-1.25, -0.49625, -1.019, -1.15375, -0.1385],
                    [-0.49625, 0.0, 0.0, 0.0, 0.0],
                    [-1.019, 0.0, -1.25, -0.457125, -0.002375],
                    [-1.15375, 0.0, -0.457125, 0.0, 0.0],
                    [-0.1385, 0.0, -0.002375, 0.0, 0.0],
                ],
            ),
            array(
                [
                    [-0.55555556, -0.22055556, -0.45288889, -0.51277778, -0.06155556],
                    [-0.22055556, 0.0, 0.0, 0.0, 0.0],
                    [-0.45288889, 0.0, -0.55555556, -0.20316667, -0.00105556],
                    [-0.51277778, 0.0, -0.20316667, 0.0, 0.0],
                    [-0.06155556, 0.0, -0.00105556, 0.0, 0.0],
                ],
            ),
            array(
                [
                    [-0.3125, -0.1240625, -0.25475, -0.2884375, -0.034625],
                    [-0.1240625, 0.0, 0.0, 0.0, 0.0],
                    [-0.25475, 0.0, -0.3125, -0.11428125, -0.00059375],
                    [-0.2884375, 0.0, -0.11428125, 0.0, 0.0],
                    [-0.034625, 0.0, -0.00059375, 0.0, 0.0],
                ],
            ),
            array(
                [
                    [-0.2, -0.0794, -0.16304, -0.1846, -0.02216],
                    [-0.0794, 0.0, 0.0, 0.0, 0.0],
                    [-0.16304, 0.0, -0.2, -0.07314, -0.00038],
                    [-0.1846, 0.0, -0.07314, 0.0, 0.0],
                    [-0.02216, 0.0, -0.00038, 0.0, 0.0],
                ],
            ),
            array(
                [
                    [-0.13888889, -0.05513889, -0.11322222, -0.12819444, -0.01538889],
                    [-0.05513889, 0.0, 0.0, 0.0, 0.0],
                    [-0.11322222, 0.0, -0.13888889, -0.05079167, -0.00026389],
                    [-0.12819444, 0.0, -0.05079167, 0.0, 0.0],
                    [-0.01538889, 0.0, -0.00026389, 0.0, 0.0],
                ],
            ),
        ]

    def _jax_func(
        self,
        x_shared: Sequence[float],
        y_21: Sequence[float],
        y_31: Sequence[float],
        x_1: Sequence[float],
        c_0: Sequence[float],
        c_1: Sequence[float],
        c_2: Sequence[float],
    ) -> tuple[Array, Array, Array, Array, Array]:
        """Compute the structural outputs and the structural constraints.

        Args:
            x_shared: The values of the shared design variables,
                where ``x_shared[0]`` is the thickness-to-chord ratio,
                ``x_shared[1]`` is the altitude,
                ``x_shared[2]`` is the Mach number,
                ``x_shared[3]`` is the aspect ratio,
                ``x_shared[4]`` is the wing sweep and
                ``x_shared[5]`` is the wing surface area.
            y_21: The lift coefficient.
            y_31: The engine weight.
            x_1: The wing taper ratio ``x_1[0]``
                and the wingbox x-sectional area ``x_1[1]``.
            c_0: The minimum fuel weight.
                If ``None``, use :meth:`.SobieskiBase.constants`.
            c_1: The miscellaneous weight.
                If ``None``, use :meth:`.SobieskiBase.constants`.
            c_2: The maximum load factor.
                If ``None``, use :meth:`.SobieskiBase.constants`.

        Returns:
            The structural outputs and the structural constraints.
        """
        tc_ratio = x_shared[0]
        aspect_ratio = x_shared[3]
        sweep = x_shared[4]
        wing_area = x_shared[5]
        taper_ratio = x_1[0]
        wingbox_area = x_1[1]
        lift = y_21[0]
        engine_mass = y_31[0]
        c_0 = c_0[0]
        c_1 = c_1[0]
        c_2 = c_2[0]

        aero_center = (1.0 + 2.0 * taper_ratio) / (3.0 * (1 + taper_ratio))
        half_span = sqrt(aspect_ratio * wing_area) * 0.5

        y_12 = self._compute_polynomial_approximation(
            array([wingbox_area, half_span, aero_center, lift]),
            self.__s_initial_for_wing_twist,
            self._a0_y12,
            self._ai_y12,
            self.__aij_y12,
        )

        s_new = array([wingbox_area])
        f_o = self._compute_polynomial_approximation(
            s_new,
            self.__s_initial_for_wing_weight,
            self.__a0_f0,
            self.__ai_f0,
            self.__aij_f0,
        )
        wing_weight_coeff = (
            0.0051
            * ((lift * c_2) ** 0.557)
            * (wing_area**0.649)
            * (aspect_ratio**0.5)
            * (tc_ratio**-0.4)
            * ((1 + taper_ratio) ** 0.1)
            * (cos(radians(sweep)) ** -1.0)
            * ((0.1875 * wing_area) ** 0.1)
        )
        thickness = tc_ratio * sqrt(wing_area / aspect_ratio)
        y_1_i1 = c_0 + self._fww_coeff * wing_area * thickness
        y_11 = y_1_i1  # Fuel weight
        y_10 = c_1 + wing_weight_coeff * f_o + y_1_i1 + engine_mass
        y_1 = array([y_10, y_11, y_12])

        # This is the mass term in the Breguet range equation.
        y_11 = log(y_10 / (y_10 - y_11))

        s_new = array(
            [tc_ratio, lift, wingbox_area, half_span, aero_center],
        )
        g_1 = [
            self._compute_polynomial_approximation(
                s_new,
                self.__s_initial_for_constraints,
                self.__a0_g1[i],
                self.__ai_g1[i],
                self.__aij_g1[i],
            )
            for i in range(5)
        ]
        g_1.append(y_12)
        g_1 = array(g_1)

        y_14 = array([y_10, y_1[1]])
        y_12 = array([y_10, y_12])
        g_1 = array(
            [
                g_1[0] - self._STRESS_LIMIT,
                g_1[1] - self._STRESS_LIMIT,
                g_1[2] - self._STRESS_LIMIT,
                g_1[3] - self._STRESS_LIMIT,
                g_1[4] - self._STRESS_LIMIT,
                g_1[5] - self._TWIST_UPPER_LIMIT,
                self._TWIST_LOWER_LIMIT - g_1[5],
            ],
        )

        return y_1, y_11, y_12, y_14, g_1
