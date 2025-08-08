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
"""Experimenting with Sellar MDA with JAX."""

from __future__ import annotations

from datetime import timedelta
from logging import getLogger
from timeit import default_timer
from typing import TYPE_CHECKING

from gemseo import configure_logger
from gemseo import create_mda

from gemseo_jax.jax_chain import JAXChain
from gemseo_jax.problems.sellar.sellar_1 import JAXSellar1
from gemseo_jax.problems.sellar.sellar_2 import JAXSellar2
from gemseo_jax.problems.sellar.sellar_chain import JAXSellarChain
from gemseo_jax.problems.sellar.sellar_system import JAXSellarSystem

if TYPE_CHECKING:
    from gemseo.mda.base_mda import BaseMDA

LOGGER = getLogger(__name__)


configure_logger()

# %%
# There are many options when combining JAXDisciplines for execution:
#   - JAXChain encapsulation:
#       This wraps a set of disciplines and executes as a single monolithic one.
#       Pros: Execution and compilation are faster.
#       Cons: Incompatible with MDANewtonRaphson.
#
#   - .compile_jit():
#       This compiles the function used to compute outputs and Jacobian.
#       Pros: Faster execution.
#       Cons: Compilation time can exceed total execution if function is called
#       only few times.
#   Note: Compilation itself does not takes place in this method, but only once a
#   jit-compiled function is executed, that is why we may add a pre-run.
#       - pre-run:
#           Executes the output and Jacobian function once to ensure compilation.
#           Pros: Ensures benchmarks include only execution times.
#           Cons: Compilation time is included in the 1st evaluation.


# %%
# Create the disciplines with `AutoJAXDiscipline`:
def get_disciplines():
    """Get new instances of the disciplines of the Sellar problem."""
    return [JAXSellar1(), JAXSellar2(), JAXSellarSystem()]


# %%
# Create the function to run MDA and log execution times:
def execute_and_log_mda(name: str, mda_chain: BaseMDA) -> None:
    """Execute mda and log total execution time."""
    t0 = default_timer()
    mda_chain.execute()
    t1 = default_timer()
    # mda.plot_residual_history(show=True, save=False)
    LOGGER.info(
        "MDA execution %s: %s seconds.",
        name,
        timedelta(seconds=t1 - t0),
    )


# %%
# # No JAXChain encapsulation
#
# ## MDA over separate disciplines WITHOUT compilation
disciplines = get_disciplines()
mda = create_mda(
    "MDAChain",
    disciplines,  # separate disciplines
    inner_mda_name="MDAJacobi",
)
execute_and_log_mda("separate disciplines (no jit)", mda)

# %%
# ## MDA over separate disciplines WITH compilation WITHOUT pre-run
disciplines = get_disciplines()
for disc in disciplines:
    disc.compile_jit(pre_run=False)
mda = create_mda(
    "MDAChain",
    disciplines,  # separate disciplines
    inner_mda_name="MDAJacobi",
)
execute_and_log_mda("separate disciplines (jit, no pre-run)", mda)

# %%
# ## MDA over separate disciplines WITH compilation WITH pre-run (standard)
disciplines = get_disciplines()
for disc in disciplines:
    disc.compile_jit()
mda = create_mda(
    "MDAChain",
    disciplines,  # separate disciplines
    inner_mda_name="MDAJacobi",
)
execute_and_log_mda("separate disciplines (jit, pre-run)", mda)

# %%
# ## Conclusion
# MDA is 1.8x faster with JIT compilation. If compilation times are excluded from
# benchmark, the speedup is 10x!

# %%
# # With JAXChain encapsulation
#
# ## MDA over JAXChain WITHOUT compilation
jax_chain = JAXChain(get_disciplines())
mda = create_mda(
    "MDAChain",
    [jax_chain],  # chain as single discipline
    inner_mda_name="MDAJacobi",
)
execute_and_log_mda("chained disciplines (no jit)", mda)

# %%
# ## MDA over JAXChain WITH compilation WITHOUT pre-run
jax_chain = JAXSellarChain(pre_run=False)
mda = create_mda(
    "MDAChain",
    [jax_chain],  # chain as single discipline
    inner_mda_name="MDAJacobi",
)
execute_and_log_mda("chained disciplines (jit, no pre-run)", mda)

# %%
# ## MDA over JAXChain WITH compilation WITH pre-run
jax_chain = JAXSellarChain()
jax_chain.compile_jit()
mda = create_mda(
    "MDAChain",
    [jax_chain],  # chain as single discipline
    inner_mda_name="MDAJacobi",
)
execute_and_log_mda("chained disciplines (jit, pre-run)", mda)

# %%
# # Conclusion
# Encapsulation with JAXChain (without JIT) allows for 1.4x speedup.
# JIT compilation allows for 1.8x speedup relative to un-jitted JAXChain and 2.6x
# relative to un-jitted separate disciplines.
# If compilation times are excluded from benchmark, these speedups are 2.2x and 3.2x,
# respectively.
