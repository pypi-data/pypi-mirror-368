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
"""Propulsion discipline for the Sobieski's SSBJ use case."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Final

from jax.numpy import array
from numpy import array as np_array

from gemseo_jax.problems.sobieski.base import BaseJAXSobieskiDiscipline

if TYPE_CHECKING:
    from collections.abc import Sequence

    from jax import Array


class JAXSobieskiPropulsion(BaseJAXSobieskiDiscipline):
    """Propulsion discipline for the Sobieski's SSBJ use case."""

    _ESF_UPPER_LIMIT: Final[float] = 1.5
    _ESF_LOWER_LIMIT: Final[float] = 0.5
    _TEMPERATURE_LIMIT: Final[float] = 1.02

    def __init__(self) -> None:  # noqa: D107
        super().__init__()
        self.__s_initial = array([
            self.mach_initial,
            self.h_initial,
            self.throttle_initial,
        ])
        self.__flag_temp = array([[0.95, 1.0, 1.1], [1.05, 1.0, 0.9], [0.95, 1.0, 1.1]])
        self.__bound_temp = array([0.25, 0.25, 0.25])
        self.__throttle_coeff = 16168.6
        self.__sfc_coeff = array(
            [
                1.13238425638512,
                1.53436586044561,
                -0.00003295564466,
                -0.00016378694115,
                -0.31623315541888,
                0.00000410691343,
                -0.00005248000590,
                -0.00000000008574,
                0.00000000190214,
                0.00000001059951,
            ],
        )
        self.__thua_coeff = array(
            [
                11483.7822254806,
                10856.2163466548,
                -0.5080237941,
                3200.157926969,
                -0.1466251679,
                0.0000068572,
            ],
        )
        self.default_input_data["c_3"] = np_array([self.constants[3]])
        self.__a0_g31 = 1.0
        self.__ai_g31 = array([0.3, -0.3, 0.3])
        self.__aij_g31 = array(
            [
                [0.2, 0.0794, 0.16304],
                [0.0794, -0.2, -0.12714],
                [0.16304, -0.12714, 0.2],
            ],
        )

    def _jax_func(
        self,
        x_shared: Sequence[float],
        y_23: Sequence[float],
        x_3: Sequence[float],
        c_3: Sequence[float],
    ) -> tuple[Array, Array, Array, Array, Array]:
        """Compute the fuel consumption, engine weight and engine scale factor.

        Args:
            x_shared: The values of the shared design variables,
                where ``x_shared[0]`` is the thickness/chord ratio,
                ``x_shared[1]`` is the altitude,
                ``x_shared[2]`` is the Mach number,
                ``x_shared[3]`` is the aspect ratio,
                ``x_shared[4]`` is the wing sweep and
                ``x_shared[5]`` is the wing surface area.
            y_23: The drag coefficient.
            x_3: The throttle.
            c_3: The reference engine weight.
                If ``None``, use :meth:`.SobieskiBase.constants`.

        Returns:
            The propulsion outputs:
                - ``y_3``: The outputs of the propulsion analysis:
                    - ``y_3[0]``: the specific fuel consumption,
                    - ``y_3[1]``: the engine weight,
                    - ``y_3[2]``: the engine scale factor,
                - ``y_34``: ``y_3[0]``
                - ``y_31``: ``y_3[1]``
                - ``y_32``: ``y_3[2]``
                - ``g_3``: The propulsion outputs to be constrained:
                    - ``g_3[0]``: the engine scale factor,
                    - ``g_3[1]``: the engine temperature,
                    - ``g_3[2]``: the throttle setting.
        """
        altitude = x_shared[1]
        mach = x_shared[2]
        adim_throttle = x_3[0]
        drag = y_23[0]
        c_3 = c_3[0]

        throttle = adim_throttle * self.__throttle_coeff
        y_34 = array(
            [
                self.__sfc_coeff[0]
                + self.__sfc_coeff[1] * mach
                + self.__sfc_coeff[2] * altitude
                + self.__sfc_coeff[3] * throttle
                + self.__sfc_coeff[4] * mach**2
                + 2 * altitude * mach * self.__sfc_coeff[5]
                + 2 * throttle * mach * self.__sfc_coeff[6]
                + self.__sfc_coeff[7] * altitude**2
                + 2 * throttle * altitude * self.__sfc_coeff[8]
                + self.__sfc_coeff[9] * throttle**2
            ],
        )
        g_30 = y_32 = drag / (3.0 * throttle)
        y_31 = c_3 * (y_32**1.05) * 3
        y_3 = array([y_34[0], y_31, y_32])

        g_31 = self._compute_polynomial_approximation(
            array([mach, altitude, adim_throttle]),
            self.__s_initial,
            self.__a0_g31,
            self.__ai_g31,
            self.__aij_g31,
        )
        throttle_ua = (
            self.__thua_coeff[0]
            + self.__thua_coeff[1] * mach
            + self.__thua_coeff[2] * altitude
            + self.__thua_coeff[3] * mach**2
            + 2 * self.__thua_coeff[4] * mach * altitude
            + self.__thua_coeff[5] * altitude**2
        )
        g_32 = throttle / throttle_ua - 1.0

        g_3 = array([
            g_30 - self._ESF_UPPER_LIMIT,
            self._ESF_LOWER_LIMIT - g_30,
            g_32,
            g_31 - self._TEMPERATURE_LIMIT,
        ])

        return y_3, y_34, y_31, y_32, g_3
