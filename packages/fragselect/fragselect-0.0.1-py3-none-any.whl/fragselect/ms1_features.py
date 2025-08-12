from enum import Enum
from dataclasses import dataclass
from typing import Set


@dataclass(frozen=True)
class FeatureGroups:
    """Groups of related features for mass spectrometry data analysis"""

    # Chromatographic features
    CHROMATOGRAPHIC: Set[str] = frozenset(
        {
            "base_width_mobility",
            "base_width_rt",
            "rt_observed",
            "rt_calibrated",
            "rt_library",
            "delta_rt",
            "cycle_fwhm",
        }
    )

    # MS1 related features
    MS1: Set[str] = frozenset(
        {
            "mono_ms1_intensity",
            "top_ms1_intensity",
            "sum_ms1_intensity",
            "weighted_ms1_intensity",
            "mono_ms1_height",
            "top_ms1_height",
            "sum_ms1_height",
            "weighted_ms1_height",
        }
    )

    # Mass accuracy features
    MASS_ACCURACY: Set[str] = frozenset(
        {
            "weighted_mass_deviation",
            "weighted_mass_error",
            "mz_observed",
            "mz_library",
            "mz_calibrated",
            "mean_ms2_mass_error",
            "top_3_ms2_mass_error",
            "mean_overlapping_mass_error",
        }
    )

    # Ion correlation features
    ION_CORRELATION: Set[str] = frozenset(
        {
            "isotope_intensity_correlation",
            "isotope_height_correlation",
            "intensity_correlation",
            "height_correlation",
            "fragment_scan_correlation",
            "template_scan_correlation",
            "fragment_frame_correlation",
            "top3_frame_correlation",
            "template_frame_correlation",
            "top3_b_ion_correlation",
            "top3_y_ion_correlation",
        }
    )

    # Ion statistics
    ION_STATS: Set[str] = frozenset(
        {
            "sum_b_ion_intensity",
            "sum_y_ion_intensity",
            "diff_b_y_ion_intensity",
            "n_b_ions",
            "n_y_ions",
        }
    )

    # Mobility features
    MOBILITY: Set[str] = frozenset(
        {
            "mobility_observed",
            "mobility_library",
            "mobility_fwhm",
        }
    )

    # Metadata and identifiers
    METADATA: Set[str] = frozenset(
        {
            "proteins",
            "genes",
            "sequence",
            "mod_sites",
            "mods",
            "channel",
            "run",
            "mod_seq_hash",
            "mod_seq_charge_hash",
            "pg_master",
            "pg",
        }
    )

    # Sequence properties
    SEQUENCE_PROPS: Set[str] = frozenset(
        {
            "n_K",
            "n_R",
            "n_P",
            "charge",
        }
    )

    # Quality metrics
    QUALITY: Set[str] = frozenset(
        {
            "score",
            "proba",
            "qval",
            "pg_qval",
            "valid",
            "decoy",
        }
    )


class FeatureType(Enum):
    """Enumeration of feature data types"""

    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    IDENTIFIER = "identifier"
    BOOLEAN = "boolean"


@dataclass(frozen=True)
class FeatureMetadata:
    """Metadata for each feature"""

    name: str
    type: FeatureType
    description: str = ""
    units: str = ""
    group: str = ""


class MSFeatures:
    """Main class for managing MS feature definitions and metadata"""

    def __init__(self):
        self.groups = FeatureGroups()

    #     self._initialize_feature_metadata()

    # def _initialize_feature_metadata(self):
    #     """Initialize metadata for all features"""
    #     self.metadata: Dict[str, FeatureMetadata] = {
    #         'rt_observed': FeatureMetadata(
    #             name='rt_observed',
    #             type=FeatureType.NUMERIC,
    #             description='Observed retention time',
    #             units='minutes',
    #             group='CHROMATOGRAPHIC'
    #         ),
    #         'mobility_observed': FeatureMetadata(
    #             name='mobility_observed',
    #             type=FeatureType.NUMERIC,
    #             description='Observed ion mobility',
    #             units='Vs/cm²',
    #             group='MOBILITY'
    #         ),
    #         # Add more feature metadata as needed
    #     }

    @property
    def all_features(self) -> Set[str]:
        """Get all feature names across all groups"""
        return {
            k: v
            for k, v in FeatureGroups.__dict__.items()
            if not k.startswith("__") and not callable(v)
        }

    def get_features_by_group(self, group: str) -> Set[str]:
        """Get features for a specific group"""
        return getattr(self.groups, group)

    @property
    def all_groups(self) -> Set[str]:
        """Get all feature group names"""
        return {
            k
            for k in FeatureGroups.__dict__.keys()
            if not k.startswith("__") and not callable(FeatureGroups.__dict__[k])
        }


# Configuration for feature selection and processing
class FeatureConfig:
    """Configuration settings for feature processing"""

    DEFAULT_FEATURES = [
        "intensity",
        "delta_rt",
    ]

    NORMALIZATION_FEATURES = ["intensity", "mono_ms1_intensity", "sum_ms1_intensity"]

    SCALING_FEATURES = ["rt_observed", "mobility_observed", "mass_error"]
