<!--
 Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com

 This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
 International License. To view a copy of this license, visit
 http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
 Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->

<!--
Changelog titles are:
- Added: for new features.
- Changed: for changes in existing functionality.
- Deprecated: for soon-to-be removed features.
- Removed: for now removed features.
- Fixed: for any bug fixes.
- Security: in case of vulnerabilities.
-->

# Changelog

All notable changes of this project will be documented here.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0)
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Version 2.1.0 (August 2025)

### Added

- [create_jax_discipline_from_discipline][gemseo_jax.utils.create_jax_discipline_from_discipline]
  can create a [JAXDiscipline][gemseo_jax.jax_discipline.JAXDiscipline]
  from a discipline using JAX instead of NumPy and SciPy.

## Version 2.0.2 (February 2025)

### Changed

- Upgrade jax version to 0.4.38.

## Version 2.0.1 (November 2024)

### Fixed

- The [JAXDiscipline][gemseo_jax.jax_discipline.JAXDiscipline] now supports using namespaces.

## Version 2.0.0 (November 2024)

### Added

- Support GEMSEO v6.
- Support for Python 3.12.
- The Sellar problem in [gemseo_jax.problems.sellar][gemseo_jax.problems.sellar].
- The Sobieski's SSBJ problem in [gemseo_jax.problems.sobieski][gemseo_jax.problems.sobieski].

### Fixed

`JAXDiscipline.compute_jacobian` correctly handles multidimensional input and output variables.

## Version 1.0.0 (March 2024)

Initial version.
