# Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com
#
# This work is licensed under a BSD 0-Clause License.
#
# Permission to use, copy, modify, and/or distribute this software
# for any purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING
# FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
# WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""Compare JAX and NumPy for the resolution of the Sobieski's SSBJ problem."""

from __future__ import annotations

from gemseo import configure
from gemseo import configure_logger
from gemseo.problems.mdo.sobieski.core.design_space import SobieskiDesignSpace
from gemseo.problems.mdo.sobieski.disciplines import SobieskiAerodynamics
from gemseo.problems.mdo.sobieski.disciplines import SobieskiMission
from gemseo.problems.mdo.sobieski.disciplines import SobieskiPropulsion
from gemseo.problems.mdo.sobieski.disciplines import SobieskiStructure
from gemseo.scenarios.doe_scenario import DOEScenario
from gemseo.scenarios.mdo_scenario import MDOScenario

from gemseo_jax.problems.sobieski.chain import JAXSobieskiChain

# Deactivate some checkers to speed up calculations in presence of cheap disciplines.
configure(False, False, True, False, False, False, False)

configure_logger()

# %%
# ## DOE
#
# ### MDF with MDAJacobi
#
# #### Solve the Sobieski's SSBJ problem with JAX
chain = JAXSobieskiChain()
doe_scenario = DOEScenario(
    [chain],
    "y_4",
    SobieskiDesignSpace(),
    maximize_objective=True,
    formulation_name="MDF",
)
doe_scenario.add_constraint("g_1", "ineq")
doe_scenario.add_constraint("g_2", "ineq")
doe_scenario.add_constraint("g_3", "ineq")
doe_scenario.execute(algo_name="OT_OPT_LHS", n_samples=100)

# %%
# #### Solve the Sobieski's SSBJ problem with NumPy
doe_scenario = DOEScenario(
    [
        SobieskiStructure(),
        SobieskiAerodynamics(),
        SobieskiPropulsion(),
        SobieskiMission(),
    ],
    "y_4",
    SobieskiDesignSpace(),
    maximize_objective=True,
    formulation_name="MDF",
)
doe_scenario.add_constraint("g_1", "ineq")
doe_scenario.add_constraint("g_2", "ineq")
doe_scenario.add_constraint("g_3", "ineq")
doe_scenario.execute(algo_name="OT_OPT_LHS", n_samples=100)

# %%
# #### Conclusion
# JAX is about 3 times faster than NumPy
# in the case of a sampling loop with a Jacobi MDA.

# %%
# ### MDF with MDAGaussSeidel
#
# #### Solve the Sobieski's SSBJ problem with JAX
chain = JAXSobieskiChain()
doe_scenario = DOEScenario(
    [chain],
    "y_4",
    SobieskiDesignSpace(),
    maximize_objective=True,
    formulation_name="MDF",
    main_mda_settings={"inner_mda_name": "MDAGaussSeidel"},
)
doe_scenario.add_constraint("g_1", "ineq")
doe_scenario.add_constraint("g_2", "ineq")
doe_scenario.add_constraint("g_3", "ineq")
doe_scenario.execute(algo_name="OT_OPT_LHS", n_samples=100)

# %%
# #### Solve the Sobieski's SSBJ problem with NumPy
doe_scenario = DOEScenario(
    [
        SobieskiStructure(),
        SobieskiAerodynamics(),
        SobieskiPropulsion(),
        SobieskiMission(),
    ],
    "y_4",
    SobieskiDesignSpace(),
    maximize_objective=True,
    formulation_name="MDF",
    main_mda_settings={"inner_mda_name": "MDAGaussSeidel"},
)
doe_scenario.add_constraint("g_1", "ineq")
doe_scenario.add_constraint("g_2", "ineq")
doe_scenario.add_constraint("g_3", "ineq")
doe_scenario.execute(algo_name="OT_OPT_LHS", n_samples=100)

# %%
# #### Conclusion
# JAX is about 3 times faster than NumPy
# in the case of a sampling loop with a Gauss-Seidel MDA.

# %%
# ## Optimization
#
# ### MDF with MDAJacobi
#
# #### Solve the Sobieski's SSBJ problem with JAX
chain = JAXSobieskiChain()
mod_scenario = MDOScenario(
    [chain],
    "y_4",
    SobieskiDesignSpace(),
    maximize_objective=True,
    formulation_name="MDF",
)
mod_scenario.add_constraint("g_1", "ineq")
mod_scenario.add_constraint("g_2", "ineq")
mod_scenario.add_constraint("g_3", "ineq")
mod_scenario.execute(algo_name="NLOPT_COBYLA", max_iter=100)

# %%
# #### Solve the Sobieski's SSBJ problem with NumPy
mod_scenario = MDOScenario(
    [
        SobieskiStructure(),
        SobieskiAerodynamics(),
        SobieskiPropulsion(),
        SobieskiMission(),
    ],
    "y_4",
    SobieskiDesignSpace(),
    maximize_objective=True,
    formulation_name="MDF",
)
mod_scenario.add_constraint("g_1", "ineq")
mod_scenario.add_constraint("g_2", "ineq")
mod_scenario.add_constraint("g_3", "ineq")
mod_scenario.execute(algo_name="NLOPT_COBYLA", max_iter=100)

# %%
# #### Conclusion
# JAX is about 4 times faster than NumPy
# in the case of an optimization loop with a Jacobi MDA.

# %%
# ### MDF with MDAGaussSeidel
#
# #### Solve the Sobieski's SSBJ problem with JAX
chain = JAXSobieskiChain()
mod_scenario = MDOScenario(
    [chain],
    "y_4",
    SobieskiDesignSpace(),
    maximize_objective=True,
    formulation_name="MDF",
    main_mda_settings={"inner_mda_name": "MDAGaussSeidel"},
)
mod_scenario.add_constraint("g_1", "ineq")
mod_scenario.add_constraint("g_2", "ineq")
mod_scenario.add_constraint("g_3", "ineq")
mod_scenario.execute(algo_name="NLOPT_COBYLA", max_iter=100)

# %%
# #### Solve the Sobieski's SSBJ problem with NumPy
mod_scenario = MDOScenario(
    [
        SobieskiStructure(),
        SobieskiAerodynamics(),
        SobieskiPropulsion(),
        SobieskiMission(),
    ],
    "y_4",
    SobieskiDesignSpace(),
    maximize_objective=True,
    formulation_name="MDF",
    main_mda_settings={"inner_mda_name": "MDAGaussSeidel"},
)
mod_scenario.add_constraint("g_1", "ineq")
mod_scenario.add_constraint("g_2", "ineq")
mod_scenario.add_constraint("g_3", "ineq")
mod_scenario.execute(algo_name="NLOPT_COBYLA", max_iter=100)

# %%
# #### Conclusion
# JAX is about 3 times faster than NumPy
# in the case of an optimization loop with a Gauss-Seidel MDA.
