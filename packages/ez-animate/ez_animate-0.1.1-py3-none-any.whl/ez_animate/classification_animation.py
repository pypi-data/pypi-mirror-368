import matplotlib.pyplot as plt
import numpy as np

from .animation_base import AnimationBase
from .utils import PCA, train_test_split


class ClassificationAnimation(AnimationBase):
    """Class for creating animations of classification models."""

    def __init__(
        self,
        model,
        X,
        y,
        test_size=0.3,
        dynamic_parameter=None,
        static_parameters=None,
        keep_previous=False,
        scaler=None,
        pca_components=2,
        plot_step=0.02,
        metric_fn=None,
        plot_metric_progression=None,
        max_metric_subplots=1,
        **kwargs,
    ):
        """Initialize the classification animation class.

        Args:
            model: The classification model.
            X: Feature matrix (input data).
            y: Target vector (output data).
            test_size: Proportion of the dataset to include in the test split.
            dynamic_parameter: The parameter to update dynamically (e.g., 'alpha', 'beta').
            static_parameters: Additional static parameters for the model.
                Should be a dictionary with parameter names as keys and their values.
            keep_previous: Whether to keep all previous lines with reduced opacity.
            scaler: Optional scaler for preprocessing the data.
            pca_components: Number of components to use for PCA.
            plot_step: Resolution of the decision boundary mesh.
            metric_fn: Optional metric function or list of functions (e.g., accuracy, F1) to calculate and display during animation.
            plot_metric_progression: Whether to plot the progression of the metric over time.
            max_metric_subplots: Maximum number of metric subplots to display.
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
        if not isinstance(pca_components, (int, type(None))) or pca_components < 1:
            raise ValueError("pca_components must be an integer greater than 0.")
        if not isinstance(plot_step, float):
            raise ValueError("plot_step must be a float.")

        self.scaler_instance = scaler
        self.pca_instance = None
        self.needs_pca = False

        if self.scaler_instance is not None:
            print("Applying scaler...")
            X = self.scaler_instance.fit_transform(X)

        if X.shape[1] > 2:
            self.needs_pca = True
            print(
                f"Input has {X.shape[1]} features. Applying PCA with n_components={pca_components}."
            )
            if pca_components != 2:
                print(
                    "Warning: Classification animation requires 2 components for plotting. Forcing pca_components=2."
                )
                pca_components = 2
            self.pca_instance = PCA(n_components=pca_components)
            X_transformed = self.pca_instance.fit_transform(X)
        elif X.shape[1] == 2:
            X_transformed = X  # Use original X if 2 features
        else:
            raise ValueError(
                "Classification animation requires at least 2 features or PCA to 2 components."
            )

        X_train, X_test, y_train, y_test = train_test_split(
            X_transformed, y, test_size=test_size, random_state=42
        )
        super().__init__(
            model,
            (X_train, y_train),
            (X_test, y_test),
            dynamic_parameter=dynamic_parameter,
            static_parameters=static_parameters,
            keep_previous=keep_previous,
            metric_fn=metric_fn,
            plot_metric_progression=plot_metric_progression,
            max_metric_subplots=max_metric_subplots,
            **kwargs,
        )
        self._set_kwargs(**kwargs, subclass="ClassificationAnimation")

        self.X_train, self.y_train = X_train, y_train
        self.X_test, self.y_test = X_test, y_test

        # Create mesh grid for decision boundary based on *all* transformed data
        x_min, x_max = X_transformed[:, 0].min() - 0.5, X_transformed[:, 0].max()
        y_min, y_max = X_transformed[:, 1].min() - 0.5, X_transformed[:, 1].max()
        self.xx, self.yy = np.meshgrid(
            np.arange(x_min, x_max, plot_step),
            np.arange(y_min, y_max, plot_step),
        )

        # Store unique classes and assign colors
        self.unique_classes = np.unique(y)
        cmap = plt.cm.coolwarm  # Default colormap
        self.colors = cmap(np.linspace(0, 1, len(self.unique_classes)))

        self.scatter_train_dict = {}
        self.scatter_test_dict = {}

        if self.keep_previous:
            self.previous_decision_lines = []  # Store previous decision boundaries

    def setup_plot(
        self, title, xlabel, ylabel, legend_loc="upper left", grid=True, figsize=(12, 6)
    ):
        """Set up the plot for classification animation."""
        # Adjust labels if PCA was used
        effective_xlabel = f"{xlabel} (PCA Comp 1)" if self.needs_pca else xlabel
        effective_ylabel = f"{ylabel} (PCA Comp 2)" if self.needs_pca else ylabel

        super().setup_plot(
            title, effective_xlabel, effective_ylabel, legend_loc, grid, figsize
        )

        # Plot training data points, colored by class
        for i, class_value in enumerate(self.unique_classes):
            class_mask = self.y_train == class_value
            scatter = self.ax.scatter(
                self.X_train[class_mask, 0],
                self.X_train[class_mask, 1],
                color=self.colors[i],
                label=f"Train Class {class_value}",
                **self.scatter_kwargs,
            )
            self.scatter_train_dict[class_value] = scatter

        # Plot test data points (optional)
        for i, class_value in enumerate(self.unique_classes):
            class_mask = self.y_test == class_value
            scatter = self.ax.scatter(
                self.X_test[class_mask, 0],
                self.X_test[class_mask, 1],
                color=self.colors[i],
                label=f"Test Class {class_value}",
                **self.scatter_kwargs_test,
            )
            self.scatter_test_dict[class_value] = scatter

        # Set plot limits based on meshgrid
        self.ax.set_xlim(self.xx.min(), self.xx.max())
        self.ax.set_ylim(self.yy.min(), self.yy.max())

        if self.add_legend:
            self.ax.legend(loc=legend_loc)

    def update_model(self, frame):
        """Update the classification model for the current frame.

        Args:
            frame: The current frame (e.g., parameter value).
        """
        # Dynamically update the model with the current frame and include static parameters
        self.model_instance = self.model(
            **{self.dynamic_parameter: frame}, **self.static_parameters
        )
        self.model_instance.fit(self.X_train, self.y_train)

    def update_plot(self, frame):
        """Update the plot for the current frame.

        Args:
            frame: The current frame (e.g., parameter value).
        """
        # --- Handle Previous Decision Boundaries ---
        if hasattr(self, "decision_boundary") and self.decision_boundary:
            try:
                self.decision_boundary.remove()
            except Exception:
                if hasattr(self.decision_boundary, "collections"):
                    for collection in self.decision_boundary.collections:
                        collection.remove()

        if hasattr(self, "decision_boundary_lines") and self.decision_boundary_lines:
            if self.keep_previous:
                self.previous_decision_lines.append(self.decision_boundary_lines)
                for i, collection in enumerate(self.previous_decision_lines):
                    try:
                        collection.set_alpha(
                            0.1 + (0.4 / len(self.previous_decision_lines)) * i
                        )
                        collection.set_color("black")
                    except Exception:
                        pass
            else:
                try:
                    self.decision_boundary_lines.remove()
                except Exception:
                    if hasattr(self.decision_boundary_lines, "collections"):
                        for collection in self.decision_boundary_lines.collections:
                            collection.remove()

        # Predict on the mesh grid
        mesh_points = np.c_[self.xx.ravel(), self.yy.ravel()]
        try:
            Z = self.model_instance.predict(mesh_points)
        except AttributeError:
            try:
                Z_proba = self.model_instance.predict_proba(mesh_points)
                Z = np.argmax(Z_proba, axis=1)
                if not np.array_equal(
                    self.model_instance.classes_, np.arange(len(self.unique_classes))
                ):
                    Z = self.model_instance.classes_[Z]
            except AttributeError:
                raise AttributeError(
                    f"{self.model.__name__} needs a 'predict' or 'predict_proba' method returning class labels."
                ) from None
        Z = Z.reshape(self.xx.shape)

        # Plot the current decision boundary contourf (filled regions)
        self.decision_boundary = self.ax.contourf(
            self.xx,
            self.yy,
            Z,
            levels=np.arange(len(self.unique_classes) + 1) - 0.5,
            **self.decision_boundary_kwargs,
        )

        # If only two classes, plot the decision boundary lines
        if len(np.unique(self.y_train)) == 2:
            self.decision_boundary_lines = self.ax.contour(
                self.xx,
                self.yy,
                Z,
                levels=[0.5],
                **self.decision_boundary_line_kwargs,
            )

        # --- Metric Handling (match RegressionAnimation style) ---
        if self.metric_fn:
            y_pred_test = self.model_instance.predict(self.X_test)
            metrics = [
                metric_fn(self.y_test, y_pred_test) for metric_fn in self.metric_fn
            ]
            # Update metric_progression for each metric subplot (if present)
            if self.metric_progression is not None:
                for i in range(min(len(metrics), len(self.metric_progression))):
                    self.metric_progression[i].append(metrics[i])
                self.update_metric_plot(frame)

            frame_rounded = round(frame, 2)
            metric_strs = [
                f"{fn.__name__.capitalize()}: {metric:.4f}"
                for fn, metric in zip(self.metric_fn, metrics)
            ]
            metric_str = ", ".join(metric_strs)

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
            self.ax.set_title(
                f"Classification ({self.dynamic_parameter}={frame})",
                **self.title_kwargs,
            )
            print(f"{self.dynamic_parameter}: {frame}", end="\r")

        # Return all artists that are updated for blitting
        if (
            self.plot_metric_progression
            and getattr(self, "metric_lines", None) is not None
        ):
            if len(np.unique(self.y_train)) == 2:
                return (
                    self.decision_boundary,
                    self.decision_boundary_lines,
                    self.metric_lines,
                )
            else:
                return (self.decision_boundary, self.metric_lines)
        else:
            if len(np.unique(self.y_train)) == 2:
                return (self.decision_boundary, self.decision_boundary_lines)
            else:
                return (self.decision_boundary,)
