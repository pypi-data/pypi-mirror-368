import sys
from abc import ABC, abstractmethod

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

# Animation Class
# The goal is to create a reusable and modular animation class that can handle animations for any model and dataset.

# Requirements
#   Modularity:          The class should be reusable for different models and datasets.
#                        Should have base class and subclasses for specific models types (regression, classification, forecasting).
#   Customizability:     Allow users to customize plot elements (e.g., colors, labels, titles).
#   Ease of Use:         Provide a simple interface for creating animations.
#   Support for Metrics: Include functionality to calculate and display metrics like MSE.
#   Saving Options:      Allow saving animations in different formats (e.g., GIF, MP4).
#   Dynamic Updates:     Support dynamic updates of model parameters (e.g., window size).
#   Plot Styling:        Provide options for grid, legends, axis limits, etc.


# High-level Design
#   Base Class:         AnimationBase
#     - Common attributes and methods for all animations.
#     - Methods for setting up the plot, updating the plot, and saving the animation.
#     - Abstract methods for model-specific updates (e.g., update_model, update_plot).
#   Subclasses:         RegressionAnimation, ClassificationAnimation, ForecastingAnimation
#     - Inherit from AnimationBase and implement model-specific updates.
#     - Each subclass can have its own attributes and methods specific to the model type.


