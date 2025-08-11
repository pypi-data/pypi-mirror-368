import os
import glob
import inspect
import pandas as pd

from typing import Dict
from functools import wraps
from rich.pretty import pprint

from abc import ABC, abstractmethod

from ..filetype import csvfile
from ..common import now_str
from ..research.perftb import PerfTB
from collections import OrderedDict

# try to import torch, and torchmetrics
try:
    import torch
    import torchmetrics
    from torchmetrics import Metric
except ImportError:
    raise ImportError("Please install torch and torchmetrics to use this module.")

def validate_torch_metrics(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        result = fn(self, *args, **kwargs)

        if not isinstance(result, dict):
            raise TypeError("torch_metrics() must return a dictionary")

        for k, v in result.items():
            if not isinstance(k, str):
                raise TypeError(f"Key '{k}' is not a string")
            if not isinstance(v, Metric):
                raise TypeError(
                    f"Value for key '{k}' is not a torchmetrics.Metric (got {type(v).__name__})"
                )

        return result

    return wrapper
def valid_custom_fields(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        rs = fn(self, *args, **kwargs)
        if not isinstance(rs, tuple) or len(rs) != 2:
            raise ValueError("Function must return a tuple (outdict, custom_fields)")
        outdict, custom_fields = rs
        if not isinstance(outdict, dict):
            raise TypeError("Output must be a dictionary")
        if not isinstance(custom_fields, list):
            raise TypeError("Custom fields must be a list")
        for field in custom_fields:
            if not isinstance(field, str):
                raise TypeError(f"Custom field '{field}' is not a string")
        return outdict, custom_fields

    return wrapper

REQUIRED_COLS = ["experiment", "dataset"]
CSV_FILE_POSTFIX = "__perf"

class PerfCalc(ABC): # Abstract base class for performance calculation

    @abstractmethod
    def get_experiment_name(self):
        """
        Return the name of the experiment.
        This function should be overridden by the subclass if needed.
        """
        pass

    @abstractmethod
    def get_dataset_name(self):
        """
        Return the name of the dataset.
        This function should be overridden by the subclass if needed.
        """
        pass

    @abstractmethod
    def get_metrics_info(self):
        """
        Return a list of metric names to be used for performance calculation OR a dictionaray with keys as metric names and values as metric instances of torchmetrics.Metric. For example: {"accuracy": Accuracy(), "precision": Precision()}

        """
        pass

    def calc_exp_outdict_custom_fields(self, outdict, *args, **kwargs):
        """Can be overridden by the subclass to add custom fields to the output dictionary.
        ! must return the modified outdict, and a ordered list of custom fields to be added to the output dictionary.
        """
        return outdict, []

    # ! can be override, but ONLY if torchmetrics are used
    # Prepare the exp data for torch metrics.
    def prepare_torch_metrics_exp_data(self, metric_names, *args, **kwargs):
        """
        Prepare the data for metrics.
        This function should be overridden by the subclass if needed.
        Must return a dictionary with keys as metric names and values as the data to be used for those metrics.
        NOTE: that the data (for each metric) must be in the format expected by the torchmetrics instance (for that metric). E.g: {"accuracy": {"preds": [...], "target": [...]}, ...} since torchmetrics expects the data in a specific format.
        """
        pass

    def __validate_metrics_info(self, metrics_info):
        """
        Validate the metrics_info to ensure it is a list or a dictionary with valid metric names and instances.
        """
        if not isinstance(metrics_info, (list, dict)):
            raise TypeError(f"Metrics info must be a list or a dictionary, got {type(metrics_info).__name__}")

        if isinstance(metrics_info, dict):
            for k, v in metrics_info.items():
                if not isinstance(k, str):
                    raise TypeError(f"Key '{k}' is not a string")
                if not isinstance(v, Metric):
                    raise TypeError(f"Value for key '{k}' is not a torchmetrics.Metric (got {type(v).__name__})")
        elif isinstance(metrics_info, list):
            for metric in metrics_info:
                if not isinstance(metric, str):
                    raise TypeError(f"Metric '{metric}' is not a string")
        return metrics_info
    def __calc_exp_perf_metrics(self, *args, **kwargs):
        """
        Calculate the performance metrics for the experiment.
        """
        metrics_info = self.__validate_metrics_info(self.get_metrics_info())
        USED_TORCHMETRICS = isinstance(metrics_info, dict)
        metric_names = metrics_info if isinstance(metrics_info, list) else list(metrics_info.keys())
        out_dict = {metric: None for metric in metric_names}
        out_dict["dataset"] = self.get_dataset_name()
        out_dict["experiment"] = self.get_experiment_name()
        out_dict, custom_fields = self.calc_exp_outdict_custom_fields(
            outdict=out_dict, *args, **kwargs
        )
        if USED_TORCHMETRICS:
            torch_metrics_dict = self.get_metrics_info()
            all_metric_data = self.prepare_torch_metrics_exp_data(
                metric_names, *args, **kwargs
            )
            metric_col_names = []
            for metric in metric_names:
                if metric not in all_metric_data:
                    raise ValueError(f"Metric '{metric}' not found in provided data.")
                tmetric = torch_metrics_dict[metric]  # torchmetrics instance
                metric_data = all_metric_data[metric]  # should be a dict of args/kwargs
                # Inspect expected parameters for the metric's update() method
                sig = inspect.signature(tmetric.update)
                expected_args = list(sig.parameters.values())
                # Prepare args in correct order
                if isinstance(metric_data, dict):
                    # Match dict keys to parameter names
                    args = [metric_data[param.name] for param in expected_args]
                elif isinstance(metric_data, (list, tuple)):
                    args = metric_data
                else:
                    raise TypeError(f"Unsupported data format for metric '{metric}'")

                # Call update and compute
                if len(expected_args) == 1:
                    tmetric.update(args)  # pass as single argument
                else:
                    tmetric.update(*args)  # unpack multiple arguments
                computed_value = tmetric.compute()
                # ensure the computed value converted to a scala value or list array
                if isinstance(computed_value, torch.Tensor):
                    if computed_value.numel() == 1:
                        computed_value = computed_value.item()
                    else:
                        computed_value = computed_value.tolist()
                col_name = f"metric_{metric}" if "metric_" not in metric else metric
                metric_col_names.append(col_name)
                out_dict[col_name] = computed_value
        else:
            # If torchmetrics are not used, calculate metrics using the custom method
            metric_rs_dict = self.calc_exp_perf_metrics(
                metric_names, *args, **kwargs)
            for metric in metric_names:
                if metric not in metric_rs_dict:
                    raise ValueError(f"Metric '{metric}' not found in provided data.")
                col_name = f"metric_{metric}" if "metric_" not in metric else metric
                out_dict[col_name] = metric_rs_dict[metric]
            metric_col_names = [f"metric_{metric}" for metric in metric_names]
        ordered_cols = REQUIRED_COLS + custom_fields + metric_col_names
        # create a new ordered dictionary with the correct order
        out_dict = OrderedDict((col, out_dict[col]) for col in ordered_cols if col in out_dict)
        return out_dict

    # ! only need to override this method if torchmetrics are not used
    def calc_exp_perf_metrics(self, metric_names, *args, **kwargs):
        """
        Calculate the performance metrics for the experiment, but not using torchmetrics.
        This function should be overridden by the subclass if needed.
        Must return a dictionary with keys as metric names and values as the calculated metrics.
        """
        raise NotImplementedError("calc_exp_perf_metrics() must be overridden by the subclass if torchmetrics are not used.")


    #! custom kwargs:
    #! outfile - if provided, will save the output to a CSV file with the given path
    #! outdir - if provided, will save the output to a CSV file in the given directory with a generated filename
    #! return_df - if True, will return a DataFrame instead of a dictionary

    def calc_save_exp_perfs(self, *args, **kwargs):
        """
        Calculate the metrics.
        This function should be overridden by the subclass if needed.
        Must return a dictionary with keys as metric names and values as the calculated metrics.
        """
        out_dict = self.__calc_exp_perf_metrics(*args, **kwargs)
        # pprint(f"Output Dictionary: {out_dict}")
        # check if any kwargs named "outfile"
        csv_outfile = kwargs.get("outfile", None)
        if csv_outfile is not None:
            filePathNoExt, _ = os.path.splitext(csv_outfile)
            # pprint(f"CSV Outfile Path (No Ext): {filePathNoExt}")
            csv_outfile = f'{filePathNoExt}{CSV_FILE_POSTFIX}.csv'
        elif "outdir" in kwargs:
            csvoutdir = kwargs["outdir"]
            csvfilename = f"{now_str()}_{self.get_dataset_name()}_{self.get_experiment_name()}_{CSV_FILE_POSTFIX}.csv"
            csv_outfile = os.path.join(csvoutdir, csvfilename)

        # convert out_dict to a DataFrame
        df = pd.DataFrame([out_dict])
        # get the orders of the columns as the orders or the keys in out_dict
        ordered_cols = list(out_dict.keys())
        df = df[ordered_cols]  # reorder columns

        if csv_outfile:
            df.to_csv(csv_outfile, index=False, sep=";", encoding="utf-8")
        return_df = kwargs.get("return_df", False)
        if return_df: # return DataFrame instead of dict if requested
            return df, csv_outfile
        else:
            return out_dict, csv_outfile

    @staticmethod
    def default_exp_csv_filter_fn(exp_file_name: str) -> bool:
        """
        Default filter function for experiments.
        Returns True if the experiment name does not start with "test_" or "debug_".
        """
        return "__perf.csv" in exp_file_name

    @classmethod
    def gen_perf_report_for_multip_exps(
        cls, indir: str, exp_csv_filter_fn=default_exp_csv_filter_fn, csv_sep=";"
    ) -> PerfTB:
        """
        Generate a performance report by scanning experiment subdirectories.
        Must return a dictionary with keys as metric names and values as performance tables.
        """
        def get_df_for_all_exp_perf(csv_perf_files, csv_sep=';'):
            """
            Create a single DataFrame from all CSV files.
            Assumes all CSV files MAY have different metrics
            """
            cols = []
            for csv_file in csv_perf_files:
                temp_df = pd.read_csv(csv_file, sep=csv_sep)
                temp_df_cols = temp_df.columns.tolist()
                for col in temp_df_cols:
                    if col not in cols:
                        cols.append(col)
            df = pd.DataFrame(columns=cols)
            for csv_file in csv_perf_files:
                temp_df = pd.read_csv(csv_file, sep=csv_sep)
                # Drop all-NA columns to avoid dtype inconsistency
                temp_df = temp_df.dropna(axis=1, how='all')
                # ensure all columns are present in the final DataFrame
                for col in cols:
                    if col not in temp_df.columns:
                        temp_df[col] = None  # fill missing columns with None
                df = pd.concat([df, temp_df], ignore_index=True)
            # assert that REQUIRED_COLS are present in the DataFrame
            # pprint(df.columns.tolist())
            for col in REQUIRED_COLS:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' is missing from the DataFrame. REQUIRED_COLS = {REQUIRED_COLS}")
            metric_cols = [col for col in df.columns if col.startswith('metric_')]
            assert len(metric_cols) > 0, "No metric columns found in the DataFrame. Ensure that the CSV files contain metric columns starting with 'metric_'."
            final_cols = REQUIRED_COLS + metric_cols
            df = df[final_cols]
            # ! validate all rows in df before returning
            # make sure all rows will have at least values for REQUIRED_COLS and at least one metric column
            for index, row in df.iterrows():
                if not all(col in row and pd.notna(row[col]) for col in REQUIRED_COLS):
                    raise ValueError(f"Row {index} is missing required columns or has NaN values in required columns: {row}")
                if not any(pd.notna(row[col]) for col in metric_cols):
                    raise ValueError(f"Row {index} has no metric values: {row}")
            # make sure these is no (experiment, dataset) pair that is duplicated
            duplicates = df.duplicated(subset=['experiment', 'dataset'], keep=False)
            if duplicates.any():
                raise ValueError("Duplicate (experiment, dataset) pairs found in the DataFrame. Please ensure that each experiment-dataset combination is unique.")
            return df

        def mk_perftb_report(df):
            """
            Create a performance report table from the DataFrame.
            This function should be customized based on the specific requirements of the report.
            """
            perftb = PerfTB()
            # find all "dataset" values (unique)
            dataset_names = list(df['dataset'].unique())
            # find all columns that start with "metric_"
            metric_cols = [col for col in df.columns if col.startswith('metric_')]

            # Determine which metrics are associated with each dataset.
            # Since a dataset may appear in multiple rows and may not include all metrics in each, identify the row with the same dataset that contains the most non-NaN metric values. The set of metrics for that dataset is defined by the non-NaN metrics in that row.

            dataset_metrics = {}
            for dataset_name in dataset_names:
                dataset_rows = df[df["dataset"] == dataset_name]
                # Find the row with the most non-NaN metric values
                max_non_nan_row = dataset_rows[metric_cols].count(axis=1).idxmax()
                metrics_for_dataset = dataset_rows.loc[max_non_nan_row, metric_cols].dropna().index.tolist()
                dataset_metrics[dataset_name] = metrics_for_dataset

            for dataset_name, metrics in dataset_metrics.items():
                # Create a new row for the performance table
                perftb.add_dataset(dataset_name, metrics)

            for _, row in df.iterrows():
                dataset_name = row['dataset']
                ds_metrics = dataset_metrics.get(dataset_name)
                if dataset_name in dataset_metrics:
                    # Add the metrics for this row to the performance table
                    exp_name = row.get('experiment')
                    exp_metric_values = {}
                    for metric in ds_metrics:
                        if metric in row and pd.notna(row[metric]):
                            exp_metric_values[metric] = row[metric]
                    perftb.add_experiment(
                        experiment_name=exp_name,
                        dataset_name=dataset_name,
                        metrics=exp_metric_values
                    )

            return perftb

        assert os.path.exists(indir), f"Input directory {indir} does not exist."

        csv_perf_files = []
        # Find experiment subdirectories
        exp_dirs = [
            os.path.join(indir, d)
            for d in os.listdir(indir)
            if os.path.isdir(os.path.join(indir, d))
        ]
        if len(exp_dirs) == 0:
            csv_perf_files = glob.glob(
                os.path.join(indir, f"*.csv")
            )
            csv_perf_files = [
                file_item
                for file_item in csv_perf_files
                if exp_csv_filter_fn(file_item)
            ]
        else:
            # multiple experiment directories found
            # Collect all matching CSV files in those subdirs
            for exp_dir in exp_dirs:
                # pprint(f"Searching in experiment directory: {exp_dir}")
                matched = glob.glob(
                    os.path.join(exp_dir, f"*.csv")
                )
                matched = [
                    file_item
                    for file_item in matched
                    if exp_csv_filter_fn(file_item)
                ]
                csv_perf_files.extend(matched)

        assert (
            len(csv_perf_files) > 0
        ), f"No CSV files matching pattern '{exp_csv_filter_fn}' found in the experiment directories."

        assert len(csv_perf_files) > 0, f"No CSV files matching pattern '{exp_csv_filter_fn}' found in the experiment directories."

        all_exp_perf_df = get_df_for_all_exp_perf(csv_perf_files, csv_sep=csv_sep)
        csvfile.fn_display_df(all_exp_perf_df)
        perf_tb = mk_perftb_report(all_exp_perf_df)
        return perf_tb