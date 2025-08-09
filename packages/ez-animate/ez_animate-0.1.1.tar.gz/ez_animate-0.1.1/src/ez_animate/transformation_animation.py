from .animation_base import AnimationBase


class TransformationAnimation(AnimationBase):
    """Class for animating data transformation steps (scaling, normalization, PCA, etc.)."""

    def __init__(
        self,
        transformer,
        X,
        dynamic_parameter=None,
        static_parameters=None,
        keep_previous=False,
        metric_fn=None,
        plot_metric_progression=None,
        max_metric_subplots=1,
        **kwargs,
    ):
        """Initialize the TransformationAnimation class.

        Args:
            transformer: The data transformer (e.g., scaler, normalizer, PCA).
            X: Input data array.
            dynamic_parameter: The parameter to update dynamically (e.g., n_components for PCA).
            static_parameters: Static parameters for the transformer.
            keep_previous: Whether to keep previous transformed states with reduced opacity.
            metric_fn: Optional metric function(s) to calculate and display during animation.
            plot_metric_progression: Whether to plot the progression of the metric over time.
            max_metric_subplots: Maximum number of metric subplots to display.
            **kwargs: Additional customization options for plotting.

        Raises:
            ValueError: If required arguments are missing or invalid.
        """
        if X is None:
            raise ValueError("X must be provided.")
        if not callable(getattr(transformer, "fit", None)):
            raise ValueError("transformer must have a fit method.")
        if not isinstance(dynamic_parameter, str):
            raise ValueError("dynamic_parameter must be a string.")
        if not isinstance(static_parameters, (dict, type(None))):
            raise ValueError("static_parameters must be a dictionary or None.")
        if not isinstance(keep_previous, bool):
            raise ValueError("keep_previous must be a boolean.")

        super().__init__(
            transformer,
            X,
            X,  # No test data needed for transformation
            dynamic_parameter=dynamic_parameter,
            static_parameters=static_parameters,
            keep_previous=keep_previous,
            metric_fn=metric_fn,
            plot_metric_progression=plot_metric_progression,
            max_metric_subplots=max_metric_subplots,
            **kwargs,
        )
        self._set_kwargs(**kwargs, subclass="TransformationAnimation")
        self.X = X
        self.transformed_X = None
        if self.keep_previous:
            self.previous_transforms = []

    def setup_plot(
        self, title, xlabel, ylabel, legend_loc="upper left", grid=True, figsize=(12, 6)
    ):
        """Set up the plot for transformation animation.

        Args:
            title: Title of the plot.
            xlabel: Label for the x-axis.
            ylabel: Label for the y-axis.
            legend_loc: Location of the legend.
            grid: Whether to show grid lines.
            figsize: Size of the figure.
        """
        super().setup_plot(title, xlabel, ylabel, legend_loc, grid, figsize)
        # Initial scatter plot of original data
        self.scatter = self.ax.scatter(
            self.X[:, 0], self.X[:, 1], label="Original Data", **self.scatter_kwargs
        )
        if self.add_legend:
            self.ax.legend(loc=legend_loc)

    def update_model(self, frame):
        """Update the transformer for the current frame.

        Args:
            frame: The current frame (e.g., parameter value).
        """
        params = {self.dynamic_parameter: frame}
        if self.static_parameters:
            params.update(self.static_parameters)
        self.transformer_instance = self.model(**params)
        self.transformer_instance.fit(self.X)
        self.transformed_X = self.transformer_instance.transform(self.X)

    def update_plot(self, frame):
        """Update the plot for the current frame.

        Args:
            frame: The current frame (e.g., parameter value).

        Returns:
            tuple: Updated scatter plot artist(s).
        """
        # Remove previous transformed scatter if exists
        if hasattr(self, "transformed_scatter") and self.transformed_scatter:
            self.transformed_scatter.remove()
        # Plot transformed data
        self.transformed_scatter = self.ax.scatter(
            self.transformed_X[:, 0],
            self.transformed_X[:, 1],
            label=f"Transformed (frame={frame})",
            **self.scatter_kwargs_test,
        )
        if self.add_legend:
            self.ax.legend()
        # Optionally update metrics
        if self.metric_fn:
            metrics = [fn(self.X, self.transformed_X) for fn in self.metric_fn]
            if self.metric_progression is not None:
                for i in range(min(len(metrics), len(self.metric_progression))):
                    self.metric_progression[i].append(metrics[i])
                self.update_metric_plot(frame)
            metric_str = ", ".join(
                [f"{fn.__name__}: {m:.4f}" for fn, m in zip(self.metric_fn, metrics)]
            )
            self.ax.set_title(
                f"{self.dynamic_parameter}={frame} - {metric_str}", **self.title_kwargs
            )
        else:
            self.ax.set_title(f"{self.dynamic_parameter}={frame}", **self.title_kwargs)
        return (self.transformed_scatter,)
