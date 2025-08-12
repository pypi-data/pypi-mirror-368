import directlfq.utils as lfq_utils
import directlfq.protein_intensity_estimation as lfqprot_estimation
import directlfq.config as config
import pandas as pd


class DirectlfqSimulation:
    def __init__(self):
        pass

    def get_directlfq_trace_per_protein(self, simulated_data):
        simulated_data_df = self.create_df_from_simulated_data(simulated_data)
        protein_df = self.estimate_directlfq_intensity_df(simulated_data_df)
        protein_df_shifted = self.shift_directlfq_traces_to_match_simulated_data(
            protein_df, simulated_data_df
        )
        return protein_df_shifted.values

    def create_df_from_simulated_data(self, simulated_data):
        flattened_simulated_data = []
        protein_names = []
        ion_names = []

        for i, array in enumerate(simulated_data):
            for j, row in enumerate(array):
                flattened_simulated_data.append(row)
                protein_names.append(f"protein_{i+1}")
                ion_names.append(f"ion_{j+1}")

        df_simulated_data = pd.DataFrame(flattened_simulated_data)
        df_simulated_data.insert(0, "protein", protein_names)
        df_simulated_data.insert(1, "ion", ion_names)
        return df_simulated_data

    def estimate_directlfq_intensity_df(self, input_df):
        config.set_global_protein_and_ion_id(protein_id="protein", quant_id="ion")
        input_df = lfq_utils.index_and_log_transform_input_df(input_df)
        input_df = lfq_utils.remove_allnan_rows_input_df(input_df)
        protein_df, ion_df = lfqprot_estimation.estimate_protein_intensities(
            input_df, min_nonan=1, num_samples_quadratic=10, num_cores=1
        )

        return protein_df

    def shift_directlfq_traces_to_match_simulated_data(
        self, protein_df, simulated_data_df
    ):
        simulated_data_df_ionmerge = (
            simulated_data_df.drop(columns="ion").groupby("protein").mean()
        )
        simulated_data_avg = simulated_data_df_ionmerge.mean(axis=0)
        protein_df_avg = protein_df.set_index("protein").mean(axis=0)
        protein_df_shifted = protein_df.set_index("protein") * (
            simulated_data_avg / protein_df_avg
        )
        return protein_df_shifted
