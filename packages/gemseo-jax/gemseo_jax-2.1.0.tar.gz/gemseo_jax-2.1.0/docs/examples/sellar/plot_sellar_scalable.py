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
"""Analysis of the scalable Sellar problem with JAX."""

from __future__ import annotations

from datetime import timedelta
from timeit import default_timer
from typing import TYPE_CHECKING

from gemseo import configure
from gemseo import configure_logger
from gemseo import create_mda
from gemseo.core.discipline.discipline import Discipline
from gemseo.problems.mdo.sellar.sellar_1 import Sellar1
from gemseo.problems.mdo.sellar.sellar_2 import Sellar2
from gemseo.problems.mdo.sellar.sellar_system import SellarSystem
from gemseo.problems.mdo.sellar.utils import get_initial_data
from matplotlib.pyplot import show
from matplotlib.pyplot import subplots
from numpy import array
from numpy.random import default_rng

from gemseo_jax.jax_chain import DifferentiationMethod
from gemseo_jax.problems.sellar.sellar_1 import JAXSellar1
from gemseo_jax.problems.sellar.sellar_2 import JAXSellar2
from gemseo_jax.problems.sellar.sellar_chain import JAXSellarChain
from gemseo_jax.problems.sellar.sellar_system import JAXSellarSystem

if TYPE_CHECKING:
    from gemseo.mda.base_mda import BaseMDA
    from gemseo.typing import RealArray

# Deactivate some checkers to speed up calculations in presence of cheap disciplines.
configure(False, False, True, False, False, False, False)
configure_logger()


def get_random_input_data(n: int) -> dict[str, RealArray]:
    """Return a random input value for [JAX]SellarSystem."""
    r_float = default_rng().random()
    return {
        name: 1.5 * r_float * value for name, value in get_initial_data(n=n).items()
    }


def get_numpy_disciplines(n: int) -> list[Discipline]:
    """Return the NumPy-based Sellar disciplines."""
    return [
        Sellar1(n=n),
        Sellar2(n=n),
        SellarSystem(n=n),
    ]


def get_jax_disciplines(
    n: int, differentiation_method=DifferentiationMethod.AUTO
) -> list[Discipline]:
    """Return the JAX-based Sellar disciplines."""
    disciplines = [
        JAXSellar1(n=n, differentiation_method=differentiation_method),
        JAXSellar2(n=n, differentiation_method=differentiation_method),
        JAXSellarSystem(n=n, differentiation_method=differentiation_method),
    ]
    for disc in disciplines:
        disc.set_cache(Discipline.CacheType.SIMPLE)
        disc.compile_jit()

    return disciplines


# %%
# # Initial setup for comparison
# Here we intend to compare the original NumPy implementation with the JAX one.
# We then need to create the original MDA and one JAX MDA for each configuration we're
# testing. In this example we compare the performance of the JAXChain encapsulation and
# also the forward and reverse modes for automatic differentiation.
def get_analytical_mda(n: int, mda_name="MDAGaussSeidel", max_mda_iter=5) -> BaseMDA:
    """Return the Sellar MDA with analytical NumPy Jacobian."""
    mda = create_mda(
        mda_name=mda_name,
        disciplines=get_numpy_disciplines(n),
        max_mda_iter=max_mda_iter,
        name="Analytical SellarChain",
    )
    mda.set_cache(Discipline.CacheType.SIMPLE)
    return mda


def get_forward_ad_mda(n: int, mda_name="MDAGaussSeidel", max_mda_iter=5) -> BaseMDA:
    """Return the Sellar MDA with JAX forward-mode AD Jacobian."""
    mda = create_mda(
        mda_name=mda_name,
        disciplines=get_jax_disciplines(n, DifferentiationMethod.FORWARD),
        max_mda_iter=max_mda_iter,
        name="JAX SellarChain",
    )
    mda.set_cache(Discipline.CacheType.SIMPLE)
    return mda


def get_chained_forward_ad_mda(
    n: int, mda_name="MDAGaussSeidel", max_mda_iter=5
) -> BaseMDA:
    """Return the Sellar MDA with JAXChain encapsulation and forward-mode Jacobian."""
    discipline = JAXSellarChain(
        n=n,
        differentiation_method=DifferentiationMethod.FORWARD,
    )
    discipline.add_differentiated_inputs(discipline.input_grammar.names)
    discipline.add_differentiated_outputs(discipline.output_grammar.names)

    mda = create_mda(
        mda_name=mda_name,
        disciplines=[discipline],
        max_mda_iter=max_mda_iter,
        name="JAX SellarChain",
    )
    mda.set_cache(Discipline.CacheType.SIMPLE)
    return mda


