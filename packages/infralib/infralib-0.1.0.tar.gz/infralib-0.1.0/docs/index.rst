InfraLib: Infrastructure Management for RL and Optimization
===========================================================

**InfraLib** is a comprehensive Python library for modeling, simulating, and analyzing large-scale infrastructure management problems. It provides a realistic and granular representation of infrastructure systems by integrating hierarchical models that capture intricate relationships between components and facilities.

Introduction
------------

Infrastructure systems are the backbone of modern society, encompassing transportation networks, utility systems, and public facilities. Managing these systems efficiently is crucial for economic stability, environmental sustainability, and public safety. InfraLib addresses the complex challenges of infrastructure management by providing:

- **Stochastic deterioration modeling** with partial observability
- **Gymnasium-compatible RL environments** for algorithm development
- **Scalable simulation** supporting millions of components
- **Rich visualization and analysis tools**
- **Flexible model architecture** with dependency injection
- **Web-based human interface** for expert data collection

Quick Links
-----------

- **Website**: https://infralib.github.io/
- **Source Code**: https://github.com/pthangeda/InfraLib
- **PyPI Package**: https://pypi.org/project/infralib/
- **Documentation**: https://infralib.readthedocs.io/

Installation
------------

Install InfraLib using pip:

.. code-block:: bash

   pip install infralib

Or install from source:

.. code-block:: bash

   git clone https://github.com/pthangeda/InfraLib.git
   cd InfraLib
   pip install -e .

Requirements:

- Python 3.12+
- NumPy >= 1.25.2
- SciPy >= 1.10.0
- Gymnasium >= 1.0.0
- Stable-Baselines3 >= 2.0.0
- Additional dependencies listed in ``pyproject.toml``

Quick Start
-----------

Here's a simple example to get you started with InfraLib:

.. code-block:: python

   from infralib.models.dynamics import WeibullDynamics
   from infralib.models.cost import SimpleCost
   from infralib.models.budget import FixedBudget
   from infralib.simulator import Simulator
   import numpy as np

   # Setup models
   dynamics = WeibullDynamics(n_states=10)
   cost = SimpleCost()
   budget = FixedBudget(initial_budget=10000)

   # Create and run simulator
   sim = Simulator(dynamics, cost, budget)
   sim.reset(n_components=5)
   actions = np.array([0, 1, 2, 0, 1])  # do_nothing, inspect, repair, do_nothing, inspect
   states, info = sim.step(actions)

   print(f"Total cost: {info['total_cost']:.2f}")
   print(f"Failures: {info['failures']}")

For RL training:

.. code-block:: python

   from infralib.envs.simple import SimpleInfraEnv
   import stable_baselines3 as sb3

   # Create environment
   env = SimpleInfraEnv(n_components=5, max_budget=10000)

   # Train RL agent
   model = sb3.PPO('MlpPolicy', env, verbose=1)
   model.learn(total_timesteps=100000)

   # Evaluate policy
   obs, info = env.reset()
   for _ in range(100):
       action, _states = model.predict(obs)
       obs, reward, done, truncated, info = env.step(action)
       if done or truncated:
           obs, info = env.reset()

Key Features
------------

Stochastic Deterioration Modeling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

InfraLib models infrastructure component deterioration using:

- **Weibull dynamics**: Realistic deterioration patterns based on empirical data
- **Markov dynamics**: Simplified models for rapid prototyping
- **Custom dynamics**: Extensible framework for domain-specific models

Partial Observability
^^^^^^^^^^^^^^^^^^^^^

Real-world infrastructure management involves:

- **Noisy inspections**: Component states are not directly observable
- **Inspection costs**: Gathering information requires resources
- **Belief state management**: Agents must reason under uncertainty

Gymnasium Compatibility
^^^^^^^^^^^^^^^^^^^^^^^

InfraLib provides RL environments that are:

- **Fully compatible** with Stable-Baselines3 and other RL libraries
- **Configurable observation spaces**: Full, partial, or custom observations
- **Flexible reward functions**: Customize objectives for your use case
- **Vectorized environments**: Train multiple agents in parallel

Scalability
^^^^^^^^^^^

InfraLib is designed for real-world scale:

- **Millions of components**: Efficient vectorized operations with Numba
- **Long time horizons**: Simulate years of infrastructure evolution
- **Batch policy evaluation**: Compare multiple strategies efficiently

Support and Community
---------------------

**Contact**: Pranay Thangeda or Melkior Ornik

**Email**: We welcome questions, bug reports, and feature requests. Please contact Pranay Thangeda (pranayt2@illinois.edu) or Melkior Ornik (melkior.ornik@illinois.edu) directly for support and collaboration opportunities.

**Feature Requests**: We are actively seeking collaborations and are willing to implement features that help researchers and practitioners use InfraLib for their specific use cases. Please reach out with your requirements and we'll work with you to extend the library's capabilities.

**Contributing**: We welcome contributions from the community. Please see our GitHub repository for contribution guidelines.

**Issues**: Report bugs and request features on our GitHub issues page: https://github.com/pthangeda/InfraLib/issues

License
-------

InfraLib is released under the **MIT License**:

.. code-block:: text

   MIT License

   Copyright (c) 2025 InfraLib Team

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.

API Reference
-------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/modules
   api/models
   api/envs
   api/simulator
   api/visualize

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
