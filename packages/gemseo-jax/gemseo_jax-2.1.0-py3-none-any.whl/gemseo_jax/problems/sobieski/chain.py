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
"""Chain of the four disciplines of the Sobieski's SSBJ use case."""

from __future__ import annotations

from gemseo.problems.mdo.sobieski.core.problem import SobieskiProblem

from gemseo_jax.jax_chain import JAXChain
from gemseo_jax.problems.sobieski.aerodynamics import JAXSobieskiAerodynamics
from gemseo_jax.problems.sobieski.mission import JAXSobieskiMission
from gemseo_jax.problems.sobieski.propulsion import JAXSobieskiPropulsion
from gemseo_jax.problems.sobieski.structure import JAXSobieskiStructure


class JAXSobieskiChain(JAXChain):
    """Chain of the four disciplines of the Sobieski's SSBJ use case."""

    def __init__(self) -> None:  # noqa: D102 D107
        disciplines = [
            JAXSobieskiAerodynamics(),
            JAXSobieskiStructure(),
            JAXSobieskiPropulsion(),
            JAXSobieskiMission(),
        ]
        super().__init__(disciplines)
        self.default_input_data.update(
            SobieskiProblem().get_default_inputs(self.input_grammar.names)
        )
        self.add_differentiated_inputs(["x_shared", "x_1", "x_2", "x_3"])
        self.add_differentiated_outputs(["y_4", "g_1", "g_2", "g_3"])
        self.compile_jit()
