[![DOI](https://zenodo.org/badge/500850617.svg)](https://zenodo.org/badge/latestdoi/500850617)

# Inflation
Inflation is a package, written in Python, that implements inflation algorithms for causal inference. In causal inference, the main task is to determine which causal relationships can exist between different observed random variables. Inflation algorithms are a class of techniques designed to solve the causal compatibility problem, that is, test compatibility between some observed data and a given causal relationship.

This package implements the inflation technique for classical, quantum, and post-quantum causal compatibility. By relaxing independence constraints to symmetries on larger graphs, it develops hierarchies of relaxations of the causal compatibility problem that can be solved using linear and semidefinite programming. For details, see [Wolfe et al. “The inflation technique for causal inference with latent variables.” Journal of Causal Inference 7 (2), 2017-0020 (2019)](https://www.degruyter.com/document/doi/10.1515/jci-2017-0020/html), [Wolfe et al. “Quantum inflation: A general approach to quantum causal compatibility.” Physical Review X 11 (2), 021043 (2021)](https://journals.aps.org/prx/abstract/10.1103/PhysRevX.11.021043), and references therein.

Examples of use of this package include:

- Causal compatibility with classical, quantum, non-signaling, and hybrid models.
- Feasibility problems and extraction of certificates.
- Optimization of Bell operators.
- Optimization over classical distributions.
- Handling of bilayer (i.e., networks) and multilayer causal structures.
- Standard [Navascués-Pironio-Acín hierarchy](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.98.010401).
- Scenarios with partial information.
- Possibilistic compatibility with a causal network.
- Estimation of do-conditionals and causal strengths.

See the documentation for more details.

## Documentation

* [Latest version](https://ecboghiu.github.io/inflation/).

## Installation

To install the package, run the following command:

```
pip install inflation
```

You can also install directly from GitHub with:

```
pip install git+https://github.com/ecboghiu/inflation.git@main
```

or download the repository on your computer and run `pip install .` in the repository folder. Install the `devel` branch for the latest features and bugfixes.

Tests are written outside the Python module, therefore they are not installed together with the package. To test the installation, clone the repository and run, in a Unix terminal,
```python -m unittest -v```
inside the repository folder.

## Example

The following example shows that the W distribution is incompatible with the triangle scenario with quantum sources by showing that a specific semidefinite programming relaxation is infeasible:

```python
from inflation import InflationProblem, InflationSDP
import numpy as np

P_W = np.zeros((2, 2, 2, 1, 1, 1))
for a, b, c, x, y, z in np.ndindex(*P_W.shape):
    if a + b + c == 1:
        P_W[a, b, c, x, y, z] = 1 / 3

triangle = InflationProblem(dag={"rho_AB": ["A", "B"],
                                 "rho_BC": ["B", "C"],
                                 "rho_AC": ["A", "C"]},
                             outcomes_per_party=(2, 2, 2),
                             settings_per_party=(1, 1, 1),
                             inflation_level_per_source=(2, 2, 2))

sdp = InflationSDP(triangle, verbose=1)
sdp.generate_relaxation('npa2')
sdp.set_distribution(P_W)
sdp.solve()

print("Problem status:", sdp.status)
print("Infeasibility certificate:", sdp.certificate_as_probs())
```

For more information about the theory and other features, please visit the [documentation](https://ecboghiu.github.io/inflation/), and more specifically the [Tutorial](https://ecboghiu.github.io/inflation/_build/html/tutorial.html) and [Examples](https://ecboghiu.github.io/inflation/_build/html/examples.html) pages.

## How to contribute

Contributions are welcome and appreciated. If you want to contribute, you can read the [contribution guidelines](https://github.com/ecboghiu/inflation/blob/main/CONTRIBUTE.md). You can also read the [documentation](https://ecboghiu.github.io/inflation/) to learn more about how the package works.

## License

Inflation is free open-source software released under [GNU GPL v. 3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).

## Citing Inflation

If you use Inflation in your work, please cite [Inflation's paper](https://www.arxiv.org/abs/2211.04483):

- Emanuel-Cristian Boghiu, Elie Wolfe and Alejandro Pozas-Kerstjens, "Inflation: a Python package for classical and quantum causal compatibility", Quantum **7**, 996 (2023), arXiv:2211.04483

```
@article{pythoninflation,
  doi = {10.22331/q-2023-05-04-996},
  url = {https://doi.org/10.22331/q-2023-05-04-996},
  title = {Inflation: a {P}ython library for classical and quantum causal compatibility},
  author = {Boghiu, Emanuel-Cristian and Wolfe, Elie and Pozas-Kerstjens, Alejandro},
  journal = {{Quantum}},
  issn = {2521-327X},
  publisher = {{Verein zur F{\"{o}}rderung des Open Access Publizierens in den Quantenwissenschaften}},
  volume = {7},
  pages = {996},
  month = may,
  year = {2023},
  archivePrefix = {arXiv},
  eprint = {2211.04483}
}
```
