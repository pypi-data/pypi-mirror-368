# Copyright 2021 ISAE-SUPAERO, https://www.isae-supaero.fr/en/
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
"""Solve the Sellar MDO problem with JAX."""

from __future__ import annotations

from gemseo import configure_logger
from gemseo import create_scenario
from gemseo.core.mdo_functions.mdo_function import MDOFunction
from gemseo.problems.mdo.sellar.sellar_design_space import SellarDesignSpace

from gemseo_jax.jax_chain import JAXChain
from gemseo_jax.problems.sellar.sellar_1 import JAXSellar1
from gemseo_jax.problems.sellar.sellar_2 import JAXSellar2
from gemseo_jax.problems.sellar.sellar_system import JAXSellarSystem

configure_logger()

# %%
# Create the disciplines:
sellar_1 = JAXSellar1()
sellar_2 = JAXSellar2()
sellar_system = JAXSellarSystem()

# %%
# Make a `JAXChain` to assemble the 3 without reconverting to NumPy:
disciplines = [sellar_1, sellar_2, sellar_system]
jax_chain = JAXChain(disciplines, name="SellarChain")

# %%
# Add the differentiated outputs to reduce the computation graph of the Jacobian:
jax_chain.add_differentiated_outputs(["obj", "c_1", "c_2"])

# %%
# Compile functions, this takes an extra compilation time, but lowers the cost of
# re-evaluation:
jax_chain.compile_jit()

# %%
# Create the MDO scenario with an MDF formulation:
design_space = SellarDesignSpace()
scenario = create_scenario(
    jax_chain,
    "obj",
    design_space,
    formulation_name="MDF",
    main_mda_settings={"inner_mda_name": "MDAGaussSeidel"},
)
scenario.add_constraint(["c_1", "c_2"], MDOFunction.ConstraintType.INEQ)

# %%
# Execute the scenario and post-process the results:
scenario.execute(algo_name="SLSQP", max_iter=10)
scenario.post_process(post_name="OptHistoryView", save=False, show=True)
