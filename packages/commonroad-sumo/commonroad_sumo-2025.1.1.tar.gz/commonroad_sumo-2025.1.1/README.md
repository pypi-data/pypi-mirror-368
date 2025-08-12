# CommonRoad - SUMO Interface

[![PyPI pyversions](https://img.shields.io/pypi/pyversions/commonroad-sumo.svg)](https://pypi.python.org/pypi/commonroad-sumo/)
[![PyPI version fury.io](https://badge.fury.io/py/commonroad-sumo.svg)](https://pypi.python.org/pypi/commonroad-sumo/)
[![PyPI download week](https://img.shields.io/pypi/dw/commonroad-sumo.svg?label=PyPI%20downloads)](https://pypi.python.org/pypi/commonroad-sumo/)
[![PyPI download month](https://img.shields.io/pypi/dm/commonroad-sumo.svg?label=PyPI%20downloads)](https://pypi.python.org/pypi/commonroad-sumo/)
[![PyPI license](https://img.shields.io/pypi/l/commonroad-sumo.svg)](https://pypi.python.org/pypi/commonroad-sumo/)


Interface between [CommonRoad](https://commonroad.in.tum.de) and the traffic simulator [SUMO](https://sumo.dlr.de).

It allows you to run non-interactive simulations to generate traffic on lanelet networks to create new CommonRoad scenarios. Additionally, you can run interactive simulations where a motion planner is executed in tandem with SUMO. The ego vehicle is controlled by the motion planner, while the behavior of the other vehicles is simulated by SUMO.

More about the interface can be found in the [original paper](http://mediatum.ub.tum.de/doc/1486856/344641.pdf):

Moritz Klischat, Octav Dragoi, Mostafa Eissa, and Matthias Althoff, *Coupling SUMO with a Motion Planning Framework for Automated Vehicles*, SUMO 2019: Simulating Connected Urban Mobility

## Quick Start

### Installation

The interface is available on PyPI and can be easily installed:

```bash
$ pip install commonroad-sumo
```

SUMO itself is already included as a dependency, therefore no further steps are required to use the interface.

### Example Usage

The following snippet will simulate random traffic on the lanelet network of a given CommonRoad scenario for `100` time steps and write the resulting CommonRoad scenario to `/tmp/simulated_scenario.xml`:

```python
from commonroad.common.file_reader import CommonRoadFileReader

from commonroad_sumo import NonInteractiveSumoSimulation

scenario, _ = CommonRoadFileReader("<path to CommonRoad scenario>").open()

simulation_result = NonInteractiveSumoSimulation.from_scenario(scenario).run(simulation_steps=100)
simulation_result.write_to_file("/tmp/simulated_scenario.xml")
```

## Documentation

The full documentation can be found at [cps.pages.gitlab.lrz.de/commonroad/sumo-interface](https://cps.pages.gitlab.lrz.de/commonroad/sumo-interface/).
