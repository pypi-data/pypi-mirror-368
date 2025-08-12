class DataConfig:
    LOG2_TRANSFORM = True
    MS2_FEATURE_NAMES = [
        "intensity",
        "mass_error",
        "correlation",
        "height",
        # "charge",
        # "mz_observed",
        # "type",
        # "number",
    ]
    LOG2_TRANSFORM_FEATURES = [
        "ms2_intensity",
        "ms2_height",
        "ms1_intensity",
        "ms1_mean_overlapping_intensity",
    ]
    ALIGN_FEATURES = [
        "ms2_intensity",
        "ms2_height",
        "ms1_intensity",
        "ms1_mean_overlapping_intensity",
    ]


class ColumnConfig:
    PRECURSOR_ID = "precursor_idx"
    ION = "ion"

    PRECURSOR_FRAGMENT_IDENTIFIER = ["precursor_idx", "ion"]
    IDENTIFIERS = [
        "precursor_idx",
        "ion",
        "pg",
        "mod_seq_hash",
        "mod_seq_charge_hash",
    ]
    PRECURSOR_IDENTIFIERS = [
        "mod_seq_charge_hash",
        "pg",
        "precursor_idx",
    ]
