# hybraut-executor-watchdog

[![PyPI - Version](https://img.shields.io/pypi/v/hybraut-executor-watchdog.svg)](https://pypi.org/project/hybraut-executor-watchdog)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hybraut-executor-watchdog.svg)](https://pypi.org/project/hybraut-executor-watchdog)

-----

The `hybraut-ros2` runtime system is monitored and managed by the `*hybraut-executor-watchdog* (FSM)` implemented in this `pkg`. This FSM listens to runtime events and responds accordingly to maintain mission continuity, recover from failures, and safely shut down in critical conditions. It helps enforce lifecycle safety and determinism across automaton operations.

When specific events are published (e.g., mode transitions, errors, mission completion), the FSM interprets these and updates the automaton's state. Each FSM state is also associated with a corresponding **status message**, which is published to inform external systems about the automaton's condition.

**NOTE:** **within the `./notebooks/demos` is a ipynb file containing examples of how the `fsm` is used.**

## Table of Contents
- [FSM Floatwart](#fsm-flowchart)
- [Installation](#installation)
- [License](#license)


## FSM Flowchart

The `hybraut-exeuctor-watchdog` has the following structure: 

![hybraut-executor-watchdog_diagram](.github/diagrams/hybraut_watchdog_fsm_flowchart.png)


## Installation

```console
pip install hybraut-executor-watchdog
```


## License

`hybraut-executor-watchdog` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
