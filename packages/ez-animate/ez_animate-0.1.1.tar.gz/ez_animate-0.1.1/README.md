<!-- Badges -->
<p align="left">
  <a href="https://github.com/SantiagoEnriqueGA/ez-animate/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/SantiagoEnriqueGA/ez-animate.svg" alt="License">
  </a>
  <a href="https://github.com/SantiagoEnriqueGA/ez-animate/actions">
    <img src="https://github.com/SantiagoEnriqueGA/ez-animate/workflows/CI/badge.svg" alt="Build Status">
  </a>
  <a href="https://pypi.org/project/ez-animate/">
    <img src="https://img.shields.io/pypi/v/ez-animate.svg" alt="PyPI Version">
  <a href="https://pepy.tech/project/ez-animate">
    <img src="https://static.pepy.tech/badge/ez-animate" alt="Downloads">
  </a>
  </a>
  <a href="https://pypi.org/project/ez-animate/">
    <img src="https://img.shields.io/pypi/pyversions/ez-animate.svg" alt="Python Versions">
  </a>
  <a href="https://codecov.io/gh/SantiagoEnriqueGA/ez-animate">
    <img src="https://codecov.io/gh/SantiagoEnriqueGA/ez-animate/branch/master/graph/badge.svg" alt="Code Coverage">
  </a>
  <a href="https://github.com/charliermarsh/ruff">
    <img src="https://img.shields.io/badge/code%20style-ruff-brightgreen.svg" alt="Code style: ruff">
  </a>
  <a href="https://santiagoenriquega.github.io/ez-animate/">
    <img src="https://img.shields.io/website?down_color=red&down_message=offline&up_color=brightgreen&up_message=MkDocs&url=https%3A%2F%2Fsantiagoenriquega.github.io%2Fez-animate" alt="Site Status">
  </a>
</p>

# ez-animate

A high-level, declarative Python package for creating common Matplotlib animations with minimal boilerplate code.


## Project Goals

`ez-animate` aims to make it easy for data scientists, analysts, educators, and researchers to create standard Matplotlib animations quickly and with minimal code. It abstracts away the complexity of `FuncAnimation`, state management, and repetitive setup, letting you focus on your data and story.

### Why?
- **Complex Setup:** No need to write custom `init` and `update` functions.
- **State Management:** Simplifies handling data and artist states between frames.
- **Repetitive Code:** Reduces boilerplate for standard animations.

### Who is it for?
- **Primary:** Data scientists & analysts (exploratory analysis, presentations, notebooks).
- **Secondary:** Students, educators, and researchers (learning, teaching, publications).

## Features
- **Simple API:** Create animations with a few lines of code.
- **Tested & Linted:** High code quality with `pytest` and `ruff`.
- **Documentation:** See [documentation](https://santiagoenriquega.github.io/ez-animate/) for usage examples and API references.

## Installation

```bash
pip install ez-animate
```


## Quickstart

```python
from ez_animate import RegressionAnimation

# Create and run the animation
animator = RegressionAnimation(
    model=Lasso,    # Scikit-learn or sega_learn model class
    X=X,
    y=y,
    test_size=0.25,
    dynamic_parameter="alpha",
    static_parameters={"max_iter": 1, "fit_intercept": True},
    keep_previous=True,
    metric_fn=Metrics.mean_squared_error,
)

# Set up the plot
animator.setup_plot(
    title="Regression Animation",
    xlabel="Feature Coefficient",
    ylabel="Target Value",
)

# Create the animation
animator.animate(frames=np.arange(0.01, 1.0, 0.01))

# Show and save the animation
animator.show()
animator.save("regression_animation.gif")
```

## Full Documentation

See the [documentation site](https://santiagoenriquega.github.io/ez-animate/) for complete usage instructions, API references, and examples.
## Development/Contributing

See [DEVELOPMENT.md](DEVELOPMENT.md) for full development and contributing guidelines.


## Project Structure

```
ez-animate/
├─ .github/
│  ├─ ISSUE_TEMPLATE
│  └─ workflows
├─ examples/
│  ├─ plots
│  ├─ sega_learn
│  └─ sklearn
├─ src/
│  └─ ez_animate
└─ tests

```

## License

This project is licensed under the terms of the [MIT License](LICENSE).


## Acknowledgments

- Built with inspiration from the Matplotlib community.
- Thanks to all contributors!

## Example GIFs

### Stochastic Gradient Descent (SGD) Regression
Here's an example of a Stochastic Gradient Descent (SGD) regression animation created using `ez-animate`. This animation shows how the fit and the metrics evolve over time as the model learns from the data.
![SGD Regression Animation](https://raw.githubusercontent.com/SantiagoEnriqueGA/ez-animate/master/docs/plots/animator_sgd.gif)

### K-Means Clustering
Here's an example of a K-Means clustering animation created using `ez-animate`. This animation shows how the cluster centroids and the data points evolve over time as the algorithm iteratively refines the clusters.
![K-Means Clustering Animation](https://raw.githubusercontent.com/SantiagoEnriqueGA/ez-animate/master/docs/plots/animator_kmeans.gif)
