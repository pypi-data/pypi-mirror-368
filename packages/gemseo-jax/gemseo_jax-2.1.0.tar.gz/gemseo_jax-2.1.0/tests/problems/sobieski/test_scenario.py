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
"""Tests for the Sobieski's Supersonic Business Jet MDO benchmark written in JAX."""

from __future__ import annotations

from gemseo.problems.mdo.sobieski.core.design_space import SobieskiDesignSpace
from gemseo.problems.mdo.sobieski.disciplines import create_disciplines
from gemseo.scenarios.doe_scenario import DOEScenario
from numpy.testing import assert_allclose

from gemseo_jax.problems.sobieski.chain import JAXSobieskiChain


def test_solution():
    """Compare the JAX-based solution with the NumPy-based one."""
    jax_chain = JAXSobieskiChain()
    n_samples = 100
    scenario = DOEScenario(
        [jax_chain],
        "y_4",
        SobieskiDesignSpace(),
        formulation_name="MDF",
        maximize_objective=True,
    )
    scenario.add_constraint("g_1", "ineq")
    scenario.add_constraint("g_2", "ineq")
    scenario.add_constraint("g_3", "ineq")
    scenario.execute(algo_name="OT_HALTON", n_samples=n_samples)
    jax_dataset = scenario.to_dataset()

    scenario = DOEScenario(
        create_disciplines(),
        "y_4",
        SobieskiDesignSpace(),
        formulation_name="MDF",
        maximize_objective=True,
    )
    scenario.add_constraint("g_1", "ineq")
    scenario.add_constraint("g_2", "ineq")
    scenario.add_constraint("g_3", "ineq")
    scenario.execute(algo_name="OT_HALTON", n_samples=n_samples)
    numpy_dataset = scenario.to_dataset()

    v1 = jax_dataset.get_view(variable_names="-y_4").to_numpy()
    v2 = numpy_dataset.get_view(variable_names="-y_4").to_numpy()
    assert_allclose(v1, v2, rtol=1e-3)
