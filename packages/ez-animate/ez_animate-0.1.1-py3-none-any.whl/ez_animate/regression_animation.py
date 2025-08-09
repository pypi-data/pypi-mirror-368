import numpy as np

from .animation_base import AnimationBase
from .utils import PCA, train_test_split


class RegressionAnimation(AnimationBase):
    """Class for creating animations of regression models."""

    def __init__(
        self,
        model,
        X,
        y,
        test_size=0.3,
        dynamic_parameter=None,
        static_parameters=None,
        keep_previous=False,
        max_previous=None,
        pca_components=1,
        metric_fn=None,
        plot_metric_progression=False,
        max_metric_subplots=1,
        **kwargs,
    ):
        """Initialize the regression animation class.

        Args:
            model: The regression model.
            X: Feature matrix (input data).
            y: Target vector (output data).
            test_size: Proportion of the dataset to include in the test split.
            dynamic_parameter: The parameter to update dynamically (e.g., 'alpha', 'beta').
            static_parameters: Additional static parameters for the model.
                Should be a dictionary with parameter names as keys and their values.
            keep_previous: Whether to keep all previous lines with reduced opacity.
            max_previous: Maximum number of previous lines to keep.
            pca_components: Number of components to use for PCA.
            metric_fn: Optional metric function or list of functions (e.g., MSE, R2) to calculate and display during animation.
            plot_metric_progression: Whether to plot the progression of the metric over time.
            max_metric_subplots: Maximum number of subplots to show for metric progression (if multiple metrics).
            **kwargs: Additional customization options (e.g., colors, line styles).
        """
        # Input validation
        if X is None or y is None:
            raise ValueError("X and y must be provided.")
        if test_size > 1 or test_size < 0:
            raise ValueError("test_size must be between 0 and 1.")
        if not isinstance(dynamic_parameter, str):
            raise ValueError("dynamic_parameter must be a string.")
        if not isinstance(static_parameters, (dict, type(None))):
            raise ValueError("static_parameters must be a dictionary or None.")
        if not isinstance(keep_previous, bool):
            raise ValueError("keep_previous must be a boolean.")
        if not isinstance(max_previous, (int, type(None))):
            raise ValueError("max_previous must be an integer or None.")
        if not isinstance(pca_components, (int, type(None))) or pca_components < 1:
            raise ValueError("pca_components must be an integer greater than 0.")

        if not isinstance(max_metric_subplots, int) or max_metric_subplots < 1:
            raise ValueError("max_metric_subplots must be an integer greater than 0.")

        self.max_metric_subplots = max_metric_subplots

        if keep_previous:
            self.max_previous = max_previous

        # Perform PCA if needed before splitting and passing to base
        self.needs_pca = X.shape[1] > 1
        self.pca_instance = None
        if self.needs_pca:
            print(
                f"Input has {X.shape[1]} features. Applying PCA with n_components={pca_components}."
            )
            self.pca_instance = PCA(n_components=pca_components)
            X_transformed = self.pca_instance.fit_transform(X)
            if pca_components == 1:
                X_transformed = X_transformed.reshape(
                    -1, 1
                )  # Ensure 2D array even for 1 component
        else:
            X_transformed = X  # Use original X if no PCA needed

        # Ensure X is 2D
        if X_transformed.ndim == 1:
            X_transformed = X_transformed.reshape(-1, 1)

        # Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X_transformed, y, test_size=test_size, random_state=42
        )
        super().__init__(
            model,
            (X_train, y_train),
            (X_test, y_test),
            dynamic_parameter,
            static_parameters,
            keep_previous,
            metric_fn=metric_fn,
            plot_metric_progression=plot_metric_progression,
            max_metric_subplots=max_metric_subplots,
            **kwargs,
        )
        self._set_kwargs(**kwargs, subclass="RegressionAnimation")

        # Split training and testing data into features and target
        self.X_train, self.y_train = X_train, y_train
        self.X_test, self.y_test = X_test, y_test

        # Initialize plot elements
        self.scatter_points = None
        self.scatter_points_test = None
        self.predicted_line = None

        if self.keep_previous:
            self.previous_predicted_lines = []  # List to store previous predicted lines

    def setup_plot(
        self, title, xlabel, ylabel, legend_loc="upper left", grid=True, figsize=(12, 6)
    ):
        """Set up the plot for regression animation."""
        # Use generic "Feature" label if PCA was applied
        if self.needs_pca and self.pca_instance.n_components == 1:
            effective_xlabel = f"{xlabel} (PCA Component 1)"
        elif self.X_train.shape[1] == 1:
            effective_xlabel = xlabel  # Use original if only 1 feature initially
        else:
            effective_xlabel = "Feature 1"  # Fallback for unexpected cases
            print("Warning: Plotting only the first feature for regression line.")

        super().setup_plot(title, effective_xlabel, ylabel, legend_loc, grid, figsize)

        # Plot static elements (scatter points for training data)
        self.scatter_points = self.ax.scatter(
            self.X_train[:, 0],
            self.y_train,
            label="Training Data",
            **self.scatter_kwargs,
        )
        # Plot test data points with different marker
        self.scatter_points_test = self.ax.scatter(
            self.X_test[:, 0],
            self.y_test,
            label="Test Data",
            **self.scatter_kwargs_test,
        )

        # Create a placeholder for the predicted regression line
        (self.predicted_line,) = self.ax.plot(
            [], [], label="Regression Line", **self.line_kwargs
        )

        if self.add_legend:
            # Add legend to the plot
            self.ax.legend(loc=legend_loc, **self.legend_kwargs)

    def update_model(self, frame):
        """Update the regression model for the current frame.

        Args:
            frame: The current frame (e.g., parameter value).
        """
        # Dynamically update the model with the current frame and include static parameters
        self.model_instance = self.model(
            **{self.dynamic_parameter: frame}, **self.static_parameters
        )
        self.model_instance.fit(self.X_train, self.y_train)
        # Sort X_test for plotting the line correctly
        sort_indices = np.argsort(self.X_test[:, 0])
        self.X_test_sorted = self.X_test[sort_indices]
        self.predicted_values = self.model_instance.predict(self.X_test_sorted)

    def update_plot(self, frame):
        """Update the plot for the current frame.

        Args:
            frame: The current frame (e.g., parameter value).
        """
        # --- Handle Previous Lines ---
        if self.keep_previous and self.predicted_line:
            # Limit the number of previous lines to avoid clutter (optional)
            if self.max_previous:
                while len(self.previous_predicted_lines) > self.max_previous:
                    # Remove the oldest line, pop is inplace
                    self.previous_predicted_lines.pop(0)

            # For all previous predicted lines, set alpha from 0.1 to 0.5 based on the number of lines
            self.previous_predicted_lines.append(self.predicted_line)
            for i, line in enumerate(self.previous_predicted_lines):
                line.set_alpha(0.1 + (0.4 / len(self.previous_predicted_lines)) * i)
                # Optionally set color for previous lines, or leave as is

            # Add a new predicted line
            # Remove zorder from kwargs to avoid conflicts
            line_kwargs = {
                **self.line_kwargs,
                "zorder": len(self.previous_predicted_lines) + 1,
            }
            (self.predicted_line,) = self.ax.plot(
                [],
                [],
                label="Regression Line",
                **line_kwargs,
            )

        # Update the regression line with the predicted values
        self.predicted_line.set_data(self.X_test_sorted[:, 0], self.predicted_values)

        # Update the title with the current frame and optional metrics
        if self.metric_fn:
            # Calculate metrics using the *original* test set order predictions
            y_pred_test_original_order = self.model_instance.predict(self.X_test)
            metrics = [
                metric_fn(self.y_test, y_pred_test_original_order)
                for metric_fn in self.metric_fn
            ]
            # Update metric_progression for each metric subplot (up to max_metric_subplots)
            if self.metric_progression is not None:
                for i in range(min(len(metrics), len(self.metric_progression))):
                    self.metric_progression[i].append(metrics[i])
                self.update_metric_plot(frame)

            frame_rounded = round(frame, 2)
            # Compose metric string for title/print
            metric_strs = [
                f"{fn.__name__.capitalize()}: {metric:.4f}"
                for fn, metric in zip(self.metric_fn, metrics)
            ]
            metric_str = ", ".join(metric_strs)

            if self.plot_metric_progression:
                self.ax.set_title(
                    f"{self.dynamic_parameter}={frame_rounded}", **self.title_kwargs
                )
            else:
                self.ax.set_title(
                    f"{self.dynamic_parameter}={frame_rounded} - {metric_str}",
                    **self.title_kwargs,
                )
            print(
                f"{self.dynamic_parameter}: {frame_rounded}, {metric_str}",
                end="\r",
            )
        else:
            self.ax.set_title(
                f"Regression ({self.dynamic_parameter}={frame})", **self.title_kwargs
            )
            print(f"{self.dynamic_parameter}: {frame}", end="\r")

        # Return all artists that are updated for blitting
        if self.plot_metric_progression and self.metric_lines is not None:
            return (self.predicted_line, self.metric_lines)
        return (self.predicted_line,)
