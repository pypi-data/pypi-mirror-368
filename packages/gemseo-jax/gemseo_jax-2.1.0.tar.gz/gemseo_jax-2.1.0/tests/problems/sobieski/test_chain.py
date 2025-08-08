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
"""Tests for JAXSobieskiChain."""

from __future__ import annotations

from gemseo.core.chains.chain import MDOChain
from gemseo.problems.mdo.sobieski.core.problem import SobieskiProblem
from gemseo.problems.mdo.sobieski.disciplines import SobieskiAerodynamics
from gemseo.problems.mdo.sobieski.disciplines import SobieskiMission
from gemseo.problems.mdo.sobieski.disciplines import SobieskiPropulsion
from gemseo.problems.mdo.sobieski.disciplines import SobieskiStructure
from numpy import atleast_1d
from numpy.testing import assert_allclose

from gemseo_jax.problems.sobieski.chain import JAXSobieskiChain


def test_execute():
    """Check the execution of JAXSobieskiChain."""
    jax_chain = JAXSobieskiChain()
    input_data = SobieskiProblem().get_default_inputs(jax_chain.input_grammar.names)
    mdo_chain = MDOChain([
        SobieskiAerodynamics(),
        SobieskiStructure(),
        SobieskiPropulsion(),
        SobieskiMission(),
    ])
    expected_output_data = mdo_chain.execute(input_data)
    output_data = {k: atleast_1d(v) for k, v in jax_chain.execute(input_data).items()}
    for name in output_data:
        assert_allclose(output_data[name], expected_output_data[name])


def test_jacobian():
    """Check the Jacobian."""
    jax_chain = JAXSobieskiChain()
    jax_chain.check_jacobian(threshold=1e-4)