class AnimationBase(ABC):
    """Base class for creating animations of machine learning models."""

    def __init__(
        self,
        model,
        train_series,
        test_series,
        dynamic_parameter=None,
        static_parameters=None,
        keep_previous=None,
        metric_fn=None,
        plot_metric_progression=None,
        max_metric_subplots=1,
        **kwargs,
    ):
        """Initialize the animation base class.

        Args:
            model: The forecasting model or any machine learning model.
            train_series: Training time series data.
            test_series: Testing time series data.
            dynamic_parameter: The parameter to update dynamically (e.g., 'window', 'alpha', 'beta').
            static_parameters: Static parameters for the model.
                Should be a dictionary with parameter names as keys and their values.
            keep_previous: Whether to keep all previous lines with reduced opacity.
            metric_fn: Optional metric function or list of functions (e.g., MSE) to calculate and display during animation.
            plot_metric_progression: Whether to plot the progression of the metric over time.
            max_metric_subplots: Maximum number of metric subplots to display.
            **kwargs: Additional customization options (e.g., colors, line styles).
        """
        # Input validation
        if train_series is None or test_series is None:
            raise ValueError("train_series and test_series must be provided.")
        if dynamic_parameter is None:
            raise ValueError("dynamic_parameter must be provided.")
        if not isinstance(static_parameters, (dict, type(None))):
            raise ValueError("static_parameters must be a dictionary or None.")
        if not isinstance(keep_previous, bool):
            raise ValueError("keep_previous must be a boolean.")

        self.model = model
        self.train_data = train_series
        self.test_data = test_series
        self.dynamic_parameter = dynamic_parameter  # Parameter to update dynamically
        self.static_parameters = (
            static_parameters if static_parameters is not None else {}
        )
        self.keep_previous = keep_previous

        # Store additional keyword arguments
        self.kwargs = kwargs

        # Optional metric function (e.g., MSE)
        self.metric_fn = metric_fn
        self.plot_metric_progression = plot_metric_progression
        self.max_metric_subplots = max_metric_subplots if max_metric_subplots else 1
        # If self.metric_fn is not a list, convert it to a list
        if self.metric_fn and not isinstance(self.metric_fn, list):
            self.metric_fn = [self.metric_fn]

        # For each metric, keep a progression list (up to max_metric_subplots)
        if self.metric_fn and self.plot_metric_progression:
            self.metric_progression = [
                [] for _ in range(min(len(self.metric_fn), self.max_metric_subplots))
            ]
        else:
            self.metric_progression = None

        # Plot elements
        self.fig, self.ax = None, None
        self.lines = {}
        self.title = None
        self.metric_axes = None  # List of axes for metrics
        self.metric_lines = None  # List of lines for metrics

    def _set_kwargs(self, subclass=None, **kwargs):
        """Set the keyword arguments for plot customization, with defaults for all animation types."""
        # General defaults
        self.ax_kwargs = kwargs.get("ax_kwargs", {"fontsize": 10})
        self.legend_kwargs = kwargs.get("legend_kwargs", {})
        self.title_kwargs = kwargs.get("title_kwargs", {})
        self.suptitle_kwargs = kwargs.get("suptitle_kwargs", {})
        self.xlabel_kwargs = kwargs.get("xlabel_kwargs", {})
        self.ylabel_kwargs = kwargs.get("ylabel_kwargs", {})
        self.grid_kwargs = kwargs.get("grid_kwargs", {})

        # Set default values for scatter plot customization based on subclass
        if subclass == "RegressionAnimation":
            self.scatter_kwargs = kwargs.get(
                "scatter_kwargs", {"color": "blue", "zorder": 3}
            )
            self.scatter_kwargs_test = kwargs.get(
                "scatter_kwargs_test",
                {"color": "lightcoral", "marker": "x", "zorder": 2},
            )
        elif subclass == "ClassificationAnimation":
            self.scatter_kwargs = kwargs.get(
                "scatter_kwargs", {"edgecolors": "k", "alpha": 0.7, "zorder": 2}
            )
            self.scatter_kwargs_test = kwargs.get(
                "scatter_kwargs_test", {"marker": "x", "alpha": 0.7, "zorder": 2}
            )
        elif subclass == "ForecastingAnimation":
            pass
        elif subclass == "ClusteringAnimation":
            self.scatter_kwargs = kwargs.get(
                "scatter_kwargs", {"alpha": 0.7, "edgecolors": "k", "zorder": 2}
            )
            self.scatter_kwargs_test = kwargs.get(
                "scatter_kwargs_test", {"alpha": 0.3, "marker": "x", "zorder": 2}
            )
        elif subclass == "TransformationAnimation":
            # Defaults for transformation visualizations
            self.scatter_kwargs = kwargs.get(
                "scatter_kwargs", {"color": "blue", "alpha": 0.6, "zorder": 2}
            )
            self.scatter_kwargs_test = kwargs.get(
                "scatter_kwargs_test",
                {"color": "orange", "alpha": 0.7, "marker": "x", "zorder": 2},
            )

        # Regression-specific defaults
        self.line_kwargs = kwargs.get("line_kwargs", {"color": "red", "zorder": 3})

        # Classification-specific defaults
        self.decision_boundary_kwargs = kwargs.get(
            "decision_boundary_kwargs", {"alpha": 0.25, "cmap": "coolwarm", "zorder": 1}
        )
        self.decision_boundary_line_kwargs = kwargs.get(
            "decision_boundary_line_kwargs", {"linewidths": 1, "colors": "black"}
        )

        # Forecasting-specific defaults
        self.train_line_kwargs = kwargs.get(
            "train_line_kwargs", {"color": "blue", "label": "Training Data"}
        )
        self.vline_kwargs = kwargs.get(
            "vline_kwargs",
            {"color": "black", "linestyle": "--", "label": "Forecast Start"},
        )
        self.fitted_line_kwargs = kwargs.get(
            "fitted_line_kwargs",
            {"color": "green", "zorder": 3, "label": "Fitted Line"},
        )
        self.forecast_line_kwargs = kwargs.get(
            "forecast_line_kwargs",
            {"color": "red", "linestyle": "--", "zorder": 3, "label": "Forecast"},
        )

        # Clustering-specific defaults
        self.cluster_gray_train_kwargs = kwargs.get(
            "cluster_gray_train_kwargs",
            {"c": "gray", "alpha": 0.5, "edgecolors": "w", "s": 50},
        )
        self.cluster_gray_test_kwargs = kwargs.get(
            "cluster_gray_test_kwargs",
            {"c": "lightgray", "alpha": 0.5, "s": 50, "marker": "x"},
        )
        self.cluster_center_kwargs = kwargs.get(
            "cluster_center_kwargs",
            {
                "marker": "*",
                "s": 300,
                "edgecolors": "black",
                "label": "Centers",
                "zorder": 3,
            },
        )
        self.prev_center_kwargs = kwargs.get(
            "prev_center_kwargs",
            {"marker": "*", "c": "yellow", "edgecolors": "gray", "s": 100, "zorder": 1},
        )
        self.trace_line_kwargs = kwargs.get(
            "trace_line_kwargs",
            {"linestyle": "--", "linewidth": 2.5, "alpha": 1, "zorder": 2},
        )

        # Metric plot customization options
        self.metric_title_kwargs = kwargs.get("metric_title_kwargs", {})
        self.metric_line_kwargs = kwargs.get("metric_line_kwargs", {})
        self.metric_ax_kwargs = kwargs.get("metric_ax_kwargs", {})
        self.metric_xlabel_kwargs = kwargs.get("metric_xlabel_kwargs", {})
        self.metric_ylabel_kwargs = kwargs.get("metric_ylabel_kwargs", {})
        self.metric_annotation_kwargs = kwargs.get("metric_annotation_kwargs", {})

    def setup_plot(
        self, title, xlabel, ylabel, legend_loc="upper left", grid=True, figsize=(12, 6)
    ):
        """Set up the plot for the animation.

        Args:
            title: Title of the plot.
            xlabel: Label for the x-axis.
            ylabel: Label for the y-axis.
            legend_loc: Location of the legend.
            grid: Whether to show grid lines.
            figsize: Size of the figure.
        """
        if not self.plot_metric_progression:
            self.fig, self.ax = plt.subplots(figsize=figsize)
            self.ax.set_title(title, **self.title_kwargs)
            self.fig.suptitle(title, **self.suptitle_kwargs)
            self.ax.set_xlabel(xlabel, **self.xlabel_kwargs)
            self.ax.set_ylabel(ylabel, **self.ylabel_kwargs)
            self.ax.grid(grid, **self.grid_kwargs)
            self.metric_axes = None
            self.metric_lines = None
        else:
            import matplotlib.gridspec as gridspec

            n_metrics = (
                min(len(self.metric_fn), self.max_metric_subplots)
                if self.metric_fn
                else 1
            )
            # Main plot on the left, metrics stacked vertically on the right
            self.fig = plt.figure(figsize=figsize)
            gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
            self.ax = self.fig.add_subplot(gs[0, 0])
            # Metrics column: n_metrics rows, 1 column
            metric_gs = gridspec.GridSpecFromSubplotSpec(
                n_metrics, 1, subplot_spec=gs[0, 1], hspace=0.3
            )
            self.metric_axes = []
            self.metric_lines = []
            for i in range(n_metrics):
                metric_ax = self.fig.add_subplot(metric_gs[i, 0])
                (metric_line,) = metric_ax.plot(
                    [], [], label=f"Metric {i + 1}", color="green"
                )
                metric_ax.set_title(
                    f"{self.metric_fn[i].__name__}"
                    if self.metric_fn
                    else f"Metric {i + 1}",
                    fontsize=9,
                    **self.metric_title_kwargs,
                )
                metric_ax.set_xlabel("", **self.metric_xlabel_kwargs)
                metric_ax.set_ylabel(
                    "Metric Value", fontsize=8, **self.metric_ylabel_kwargs
                )
                metric_ax.tick_params(axis="both", which="major", labelsize=8)
                self.metric_axes.append(metric_ax)
                self.metric_lines.append(metric_line)
                self.ax.set_title(f"{self.dynamic_parameter}=", **self.title_kwargs)
            self.fig.suptitle(title, **self.suptitle_kwargs)
        if legend_loc is not None:
            # self.ax.legend(loc=legend_loc)
            # Will call legend() in update_plot() to update the legend
            self.add_legend = True
        else:
            self.add_legend = False
        self.ax.set_xlabel(xlabel, **self.xlabel_kwargs)
        self.ax.set_ylabel(ylabel, **self.ylabel_kwargs)
        self.ax.grid(grid, **self.grid_kwargs)
        plt.tight_layout()

    def update_metric_plot(self, frame):
        """Update the metric plot(s) for the current frame, and annotate with the current value of each metric in the top left corner."""
        if (
            self.metric_progression is not None
            and self.metric_lines is not None
            and self.metric_axes is not None
        ):
            for _, (progression, metric_line, metric_ax) in enumerate(
                zip(self.metric_progression, self.metric_lines, self.metric_axes)
            ):
                x_data = np.arange(len(progression))
                y_data = np.array(progression)
                metric_line.set_data(x_data, y_data)
                metric_ax.relim()
                metric_ax.autoscale_view()
                # Remove previous annotation if it exists
                if (
                    hasattr(metric_ax, "_current_metric_annotation")
                    and metric_ax._current_metric_annotation is not None
                ):
                    metric_ax._current_metric_annotation.remove()
                    metric_ax._current_metric_annotation = None
                # Add annotation for the current value (last value in progression) at the top left corner
                if len(x_data) > 0 and len(y_data) > 0:
                    annotation = metric_ax.annotate(
                        f"{y_data[-1]:.4g}",
                        xy=(0, 1),
                        xycoords="axes fraction",
                        xytext=(5, -5),
                        textcoords="offset points",
                        ha="left",
                        va="top",
                        fontsize=9,
                        color=metric_line.get_color()
                        if hasattr(metric_line, "get_color")
                        else "green",
                        bbox={
                            "boxstyle": "round,pad=0.3,rounding_size=0.2",
                            "fc": "#f8f8f8",  # solid light background
                            "ec": "#333333",  # solid border
                            "lw": 1.2,
                            "alpha": 1.0,
                        },
                        **self.metric_annotation_kwargs,
                    )
                    metric_ax._current_metric_annotation = annotation
                else:
                    metric_ax._current_metric_annotation = None

    @abstractmethod
    def update_model(self, frame):
        """Abstract method to update the model for a given frame. Must be implemented by subclasses."""
        raise NotImplementedError

    @abstractmethod
    def update_plot(self, frame):
        """Abstract method to update the plot for a given frame.Must be implemented by subclasses."""
        raise NotImplementedError

    def animate(self, frames, interval=150, blit=False, repeat=True):
        """Create the animation.

        Args:
            frames: Range of frames (e.g., window sizes).
            interval: Delay between frames in milliseconds.
            blit: Whether to use blitting for faster rendering.
            repeat: Whether to repeat the animation.
        """

        def _update(frame):
            self.update_model(frame)
            return self.update_plot(frame)

        self.ani = animation.FuncAnimation(
            self.fig,
            _update,
            frames=frames,
            interval=interval,
            blit=blit,
            repeat=repeat,
        )

        return self.ani

    def save(self, filename, writer="pillow", fps=5, dpi=100):
        """Save the animation to a file.

        Args:
            filename: Path to save the animation.
            writer: Writer to use (e.g., 'pillow' for GIF).
            fps: Frames per second.
            dpi: Dots per inch for the saved figure.
        """
        if not hasattr(self, "ani"):
            raise RuntimeError("Animation has not been created. Call `animate` first.")
        # print(f"Saving animation to {filename} (this may take a while)...")
        # progress_callback = lambda i, n: print(f"Saving frame {i+1}/{n}", end='\r')

        try:
            self.ani.save(filename, writer=writer, fps=fps, dpi=dpi)
            sys.stdout.write("\033[K")  # Clear the line
            print(f"Animation saved successfully to {filename}.")
        except Exception as e:
            sys.stdout.write("\033[K")  # Clear the line on error too
            print(f"\nError saving animation: {e}")

    def show(self):
        """Display the animation."""
        if not hasattr(self, "ani") or self.ani is None:
            raise RuntimeError("Animation has not been created. Call `animate` first.")
        if self.fig is None:
            raise RuntimeError("Plot has not been set up. Call `setup_plot` first.")

        try:
            plt.show()
            print("Animation displayed.")
        except Exception as e:
            print(f"Error showing animation: {e}")
            # Attempt to close the figure if it exists, in case plt.show failed partially
            if self.fig:
                plt.close(self.fig)
