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
"""Chain of the three disciplines of the Sellar problem in JAX."""

from __future__ import annotations

from typing import Any

from gemseo.problems.mdo.sellar.variables import C_1
from gemseo.problems.mdo.sellar.variables import C_2
from gemseo.problems.mdo.sellar.variables import OBJ

from gemseo_jax.jax_chain import JAXChain
from gemseo_jax.problems.sellar.sellar_1 import JAXSellar1
from gemseo_jax.problems.sellar.sellar_2 import JAXSellar2
from gemseo_jax.problems.sellar.sellar_system import JAXSellarSystem


class JAXSellarChain(JAXChain):
    """Chain of the three disciplines of the Sellar problem in JAX."""

    def __init__(
        self, n: int = 1, k: float = 1.0, pre_run: bool = True, **kwargs: Any
    ) -> None:
        """
        Args:
            pre_run: Whether to pre run the jit.
            **kwargs: The arguments passed to JAXChain.
        """  # noqa: D205  D212 D415
        disciplines = [
            JAXSellar1(n=n, k=k),
            JAXSellar2(n=n, k=k),
            JAXSellarSystem(n=n),
        ]
        super().__init__(disciplines, **kwargs)
        self.add_differentiated_outputs([OBJ, C_1, C_2])
        self.compile_jit(pre_run=pre_run)
