import warnings

import matplotlib.pyplot as plt
import numpy as np

from .animation_base import AnimationBase
from .utils import PCA, train_test_split


class ClusteringAnimation(AnimationBase):
    """Animation class for visualizing clustering algorithms (e.g., K-Means)."""

    def __init__(
        self,
        model,
        data,
        labels=None,
        test_size=0.3,
        dynamic_parameter=None,
        static_parameters=None,
        keep_previous=False,
        trace_centers=False,
        scaler=None,
        pca_components=2,
        metric_fn=None,
        plot_metric_progression=False,
        max_metric_subplots=1,
        **kwargs,
    ):
        """Initialize the clustering animation class.

        Args:
            model: The clustering model (e.g., KMeans instance).
            data: The input data for clustering.
            labels: Optional true labels for coloring points.
            test_size: Proportion of data to use as test set.
            dynamic_parameter: The parameter to update dynamically (e.g., 'n_iter').
            static_parameters: Static parameters for the model.
            keep_previous: Whether to keep previous cluster assignments with reduced opacity.
            trace_centers: Whether to trace the movement of cluster centers over iterations.
            scaler: Optional scaler for data preprocessing.
            pca_components: Number of PCA components for dimensionality reduction.
            metric_fn: Optional metric function or list of functions (e.g., silhouette_score) to calculate and display during animation.
            plot_metric_progression: Whether to plot the progression of metrics over frames.
            max_metric_subplots: Maximum number of metric subplots to display.
            **kwargs: Additional customization options.
        """
        # Input validation
        if data is None or len(data) == 0:
            raise ValueError("Input data cannot be None or empty.")
        if not isinstance(data, np.ndarray):
            raise TypeError("Input data must be a numpy array.")
        if labels is not None and not isinstance(labels, (np.ndarray, list)):
            raise TypeError("Labels must be a numpy array or list.")
        if not isinstance(dynamic_parameter, str):
            raise ValueError("dynamic_parameter must be a string.")
        if not isinstance(static_parameters, (dict, type(None))):
            raise ValueError("static_parameters must be a dictionary or None.")
        if not isinstance(keep_previous, bool):
            raise ValueError("keep_previous must be a boolean.")
        if not isinstance(pca_components, (int, type(None))) or pca_components < 1:
            raise ValueError("pca_components must be an integer greater than 0.")
        if trace_centers is not None and not isinstance(trace_centers, bool):
            raise ValueError("trace_centers must be a boolean.")

        self.scaler_instance = scaler
        self.pca_instance = None
        self.needs_pca = False

        if self.scaler_instance is not None:
            print("Applying scaler...")
            data = self.scaler_instance.fit_transform(data)

        if data.shape[1] > 2:
            self.needs_pca = True
            print(
                f"Input has {data.shape[1]} features. Applying PCA with n_components={pca_components}."
            )
            if pca_components != 2:
                print(
                    "Warning: Classification animation requires 2 components for plotting. Forcing pca_components=2."
                )
                pca_components = 2
            self.pca_instance = PCA(n_components=pca_components)
            data_transformed = self.pca_instance.fit_transform(data)
        elif data.shape[1] < 2:
            raise ValueError(
                "Classification animation requires at least 2 features or PCA to 2 components."
            )
        else:
            data_transformed = data  # Use original X if 2 features

        # If no labels provided, create dummy labels
        if labels is None:
            dummy_labels = np.zeros(data_transformed.shape[0], dtype=int)

        X_train, X_test, y_train, y_test = train_test_split(
            data_transformed,
            dummy_labels if labels is None else labels,
            test_size=test_size,
            random_state=42,
        )

        self.X_train, self.X_test = X_train, X_test
        if labels is not None:
            self.y_train, self.y_test = y_train, y_test

        super().__init__(
            model,
            (X_train, y_train),
            (X_test, y_test),
            dynamic_parameter=dynamic_parameter,
            static_parameters=static_parameters,
            keep_previous=keep_previous,
            metric_fn=metric_fn,
            scaler=scaler,
            pca_components=pca_components,
            plot_metric_progression=plot_metric_progression,
            max_metric_subplots=max_metric_subplots,
            **kwargs,
        )
        self._set_kwargs(**kwargs, subclass="ClusteringAnimation")
        self.keep_previous = keep_previous
        self.trace_centers = trace_centers
        self.previous_centers = []
        self.previous_labels = []

        self.labels = labels
        if labels is not None:
            # Store unique classes and assign colors
            self.unique_labels = np.unique(labels)
            cmap = plt.cm.coolwarm  # Default colormap
            self.colors = cmap(np.linspace(0, 1, len(self.unique_labels)))

    def setup_plot(
        self,
        title,
        xlabel,
        ylabel,
        use_true_labels=False,
        legend_loc="upper left",
        grid=True,
        figsize=(12, 6),
    ):
        """Set up the plot for the clustering animation.

        Args:
            title: Title of the plot.
            xlabel: Label for the x-axis.
            ylabel: Label for the y-axis.
            use_true_labels: Whether to color points by true labels if available.
            legend_loc: Location of the legend.
            grid: Whether to display a grid.
            figsize: Size of the figure.
        """
        # Adjust labels if PCA was used
        effective_xlabel = f"{xlabel} (PCA Comp 1)" if self.needs_pca else xlabel
        effective_ylabel = f"{ylabel} (PCA Comp 2)" if self.needs_pca else ylabel

        super().setup_plot(
            title, effective_xlabel, effective_ylabel, legend_loc, grid, figsize
        )

        # Plot the points colored by their cluster labels (training data)
        if self.labels is not None and use_true_labels:
            for i, label in enumerate(self.unique_labels):
                mask = self.y_train == label
                self.ax.scatter(
                    self.X_train[mask, 0],
                    self.X_train[mask, 1],
                    color=self.colors[i],
                    label=f"Train Class {label}",
                    **self.scatter_kwargs,
                )
            # Plot test data points
            for i, label in enumerate(self.unique_labels):
                mask = self.y_test == label
                self.ax.scatter(
                    self.X_test[mask, 0],
                    self.X_test[mask, 1],
                    color=self.colors[i],
                    label=f"Test Class {label}",
                    **self.scatter_kwargs_test,
                )

        else:
            # Plot all points in gray, we will update colors in animation
            self.ax.scatter(
                self.X_train[:, 0],
                self.X_train[:, 1],
                **self.cluster_gray_train_kwargs,
            )
            self.ax.scatter(
                self.X_test[:, 0],
                self.X_test[:, 1],
                **self.cluster_gray_test_kwargs,
            )

        # Set plot limits with some padding
        all_data = np.vstack((self.X_train, self.X_test))
        x_min, x_max = all_data[:, 0].min() - 1, all_data[:, 0].max() + 1
        y_min, y_max = all_data[:, 1].min() - 1, all_data[:, 1].max() + 1
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)

        if self.add_legend:
            self.ax.legend(loc=legend_loc)

    def update_model(self, frame):
        """Update the clustering model for the current frame.

        Args:
            frame: The current frame index.
        """
        # Dynamically update the model with the current frame and include static parameters
        try:
            self.model_instance = self.model(
                **{self.dynamic_parameter: frame}, **self.static_parameters
            )
        except TypeError:
            # sega_learn models may require X during initialization
            self.model_instance = self.model(
                X=self.X_train,
                **{self.dynamic_parameter: frame},
                **self.static_parameters,
            )
            self.model_instance.fit()
            return

        if hasattr(self, "y_train"):
            self.model_instance.fit(self.X_train, self.y_train)
        else:
            self.model_instance.fit(self.X_train)

    def update_plot(self, frame):
        """Update the plot for the current frame.

        Args:
            frame: The current frame index.
        """
        # Remove previous cluster centers and assignments if present
        if hasattr(self, "cluster_centers_plot") and self.cluster_centers_plot:
            try:
                for c in self.cluster_centers_plot:
                    c.remove()
            except Exception:
                pass
        if hasattr(self, "cluster_assignments_plot") and self.cluster_assignments_plot:
            try:
                for s in self.cluster_assignments_plot:
                    s.remove()
            except Exception:
                pass

        # Update the model for the current frame
        self.update_model(frame)

        # Predict cluster assignments for all data
        all_data = np.vstack((self.X_train, self.X_test))
        try:
            cluster_labels = self.model_instance.predict(all_data)
        except Exception:
            # Some clustering models use labels_ after fit
            cluster_labels = getattr(self.model_instance, "labels_", None)
            if cluster_labels is None:
                raise AttributeError(
                    f"{self.model.__name__} must have a 'predict' method or 'labels_' attribute after fitting."
                ) from None

        # Plot the points colored by their cluster assignment, distinguishing X_train and X_test
        n_clusters = len(np.unique(cluster_labels))

        # Use the recommended way to get a colormap in Matplotlib >=3.7
        try:
            cmap = plt.colormaps.get_cmap("tab10")
        except AttributeError:
            # Fallback for older matplotlib
            cmap = plt.cm.get_cmap("tab10")

        self.cluster_assignments_plot = []
        n_train = self.X_train.shape[0]
        _n_test = self.X_test.shape[0]
        for i in range(n_clusters):
            # Mask for X_train
            mask_train = cluster_labels[:n_train] == i
            if np.any(mask_train):
                scatter_train = self.ax.scatter(
                    self.X_train[mask_train, 0],
                    self.X_train[mask_train, 1],
                    color=cmap(i),
                    label=f"Cluster {i} (train)",
                    **self.scatter_kwargs,
                )
                self.cluster_assignments_plot.append(scatter_train)
            # Mask for X_test
            mask_test = cluster_labels[n_train:] == i
            if np.any(mask_test):
                scatter_test = self.ax.scatter(
                    self.X_test[mask_test, 0],
                    self.X_test[mask_test, 1],
                    color=cmap(i),
                    label=f"Cluster {i} (test)",
                    **self.scatter_kwargs_test,
                )
                self.cluster_assignments_plot.append(scatter_test)

        # Plot cluster centers if available
        self.cluster_centers_plot = []
        centers = getattr(self.model_instance, "cluster_centers_", None)
        if centers is not None:
            if self.pca_instance is not None and centers.shape[1] != 2:
                centers = self.pca_instance.transform(centers)
            center_plot = self.ax.scatter(
                centers[:, 0],
                centers[:, 1],
                c=cmap(np.arange(n_clusters)),
                **self.cluster_center_kwargs,
            )
            self.cluster_centers_plot.append(center_plot)

        # Optionally keep previous cluster centers and trace their movement
        if self.keep_previous and centers is not None:
            self.previous_centers.append(centers.copy())
            n_prev = len(self.previous_centers)
            for i, prev in enumerate(self.previous_centers[:-1]):
                # Alpha ranges from 0.1 to 0.5 as i goes from 0 to n_prev-2
                alpha = 0.1 + 0.4 / max(1, n_prev - 1) * i if n_prev > 1 else 0.1
                prev_kwargs = dict(self.prev_center_kwargs)
                prev_kwargs["alpha"] = alpha
                prev_plot = self.ax.scatter(
                    prev[:, 0],
                    prev[:, 1],
                    **prev_kwargs,
                )
                self.cluster_centers_plot.append(prev_plot)

        # Trace cluster centers with lines if enabled and number of centers is consistent
        if self.trace_centers and len(self.previous_centers) > 1:
            # Only draw lines if all previous centers have the same shape as current
            consistent = all(pc.shape == centers.shape for pc in self.previous_centers)
            if consistent:
                # Draw a line for each center across all iterations
                prev_arr = np.stack(
                    self.previous_centers
                )  # shape: (n_iters, n_centers, 2)
                n_centers = prev_arr.shape[1]
                for k in range(n_centers):
                    trace_kwargs = dict(self.trace_line_kwargs)
                    trace_kwargs["color"] = cmap(k)
                    self.ax.plot(
                        prev_arr[:, k, 0],
                        prev_arr[:, k, 1],
                        **trace_kwargs,
                    )
            else:
                # Warning
                warnings.warn(
                    "Cannot trace centers: inconsistent number of centers across iterations.",
                    UserWarning,
                    stacklevel=2,
                )

        # Update the title with the current frame and optional metrics
        def is_clustering_metric(fn):
            # Check for common clustering metric names
            clustering_metrics = [
                "silhouette_score",
                "calinski_harabasz_score",
                "davies_bouldin_score",
            ]
            return any(name in fn.__name__ for name in clustering_metrics)

        # --- Metric Handling (match RegressionAnimation style) ---
        if self.metric_fn:
            y_pred_test = self.model_instance.predict(self.X_test)
            metrics = []
            for fn in self.metric_fn:
                if is_clustering_metric(fn):
                    val = fn(self.X_test, y_pred_test)
                else:
                    val = fn(self.y_test, y_pred_test)
                metrics.append(round(val, 4))
            frame_rounded = round(frame, 2)
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
                self.ax.set_title(f"{self.dynamic_parameter}={frame_rounded}")
            else:
                self.ax.set_title(
                    f"{self.dynamic_parameter}={frame_rounded} - {metric_str}",
                    fontsize=10,
                )
            print(f"{self.dynamic_parameter}: {frame_rounded}, {metric_str}", end="\r")
        else:
            self.ax.set_title(f"Clustering ({self.dynamic_parameter}={frame})")
            print(f"{self.dynamic_parameter}: {frame}", end="\r")

        # Return all artists that are updated for blitting
        if (
            self.plot_metric_progression
            and getattr(self, "metric_lines", None) is not None
        ):
            return tuple(
                self.cluster_assignments_plot
                + self.cluster_centers_plot
                + [self.metric_lines]
            )
        return tuple(self.cluster_assignments_plot + self.cluster_centers_plot)
