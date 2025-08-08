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
"""Create a JAXDiscipline from a discipline using JAX."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gemseo.core.discipline.discipline import Discipline
from jax.numpy import sqrt
from numpy import array

from gemseo_jax.utils import create_jax_discipline_from_discipline

if TYPE_CHECKING:
    from gemseo_jax.jax_discipline import DataType

# %%
# This short example illustrates
# how to create a [JAXDiscipline][gemseo_jax.jax_discipline.JAXDiscipline]
# from a standard [Discipline][gemseo.core.discipline.discipline.Discipline]
# using JAX instead of NumPy and SciPy.
#
# First,
# let us create such as discipline
# whose single output is the square root of its single input multiplied by 2:


class DummyDisciplineUsingJAX(Discipline):
    """A dummy discipline using JAX."""

    default_grammar_type = Discipline.GrammarType.SIMPLER

    def __init__(self) -> None:
        super().__init__()
        self.io.input_grammar.update_from_names(("in",))
        self.io.output_grammar.update_from_names(("out",))
        self.io.input_grammar.defaults = {"in": array([1.0])}

    def _run(self, input_data: dict[str, DataType]) -> dict[str, DataType]:
        return {"out": 2 * sqrt(input_data["in"])}


discipline_using_jax = DummyDisciplineUsingJAX()

# %%
# Then,
# we use the function
# [create_jax_discipline_from_discipline][gemseo_jax.utils.create_jax_discipline_from_discipline]
# to create a [JAXDiscipline][gemseo_jax.jax_discipline.JAXDiscipline]
jax_discipline = create_jax_discipline_from_discipline(discipline_using_jax)
jax_discipline.add_differentiated_inputs(["in"])
jax_discipline.add_differentiated_outputs(["out"])

# %%
# Now,
# you can use `jax_discipline`
# as any [JAXDiscipline][gemseo_jax.jax_discipline.JAXDiscipline].
# To execute it from default input values:
jax_discipline.execute()
jax_discipline.io.data["out"]

# %%
# To execute it from new input values:
jax_discipline.execute({"in": array([3.0])})
jax_discipline.io.data["out"]

# %%
# To compute its Jacobian:
jax_discipline.linearize({"in": array([3.0])})

# %%
# !!! note
#     This [JAXDiscipline][gemseo_jax.jax_discipline.JAXDiscipline]
#     is also compatible with JIT compilation.
