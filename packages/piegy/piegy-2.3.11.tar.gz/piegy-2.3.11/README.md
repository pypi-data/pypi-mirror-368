# piegy

The package full name is: Payoff-Driven Stochastic Spatial Model for Evolutionary Game Theory. "pi" refers to "payoff, and "egy" is taken from "Evolutionary Game Theory".

Provides a stochastic spatial model for simulating the interaction and evolution of two species in either 1D or 2D space, as well as analytic tools.

## Installation

To install *piegy*, run the following in terminal:

```bash
pip install piegy
```

## Documentation and Source

See source code at: [piegy GitHub Repo](https://github.com/Chenning04/piegy.git). 
The *piegy* documentation at: [piegy Documentation](https://piegy.readthedocs.io/en/). 

## How the Model Works

Our model can be summarized as "classical evolutionary game theory endowed with spatial structure and payoff-driven migration rules". Consider two species, predators and preys (denoted by *U* and *V*), in a rectangular region. We divide the region into N by M patches and simulate their interaction within a patch by classical game theory (i.e., payoff matrices and carrying capacity). Interactions across patches are simulated by payoff-driven migration rules. An individual migrates to a neighboring patch with probability weighted by payoff in the neighbors.

We use the Gillepie algorithm as the fundamental event-selection algorithm. At each time step, one event is selected and let happen; and the step size is continuous, dependent on the current state in the space. Data are recorded every some specified time interval.

## Analytic Tools

The *piegy* package also provides a wide range of analytic and supportive tools alongside the main model, such as plotting, numerical tools, data saving & reading, etc. We also provide the *piegy.videos* module for more direct visualizations such as how population distribution change over time.

## C Core

From version 2 on, the *piegy* simulations are now equipped with a C core, which makes it significantly faster than previous versions.

## Examples

To get started, simply get our demo model and run simulation:

```python
from piegy import simulation, figures
import matplotlib.pyplot as plt

mod = simulation.demo_model()
simulation.run(mod)

fig1, ax1 = plt.subplots()
figures.UV_dyna(mod, ax1)
fig2, ax2 = plt.subplots(1, 2, figsize = (12.8, 4.8))
figures.UV_hmap(mod, ax2[0], ax2[1])
```

The figures reveal population dynamics and steady state population distribution.


## Acknowledgments

- Thanks Professor Daniel Cooney at University of Illinois Urbana-Champaign. This package is developed alongside a project with Prof. Cooney and received enormous help from him.
- Special thanks to the open-source community for making this package possible.

