# PyMBO: Python Multi-objective Bayesian Optimization

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.2.2-green.svg)](https://github.com/jakub-jagielski/pymbo)

PyMBO is a comprehensive framework for multi-objective Bayesian optimization that combines advanced algorithms with intuitive visualization capabilities. The framework is designed for researchers and practitioners working with complex optimization problems involving multiple objectives and high-dimensional parameter spaces.

## Features

### Core Optimization
- **Multi-objective Bayesian optimization** using PyTorch and BoTorch backends
- **Hybrid sequential/parallel execution** with automatic mode detection
- **Multiple acquisition functions** including Expected Hypervolume Improvement (EHVI)
- **Support for mixed parameter types** (continuous, discrete, categorical)

### Screening and Analysis
- **SGLBO (Stochastic Gradient Line Bayesian Optimization)** for efficient parameter space exploration
- **Parameter importance analysis** with correlation matrices
- **Real-time visualization** of acquisition functions and optimization progress
- **Comprehensive benchmarking** tools for algorithm comparison

### Interface and Usability
- **Graphical user interface** with interactive controls
- **Programmatic API** for integration into existing workflows
- **Export capabilities** for results and visualizations
- **Extensive documentation** and examples

## Installation

### From PyPI (Recommended)
```bash
pip install pymbo
```

### From Source
```bash
git clone https://github.com/jakub-jagielski/pymbo.git
cd pymbo
pip install -r requirements.txt
```

## Quick Start

### Graphical Interface
Launch the application with:
```bash
python -m pymbo
```

### Programmatic Usage
```python
from pymbo import EnhancedMultiObjectiveOptimizer, SimpleController

# Define optimization problem
optimizer = EnhancedMultiObjectiveOptimizer(
    bounds=[(0, 10), (0, 10)],  # Parameter bounds
    objectives=['maximize']      # Optimization direction
)

# Initialize controller and run optimization
controller = SimpleController(optimizer)
results = controller.run_optimization()
```

### Parallel Optimization
```python
from pymbo.core.controller import SimpleController

controller = SimpleController()

# Benchmark multiple strategies
benchmark_results = controller.benchmark_optimization_strategies(
    strategies=['ehvi', 'ei', 'random'],
    n_suggestions=10,
    parallel=True
)

# What-if analysis
scenarios = [
    {'name': 'conservative', 'n_suggestions': 5},
    {'name': 'aggressive', 'n_suggestions': 15}
]
what_if_results = controller.run_what_if_analysis(
    scenarios=scenarios, 
    parallel=True
)
```

## SGLBO Screening Module

For complex parameter spaces, PyMBO includes a specialized screening module that provides efficient initial exploration:

```python
from pymbo.screening import ScreeningOptimizer

optimizer = ScreeningOptimizer(
    params_config=parameters_configuration,
    responses_config=responses_configuration
)

results = optimizer.run_screening()
```

The screening module provides:
- Parameter sensitivity analysis
- Response surface approximation  
- Design space reduction
- Seamless integration with main optimization

## Architecture

```
pymbo/
├── core/           # Optimization algorithms and controllers
│   ├── optimizer.py      # Core optimization implementation
│   ├── controller.py     # Optimization control and orchestration
│   └── orchestrator.py   # Parallel execution management
├── gui/            # Graphical user interface components
├── screening/      # SGLBO screening optimization
├── utils/          # Utilities for plotting and analysis
└── ...
```

The framework uses a modular design that separates:
- **Optimization algorithms** (core module)
- **User interfaces** (GUI and programmatic API)  
- **Analysis tools** (screening and utilities)
- **Visualization** (integrated plotting and export)

## Performance Characteristics

PyMBO's hybrid architecture provides:
- **Automatic parallelization** for embarrassingly parallel tasks
- **Sequential execution** for interactive optimization
- **Memory-efficient** handling of large parameter spaces
- **GPU acceleration** support where applicable

Typical performance improvements:
- 2-10x speedup for strategy benchmarking
- 3-8x faster data loading for large datasets
- Efficient memory usage for high-dimensional problems

## Documentation and Examples

The framework includes comprehensive documentation covering:
- Algorithm implementation details
- User interface guides
- API reference
- Performance benchmarks
- Integration examples

## Contributing

We welcome contributions from the research community. To contribute:

1. Fork the repository
2. Create a feature branch
3. Implement your changes with appropriate tests
4. Submit a pull request with a clear description

Please ensure that contributions maintain code quality and include appropriate documentation.

## Citation

If you use PyMBO in your research, please cite:

```bibtex
@software{jagielski2025pymbo,
  author = {Jakub Jagielski},
  title = {PyMBO: A Python library for multivariate Bayesian optimization and stochastic Bayesian screening},
  version = {3.2.2},
  year = {2025},
  url = {https://github.com/jakub-jagielski/pymbo}
}
```

## Development

PyMBO was developed with the assistance of [Anthropic's Claude Code](https://docs.anthropic.com/en/docs/claude-code), an AI-powered development tool that enhanced the implementation of optimization algorithms, GUI components, and documentation.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions, bug reports, or feature requests, please use the [GitHub Issues](https://github.com/jakub-jagielski/pymbo/issues) system.