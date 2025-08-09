import numpy as np

from .animation_base import AnimationBase


class ForecastingAnimation(AnimationBase):
    """Class for creating animations of forecasting models."""

    def __init__(
        self,
        model,
        train_series,
        test_series,
        forecast_steps,
        dynamic_parameter=None,
        static_parameters=None,
        keep_previous=False,
        max_previous=None,
        metric_fn=None,
        plot_metric_progression=False,
        max_metric_subplots=1,
        **kwargs,
    ):
        """Initialize the forecasting animation class.

        Args:
            model: The forecasting model.
            train_series: Training time series data.
            test_series: Testing time series data.
            forecast_steps: Number of steps to forecast.
            dynamic_parameter: The parameter to update dynamically (e.g., 'window', 'alpha', 'beta').
            static_parameters: Static parameters for the model.
                Should be a dictionary with parameter names as keys and their values.
            keep_previous: Whether to keep all previous lines with reduced opacity.
            max_previous: Maximum number of previous lines to keep.
            metric_fn: Optional metric function or list of functions (e.g., MSE, MAE) to calculate and display during animation.
            plot_metric_progression: Whether to plot the progression of metrics over frames.
            max_metric_subplots: Maximum number of metric subplots to display.
            **kwargs: Additional customization options (e.g., colors, line styles).
        """
        super().__init__(
            model,
            train_series,
            test_series,
            dynamic_parameter,
            static_parameters,
            keep_previous,
            metric_fn=metric_fn,
            plot_metric_progression=plot_metric_progression,
            max_metric_subplots=max_metric_subplots,
            **kwargs,
        )
        self._set_kwargs(**kwargs, subclass="ForecastingAnimation")
        self.forecast_steps = forecast_steps
        if self.keep_previous:
            self.previous_forecast_lines = []  # List to store previous forecast lines
            self.previous_fitted_lines = []  # List to store previous fitted lines
            self.max_previous = max_previous

        # Initialize plot elements
        self.train_indices = range(len(train_series))
        self.forecast_indices = range(
            len(train_series), len(train_series) + forecast_steps
        )
        self.fitted_line = None
        self.forecast_line = None

    def setup_plot(
        self, title, xlabel, ylabel, legend_loc="upper left", grid=True, figsize=(12, 6)
    ):
        """Set up the plot for forecasting animation."""
        super().setup_plot(title, xlabel, ylabel, legend_loc, grid, figsize)

        # Plot static elements using defaults
        self.ax.plot(self.train_indices, self.train_data, **self.train_line_kwargs)
        self.ax.axvline(x=len(self.train_data), **self.vline_kwargs)

        # Create placeholders for dynamic lines, with higher zorder and style
        (self.fitted_line,) = self.ax.plot([], [], **self.fitted_line_kwargs)
        (self.forecast_line,) = self.ax.plot([], [], **self.forecast_line_kwargs)

        # Auto-adjust y-limits based on the training data range
        min_y = min(self.train_data) - 0.5 * (
            max(self.train_data) - min(self.train_data)
        )
        max_y = max(self.train_data) + 0.5 * (
            max(self.train_data) - min(self.train_data)
        )
        self.ax.set_ylim(min_y, max_y)

        if self.add_legend:
            # Add legend to the plot
            self.ax.legend(loc=legend_loc, **self.legend_kwargs)

    def update_model(self, frame):
        """Update the model for the current frame.

        Args:
            frame: The current frame (e.g., parameter value).
        """
        # Dynamically update the model with the current frame and include static parameters
        self.model_instance = self.model(
            **{self.dynamic_parameter: frame}, **self.static_parameters
        )
        if not hasattr(self.model_instance, "fit"):
            raise AttributeError(
                f"{self.model.__name__} needs a 'fit' method to train the model."
            )
        try:
            self.fitted_values = self.model_instance.fit(self.train_data)
        except TypeError:
            try:
                # Where model.fit requires (X,y) format
                self.fitted_values = self.model_instance.fit(
                    np.arange(len(self.train_data)).reshape(-1, 1),
                    self.train_data,
                )
            except Exception as e:
                raise TypeError(
                    f"Model {self.model.__name__} fit failed with error: {e}. "
                    "Ensure the model's fit method is compatible with the training data format."
                ) from e

        # In-sample fitted values (for training data)
        if hasattr(self.model_instance, "predict"):  # sktime convention
            try:
                self.fitted_values = self.model_instance.predict(
                    np.arange(len(self.train_data)).reshape(-1, 1)
                )
            except Exception:
                self.fitted_values = np.array(self.train_data)
        elif self.fitted_values is None:
            self.fitted_values = np.array(self.train_data)

        # Forecast for test set
        if hasattr(self.model_instance, "forecast"):
            self.forecast_values = self.model_instance.forecast(
                steps=self.forecast_steps
            )
        elif hasattr(self.model_instance, "predict"):
            try:
                self.forecast_values = self.model_instance.predict(self.forecast_steps)
            except Exception:
                try:
                    X = np.arange(
                        len(self.train_data),
                        len(self.train_data) + self.forecast_steps,
                    ).reshape(-1, 1)
                    self.forecast_values = self.model_instance.predict(X)
                except Exception as e:
                    print(f"Error predicting forecast: {e}")
                    self.forecast_values = np.zeros(self.forecast_steps)
        else:
            raise AttributeError(
                f"{self.model.__name__} needs a 'forecast' or 'predict' method to generate forecasts."
            )

        # Convert to numpy arrays if pandas Series
        if hasattr(self.fitted_values, "to_numpy"):
            self.fitted_values = self.fitted_values.to_numpy()
        if hasattr(self.forecast_values, "to_numpy"):
            self.forecast_values = self.forecast_values.to_numpy()

        # Ensure 1D
        self.fitted_values = np.asarray(self.fitted_values).flatten()
        self.forecast_values = np.asarray(self.forecast_values).flatten()

    def update_plot(self, frame):
        """Update the plot for the current frame.

        Args:
            frame: The current frame (e.g., parameter value).
        """
        # --- Handle Previous Lines ---
        if self.keep_previous and self.forecast_line and self.fitted_line:
            # Limit the number of previous lines to avoid clutter
            if self.max_previous:
                while len(self.previous_forecast_lines) > self.max_previous:
                    self.previous_forecast_lines.pop(0)
                while len(self.previous_fitted_lines) > self.max_previous:
                    self.previous_fitted_lines.pop(0)

            self.previous_forecast_lines.append(self.forecast_line)
            for i, line in enumerate(self.previous_forecast_lines):
                line.set_alpha(0.1 + (0.4 / len(self.previous_forecast_lines)) * i)
                line.set_color("lightcoral")

            self.previous_fitted_lines.append(self.fitted_line)
            for i, line in enumerate(self.previous_fitted_lines):
                line.set_alpha(0.1 + (0.4 / len(self.previous_fitted_lines)) * i)
                line.set_color("lightgreen")

            (self.fitted_line,) = self.ax.plot([], [], **self.fitted_line_kwargs)

        # Update the dynamic lines with the latest fitted and forecasted values
        self.fitted_line.set_data(self.train_indices, self.fitted_values)
        self.forecast_line.set_data(self.forecast_indices, self.forecast_values)

        # --- Metric Handling (match RegressionAnimation style) ---
        if self.metric_fn:
            metrics = [
                metric_fn(self.test_data, self.forecast_values)
                for metric_fn in self.metric_fn
            ]
            frame_rounded = round(frame, 2) if isinstance(frame, float) else frame
            metric_strs = [
                f"{fn.__name__.capitalize()}: {metric:.4f}"
                for fn, metric in zip(self.metric_fn, metrics)
            ]
            metric_str = ", ".join(metric_strs)

            # Update metric_progression for each metric subplot (if present)
            if self.metric_progression is not None:
                for i in range(min(len(metrics), len(self.metric_progression))):
                    self.metric_progression[i].append(metrics[i])
                self.update_metric_plot(frame)

            if (
                self.plot_metric_progression
                and getattr(self, "metric_lines", None) is not None
            ):
                self.ax.set_title(
                    f"{self.dynamic_parameter}={frame_rounded}", **self.title_kwargs
                )
            else:
                self.ax.set_title(
                    f"{self.dynamic_parameter}={frame_rounded} - {metric_str}",
                    **self.title_kwargs,
                )
            print(f"{self.dynamic_parameter}: {frame_rounded}, {metric_str}", end="\r")
        else:
            frame_rounded = round(frame, 2) if isinstance(frame, float) else frame
            self.ax.set_title(
                f"Forecast ({self.dynamic_parameter}={frame_rounded})",
                **self.title_kwargs,
            )
            print(f"{self.dynamic_parameter}: {frame}", end="\r")

        # Return all artists that are updated for blitting
        if (
            self.plot_metric_progression
            and getattr(self, "metric_lines", None) is not None
        ):
            return [self.fitted_line, self.forecast_line, self.metric_lines]
        if hasattr(self, "previous_forecast_lines"):
            return [self.fitted_line, self.forecast_line] + self.previous_forecast_lines
        else:
            return [self.fitted_line, self.forecast_line]