def get_reverse_ad_mda(n: int, mda_name="MDAGaussSeidel", max_mda_iter=5) -> BaseMDA:
    """Return the Sellar MDA with JAX reverse-mode AD Jacobian."""
    mda = create_mda(
        mda_name=mda_name,
        disciplines=get_jax_disciplines(n, DifferentiationMethod.REVERSE),
        max_mda_iter=max_mda_iter,
        name="JAX SellarChain",
    )
    mda.set_cache(Discipline.CacheType.SIMPLE)
    return mda


def get_chained_reverse_ad_mda(
    n: int, mda_name="MDAGaussSeidel", max_mda_iter=5
) -> BaseMDA:
    """Return the Sellar MDA with JAXChain encapsulation and reverse-mode Jacobian."""
    discipline = JAXSellarChain(
        n=n,
        differentiation_method=DifferentiationMethod.REVERSE,
    )
    discipline.add_differentiated_inputs(discipline.input_grammar.names)
    discipline.add_differentiated_outputs(discipline.output_grammar.names)

    mda = create_mda(
        mda_name=mda_name,
        disciplines=[discipline],
        max_mda_iter=max_mda_iter,
        name="JAX SellarChain",
    )
    mda.set_cache(Discipline.CacheType.SIMPLE)
    return mda


mdas = {
    "MDOChain[NumPy] - Analytical": get_analytical_mda,  # this is the reference
    "JAXChain - Forward AD": get_chained_forward_ad_mda,
    "JAXChain - Reverse AD": get_chained_reverse_ad_mda,
    "MDOChain[JAX] - Forward AD": get_forward_ad_mda,
    "MDOChain[JAX] - Reverse AD": get_reverse_ad_mda,
}


# %%
# # Execution and linearization scalability
#
# Let's make a function to execute and linearize an MDA, while logging times.
# Also, we run several repetitions to avoid noisy results:
def run_and_log(get_mda, dimension, n_repeat=7, **mda_options):
    mda = get_mda(dimension, **mda_options)
    t0 = default_timer()
    for _i in range(n_repeat):
        mda.execute({
            name: value
            for name, value in get_random_input_data(dimension).items()
            if name in mda.input_grammar.names
        })
    t1 = default_timer()
    t_execute = timedelta(seconds=t1 - t0) / float(n_repeat)

    t2 = default_timer()
    for _i in range(n_repeat):
        mda.linearize({
            name: value
            for name, value in get_random_input_data(dimension).items()
            if name in mda.input_grammar.names
        })
    t3 = default_timer()
    t_linearize = timedelta(seconds=t3 - t2) / float(n_repeat)
    return t_execute, t_linearize


# %%
# # Run the MDA for each of the mdas, for several number of dimensions
dimensions = [1, 10, 100, 1000]
times = {}
mda_config = {"mda_name": "MDAGaussSeidel", "max_mda_iter": 1}
for mda_name, mda_func in mdas.items():
    time_exec = []
    time_lin = []
    for dimension in dimensions:
        t_e, t_l = run_and_log(mda_func, dimension, **mda_config)
        time_exec.append(t_e)
        time_lin.append(t_l)
    times[mda_name] = (array(time_exec), array(time_lin))

# %%
# Now let's visualize our results:
mda_ref = next(iter(mdas.keys()))
t_ref = times[mda_ref]
speedup = {
    mda_name: (t_e / t_ref[0], t_l / t_ref[1]) for mda_name, (t_e, t_l) in times.items()
}

fig, axes = subplots(2, 1, layout="constrained", figsize=(6, 8))
fig.suptitle("Speedup compared to NumPy Analytical")
for mda_name in mdas:
    linestyle = ":" if mda_name == mda_ref else "-"
    speedup_e, speedup_l = speedup[mda_name]
    axes[0].plot(dimensions, speedup_e, linestyle, label=mda_name)
    axes[1].plot(dimensions, speedup_l, linestyle, label=mda_name)
axes[0].legend(bbox_to_anchor=(0.9, -0.1))
axes[0].set_ylabel("Execution")
axes[0].set_xscale("log")
axes[1].set_ylabel("Linearization")
axes[1].set_xlabel("Dimension")
axes[1].set_xscale("log")
show()

# %%
# # Conclusion
# JAX AD is as fast as analytical derivatives with NumPy.
# Encapsulation with JAXChain slows execution, but speeds-up linearization.
# Speedup is maintained even at higher dimensions.
