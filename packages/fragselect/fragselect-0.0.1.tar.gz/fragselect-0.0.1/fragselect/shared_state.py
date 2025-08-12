class SharedState:
    """Container for state shared between multiple classes"""

    def __init__(self):
        self.level_information = None
        self.sorted_columns = None
        self.lin_scaled_data = None
        self.ms2_identifiers = None
        self.ms1_identifiers = None
        self.extracted_ms2_identifiers = None
        self.extracted_ms1_identifiers = None
        self.level = None


# Create a single instance to be imported by other modules
shared_state = SharedState()
