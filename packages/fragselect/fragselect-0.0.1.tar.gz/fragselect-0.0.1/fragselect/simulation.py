import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from fragselect.featureengineering import FeatureEngineering
import torch


class Simulation:
    def __init__(
        self,
        n_fragments=None,
        n_runs=None,
        percent_similar=None,
        percent_systematic_error=None,
        base_pattern=None,
        base_pattern_length=None,
    ):
        self.n_fragments = n_fragments
        self.n_runs = n_runs
        self.percent_similar = percent_similar
        self.percent_systematic_error = percent_systematic_error
        self.base_pattern = base_pattern

        # create FeatureEngineering
        self.feature_engineering = FeatureEngineering()

        if base_pattern is not None:
            self.base_pattern_length = len(base_pattern)
        else:
            self.base_pattern_length = base_pattern_length

    def create_3d_simulation(self, num_of_acqu, min, max, num_of_prot, mean_dist=False):
        # simulate ion trace data
        self.simulate_ion_trace_dataset(num_of_acqu, min, max, num_of_prot)

        # simulate ms accuracy
        self.simulate_ms_accuracy()

        if mean_dist:
            # feature engineering
            mean_distances = self.feature_engineering._calculate_mean_distances(
                self.data
            )

            data = [
                np.stack((traces, ms_accuracies, mean_distances), axis=2)
                for traces, ms_accuracies, mean_distances in zip(
                    self.data, self.ms_acccuracies, mean_distances
                )
            ]

            data = self._change_dtypes(data)

            return data

        else:
            data = [
                np.stack((traces, ms_accuracies), axis=2)
                for traces, ms_accuracies in zip(self.data, self.ms_acccuracies)
            ]

            data = self._change_dtypes(data)

            return data

    def _change_dtypes(self, data):
        return [torch.tensor(dataset).float() for dataset in data]

    def simulate_ion_trace_dataset(self, num_of_acqu, min, max, num_of_prot):
        self.data = []
        self.sim_indices = []
        self.systematic_indices = []
        self.sim_percent = []
        self.y_true = np.zeros((num_of_prot, num_of_acqu))
        self.num_of_acqu = num_of_acqu

        for i, percent in enumerate(np.linspace(min, max, num_of_prot)):
            self.percent_similar = percent
            self.create_two_sample_base_pattern(n_runs=num_of_acqu)

            # simulate data
            ion_traces = self.simulate()
            ion_traces += np.abs(ion_traces.min()) + 1e-8

            # collect the data
            self.data.append(ion_traces)
            self.sim_indices.append(
                int(self.n_fragments * (self.percent_similar / 100))
            )
            self.systematic_indices.append(
                int(self.n_fragments * (self.percent_systematic_error / 100))
            )
            self.sim_percent.append(self.percent_similar)

            # calculate y_true
            self.y_true[i] = np.nanmean(ion_traces[: self.sim_indices[i]], axis=0)

    def simulate(self):
        # Generating the ion trace data
        ion_traces = np.zeros((self.n_fragments, self.n_runs))

        for i in range(self.n_fragments):
            if i < self.n_fragments * self.percent_similar / 100:
                ion_traces[i] = self.generate_similar_trace()
            elif (
                i
                < self.n_fragments
                * (self.percent_similar + self.percent_systematic_error)
                / 100
            ):
                ion_traces[i] = self.generate_systematic_error_trace()
            else:
                ion_traces[i] = self.generate_random_error_trace()
        return ion_traces

    # Function to generate a similar shape trace
    def generate_similar_trace(self, random_pattern=False):
        if self.base_pattern is None or random_pattern:
            self.base_pattern = self.random_pattern()

        trace = np.tile(self.base_pattern, self.n_runs // self.base_pattern_length + 1)
        trace = trace[: self.n_runs]  # trim to the length of runs
        trace += np.random.normal(0, 1, size=trace.shape)  # adding small noise
        return trace

    def random_pattern(self):
        return np.random.uniform(-10, 10, self.n_runs)

    # Function to generate a trace with systematic error
    def generate_systematic_error_trace(self):
        trace = self.generate_similar_trace()
        # error_index = np.random.randint(0, self.n_runs)
        # error_indices = np.random.choice(self.n_runs, replace=True)
        trace += np.random.uniform(-10, 10)  # adding a systematic error
        return trace

    # Function to generate a trace with random error
    def generate_random_error_trace(self):
        trace = self.generate_similar_trace(random_pattern=True)

        # add random errors
        error_indices = np.random.choice(self.n_runs, replace=True)
        trace[:error_indices] += np.random.uniform(
            -5, 5, size=error_indices
        )  # adding random errors

        # add random errors
        trace += np.random.uniform(-5, 5)

        return trace

    def create_two_sample_base_pattern(
        self,
        n_fragments_range=(50, 100),
        n_runs=36,
        sample_a_mean=(2, 10),
        sample_b_mean=(2, 10),
        sample_a_std=(5, 0.5),
        sample_b_std=(3, 3),
    ):
        # Number of fragments and runs
        n_fragments = np.random.randint(n_fragments_range[0], n_fragments_range[1])

        # Percentage distributions
        percent_systematic_error = np.random.uniform(25, 30)

        # Generating base trace pattern (up, down, up, down, up, up ...)
        sample_a_mean = np.random.normal(sample_a_mean[0], sample_a_mean[1])
        sample_b_mean = np.random.normal(
            sample_b_mean[0], sample_b_mean[1]
        ) + np.random.uniform(-4, 4)

        sample_a_std = np.abs(np.random.normal(sample_a_std[0], sample_a_std[1]))
        sample_b_std = np.abs(np.random.normal(sample_b_std[0], sample_b_std[1]))

        sample_a_reps = np.random.randint(5, n_runs)
        sample_b_reps = n_runs - sample_a_reps

        sample_a = np.random.normal(sample_a_mean, sample_a_std, sample_a_reps)
        sample_b = np.random.normal(sample_b_mean, sample_b_std, sample_b_reps)

        base_pattern = np.concatenate([sample_a, sample_b])

        self.n_fragments = n_fragments
        self.n_runs = n_runs
        self.percent_systematic_error = percent_systematic_error
        self.base_pattern = base_pattern
        self.base_pattern_length = len(base_pattern)

    def simulate_ms_accuracy(self):
        self.ms_acccuracies = []
        for trace, sim_perc in zip(self.data, self.sim_indices):
            # simulate ms accuracy scores correctly
            ms_accuracy = np.ones(trace.shape)
            ms_accuracy[:sim_perc] = 1
            ms_accuracy[sim_perc:] = 0

            # simulate faulty ms accuracy scores
            high_to_low = True
            ms_accuracy = self.assign_faulty_ms_accuracy(
                ms_accuracy, high_to_low, sim_perc, trace
            )

            # simulate faulty ms accuracy scores
            high_to_low = False
            ms_accuracy = self.assign_faulty_ms_accuracy(
                ms_accuracy, high_to_low, sim_perc, trace
            )

            ms_accuracy -= np.random.normal(0, 0.1, trace.shape)

            # standardise and stack
            ms_accuracy = MinMaxScaler().fit_transform(ms_accuracy)

            self.ms_acccuracies.append(ms_accuracy)

    def assign_faulty_ms_accuracy(self, ms_accuracy, high_to_low, sim_perc, trace):
        if high_to_low == True:
            # assign fault ms accuracy scores
            percent_incorrect_accuracy_within_protein = np.random.uniform(0.10, 0.15)
            number_of_incorrect_accuracy_within_protein = int(
                percent_incorrect_accuracy_within_protein * len(trace)
            )
            number_of_incorrect_accuracy_indices_within_protein = np.random.choice(
                sim_perc, number_of_incorrect_accuracy_within_protein, replace=False
            )

            for i in number_of_incorrect_accuracy_indices_within_protein:
                num_of_incorrect_accuracy_within_trace = int(
                    self.num_of_acqu * (np.random.uniform(0.10, 0.15))
                )
                numbers_of_incorrect_labels = np.random.choice(
                    self.num_of_acqu,
                    num_of_incorrect_accuracy_within_trace,
                    replace=False,
                )
                ms_accuracy[i, numbers_of_incorrect_labels] = 0

        else:
            # assign fault ms accuracy scores
            percent_incorrect_accuracy_within_protein = np.random.uniform(0.10, 0.15)
            number_of_incorrect_accuracy_within_protein = int(
                percent_incorrect_accuracy_within_protein * len(trace)
            )
            number_of_incorrect_accuracy_indices_within_protein = np.random.choice(
                range(sim_perc, len(ms_accuracy)),
                number_of_incorrect_accuracy_within_protein,
                replace=False,
            )

            for i in number_of_incorrect_accuracy_indices_within_protein:
                num_of_incorrect_accuracy_within_trace = int(
                    self.num_of_acqu * (np.random.uniform(0.10, 0.15))
                )
                numbers_of_incorrect_labels = np.random.choice(
                    self.num_of_acqu,
                    num_of_incorrect_accuracy_within_trace,
                    replace=False,
                )
                ms_accuracy[i, numbers_of_incorrect_labels] = 1

        return ms_accuracy

    def simulate_missing_values(self, data, num_of_prot):
        for protein in range(num_of_prot):
            row, col = data[protein].shape[:2]
            num_of_missing_vals = int(row * col * np.random.uniform(0.05, 0.1, 1)[0])
            unique_combos = np.array(
                np.meshgrid([np.arange(row)], [np.arange(col)])
            ).T.reshape(-1, 2)

            indices = np.random.choice(
                len(unique_combos), num_of_missing_vals, replace=False
            )
            rows_cols = unique_combos[indices]
            rows = rows_cols[:, 0]
            cols = rows_cols[:, 1]

            data[protein][rows, cols, :] = torch.nan

        return data

    def plot_simulated_traces(self, ion_trace):
        for idx, trace in enumerate(ion_trace):
            if idx < self.n_fragments * self.percent_similar / 100:
                sns.pointplot(trace, color="green", linewidth=1, label="similar")
            elif (
                idx
                < self.n_fragments
                * (self.percent_similar + self.percent_systematic_error)
                / 100
            ):
                sns.pointplot(
                    trace,
                    color="blue",
                    alpha=0.2,
                    linewidth=1,
                    label="systematic error",
                )
            else:
                sns.pointplot(
                    trace, color="red", alpha=0.2, linewidth=1, label="random error"
                )
            # Create a custom legend
            custom_lines = [
                Line2D([0], [0], color="green", lw=2),
                Line2D([0], [0], color="blue", lw=2),
                Line2D([0], [0], color="red", lw=2),
            ]
            plt.legend(custom_lines, ["similar", "systematic error", "random error"])

            plt.title("Simulated Ion Trace Data")
            plt.xlabel("Run")
            plt.ylabel("Fragment Intensity")
