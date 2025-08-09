__version__ = "0.1.0"
from .classification_animation import ClassificationAnimation
from .clustering_animation import ClusteringAnimation
from .forecasting_animation import ForecastingAnimation
from .regression_animation import RegressionAnimation
from .transformation_animation import TransformationAnimation
from .utils import PCA, train_test_split

__all__ = [
    "ForecastingAnimation",
    "RegressionAnimation",
    "ClassificationAnimation",
    "ClusteringAnimation",
    "TransformationAnimation",
    "PCA",
    "train_test_split",
]
