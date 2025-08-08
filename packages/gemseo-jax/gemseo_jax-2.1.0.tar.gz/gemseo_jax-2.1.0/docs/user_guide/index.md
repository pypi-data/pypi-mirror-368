<!--
 Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com

 This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
 International License. To view a copy of this license, visit
 http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
 Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->
# User guide

## JAX

JAX is a library for array-oriented numerical computation (similar to [NumPy](https://numpy.org/)), with automatic
differentiation (AD) and just-in-time (JIT) compilation to enable hardware accelerated numerical computing.

JAX is heavily used for large-scale machine learning research, but many of its benefits can also be used to leverage
scientific computing as a whole. In the context of Multidisciplinary Optimization (MDO), we use JAX to avoid manual
implementation of derivatives of objective functions and constraints wrt optimization variables, which allows for using
gradient-based optimizers without an extra implementation cost.

There are other libraries that allows for AD in python ([Autograd](https://github.com/HIPS/autograd),
[TensorFlow](https://www.tensorflow.org/), [PyTorch](https://pytorch.org/)), but JAX was chosen due to its:

- Wide community and ecosystem of
[libraries, projects and other associated resources](https://github.com/n2cholas/awesome-jax);
- Hardware-aware configuration optimizations on CPU, GPU and TPU;
- Focus on general scientific computing rather than machine-learning problems.

In our experience, writing MDO problems with GEMSEO-JAX means less code and usually faster programs than their NumPy
implementations ([Is JAX faster than NumPy?](https://jax.readthedocs.io/en/latest/faq.html#is-jax-faster-than-numpy)).

For an initial introduction to JAX, we recommend reading the
[Quickstart](https://jax.readthedocs.io/en/latest/quickstart.html),
[Key Concepts](https://jax.readthedocs.io/en/latest/key-concepts.html) and
[How to Think in JAX](https://jax.readthedocs.io/en/latest/notebooks/thinking_in_jax.html) notebooks.
For a better grasp of JAX functionalities and how to efficiently use it, we recommed
[Just-in-time Compilation](https://jax.readthedocs.io/en/latest/jit-compilation.html) and
[The Autodiff Cookbook](https://jax.readthedocs.io/en/latest/notebooks/autodiff_cookbook.html).

## GEMSEO-JAX overview

The plugin is centered around [JAXDiscipline][gemseo_jax.jax_discipline.JAXDiscipline], which wraps a JAX function,
with built-in automatic differentiation.
This class provides useful functionalities:

- filtering of the Jacobian computation graph for specific inputs/outputs,
- jit compiling function and jacobian call for lowering cost of re-evaluation,
- performing pre-run's to trigger and log compilation times.


[AutoJAXDiscipline][gemseo_jax.auto_jax_discipline.AutoJAXDiscipline] is a special
[JAXDiscipline][gemseo_jax.jax_discipline.JAXDiscipline]
inferring the input names, output names and default input values
from the signature of the JAX function,
in the manner of [AutoPyDiscipline][gemseo.disciplines.auto_py.AutoPyDiscipline].


[JAXChain][gemseo_jax.jax_chain.JAXChain] is a [JAXDiscipline][gemseo_jax.jax_discipline.JAXDiscipline]
allowing to assemble a series of [JAXDiscipline][gemseo_jax.jax_discipline.JAXDiscipline]s
and execute them all in JAX.
This is useful to avoid meaningless JAX-to/from-NumPy conversions.

!!! info
    The [JAXDiscipline][gemseo_jax.jax_discipline.JAXDiscipline],
    the [AutoJAXDiscipline][gemseo_jax.auto_jax_discipline.AutoJAXDiscipline]
    and the [JAXChain][gemseo_jax.jax_chain.JAXChain] do not support the use of namespaces. This is because the
    functions that they wrap are compiled with the original naming, and adding a layer on top would break the naming
    convention and make it difficult to use the automatic Jacobians as computed by `JAX`.
    Consider using the [RemappingDiscipline][gemseo.disciplines.remapping.RemappingDiscipline] to rename inputs and
    outputs instead.

## Quick guide

```python
from jax.numpy import exp, sqrt
from gemseo_jax.auto_jax_discipline import AutoJAXDiscipline


def compute_y_1(y_2=1.0, x_local=1.0, x_shared_1=1.0, x_shared_2=3.0):
    y_1 = x_shared_1**2 + x_shared_2 + x_local - 0.2 * y_2
    return y_1


def compute_y_2(y_1=1.0, x_shared_1=1.0, x_shared_2=3.0):
    y_2 = sqrt(abs(y_1)) + x_shared_1 + x_shared_2
    return y_2


def compute_obj_c_1_c_2(y_1=1.0, y_2=1.0, x_shared_2=3.0, x_local=1.0):
    obj = x_local**2 + x_shared_2 + y_1**2 + exp(-y_2)
    c_1 = 3.16 - y_1**2
    c_2 = y_2 - 24.0
    return obj, c_1, c_2


sellar_1 = AutoJAXDiscipline(compute_y_1, name="Sellar1")
sellar_2 = AutoJAXDiscipline(compute_y_2, name="Sellar2")
sellar_system = AutoJAXDiscipline(compute_obj_c_1_c_2, name="SellarSystem")
```
Here, the JAX functions are defined and automatically wrapped into GEMSEO disciplines with
[AutoJAXDiscipline][gemseo_jax.auto_jax_discipline.AutoJAXDiscipline].
The Jacobians are automatically calculated using Automatic Differentiation (AD).
By default we "agressively" promote double precision in all [JAXDiscipline][gemseo_jax.jax_discipline.JAXDiscipline],
which differs from [JAX's default single-precision](https://jax.readthedocs.io/en/latest/notebooks/Common_Gotchas_in_JAX.html#double-64bit-precision).

These disciplines can already be used in a GEMSEO process, but may lead to sub-optimal
performance due to excessive number of conversions from NumPy(GEMSEO) to JAX arrays.
To avoid this, a [JAXChain][gemseo_jax.jax_chain.JAXChain] can be used to keep the communication between disciplines
all inside JAX, here GEMSEO is only used to generate the sequence of discipline execution.

```python
from gemseo_jax.jax_chain import JAXChain


disciplines = [sellar_1, sellar_2, sellar_system]
jax_chain = JAXChain(disciplines, name="SellarChain")
```
We can also filter the Jacobian function to ensure AD is only made for some outputs of interest.
In practice, this means JAX views fewer operations to trace and apply AD over.

```python
jax_chain.add_differentiated_outputs(["obj", "c_1", "c_2"])
```

Finally, we may jit-compile the output and Jacobian functions that will be used.
This takes an extra compilation time, but lowers significantly the cost of function calls.

As compilation is just-in-time, by default we make a pre-run of the jitted functions and log
compilation times. This ensures compilation is not added to execution timing, but some comprehensive benchmarks
may turn this off.

```python
jax_chain.compile_jit(pre_run=True)
```
