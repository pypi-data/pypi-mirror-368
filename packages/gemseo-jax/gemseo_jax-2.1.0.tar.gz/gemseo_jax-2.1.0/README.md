<!--
 Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com

 This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
 International License. To view a copy of this license, visit
 http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
 Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->

# gemseo-jax

[![PyPI - License](https://img.shields.io/pypi/l/gemseo-jax)](https://www.gnu.org/licenses/lgpl-3.0.en.html)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gemseo-jax)](https://pypi.org/project/gemseo-jax/)
[![PyPI](https://img.shields.io/pypi/v/gemseo-jax)](https://pypi.org/project/gemseo-jax/)
[![Codecov branch](https://img.shields.io/codecov/c/gitlab/gemseo:dev/gemseo-jax/develop)](https://app.codecov.io/gl/gemseo:dev/gemseo-jax)

## Overview

GEMSEO plugin for JAX (jit compilation, autodiff, XLA).

The power of [JAX](https://jax.readthedocs.io) (a Python library for high-performance array computing) to accelerate MDO.

JAX is heavily used for large-scale machine learning research, but many of its benefits can also be used to leverage
scientific computing as a whole. In the context of Multidisciplinary Optimization (MDO), we use JAX to avoid manual
implementation of derivatives of objective functions and constraints wrt optimization variables, which allows for using
gradient-based optimizers without an extra implementation cost.


## Installation

Install the latest version with `pip install gemseo-jax`.

See [pip](https://pip.pypa.io/en/stable/getting-started/) for more information.

## Bugs and questions

Please use the [gitlab issue tracker](https://gitlab.com/gemseo/dev/gemseo-jax/-/issues)
to submit bugs or questions.

## Contributing

See the [contributing section of GEMSEO](https://gemseo.readthedocs.io/en/stable/software/developing.html#dev).

## Contributors

- Ian Costa-Alves
- François Gallard
- Matthias De Lozzo
- Antoine DECHAUME
