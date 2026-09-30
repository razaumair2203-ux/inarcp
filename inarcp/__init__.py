"""Innovation-normalized autoregressive conformal prediction."""
from .model import INARCP, history_scale
from .theory import (oracle_mean_length, efficiency_terms,
                     finite_calibration_mean_length, recommend_split)
from .clutter import ComplexINARCP, NoiseAwareINARCP, exact_coverage, os_coverage

__version__ = "0.3.0"
__all__ = ["INARCP", "history_scale", "oracle_mean_length", "efficiency_terms",
           "finite_calibration_mean_length", "recommend_split",
           "ComplexINARCP", "NoiseAwareINARCP", "exact_coverage", "os_coverage"]
