from __future__ import annotations

import os

from datetime import datetime

import polars as pl
import pyopenms as oms

from tqdm import tqdm

from masster.sample.sample import Sample


def save(self, filename=None):
    """
    Save the study to an HDF5 file with proper serialization of complex objects.

    Args:
        study: The study object to save
        filename (str, optional): Target file name. If None, uses default.
    """

    if filename is None:
        # save to default file name in default_folder
        if self.default_folder is not None:
            filename = os.path.join(self.default_folder, "data.study5")
        else:
            self.logger.error("either filename or default_folder must be provided")
            return
    else:
        # check if filename includes any path
        if not os.path.isabs(filename):
            if self.default_folder is not None:
                filename = os.path.join(self.default_folder, filename)
            else:
                filename = os.path.join(os.getcwd(), filename)

    # if filename exists, append a timestamp to avoid overwriting
    #if os.path.exists(filename):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{filename.replace('.study5', '')}_{timestamp}.study5"

    self._save_study5(filename)

    if self.consensus_map is not None:
        # save the features as a separate file
        self._save_consensusXML(filename=filename.replace(".study5", ".consensusXML"))


def save_samples(self, samples=None):
    if samples is None:
        # get all sample_uids from samples_df
        samples = self.samples_df["sample_uid"].to_list()

    self.logger.info(f"Saving features for {len(samples)} samples...")

    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for sample_uid in tqdm(
        samples,
        total=len(samples),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Save samples",
        disable=tdqm_disable,
    ):
        # check if sample_uid is in samples_df
        if sample_uid not in self.samples_df.get_column("sample_uid").to_list():
            self.logger.warning(
                f"Sample with uid {sample_uid} not found in samples_df.",
            )
            continue
        # load the mzpkl file
        sample_row = self.samples_df.filter(pl.col("sample_uid") == sample_uid)
        if sample_row.is_empty():
            continue
        ddaobj = Sample(filename=sample_row.row(0, named=True)["sample_path"])
        if "rt_original" not in ddaobj.features_df.columns:
            # add column 'rt_original' with rt values
            ddaobj.features_df = ddaobj.features_df.with_columns(
                pl.col("rt").alias("rt_original"),
            )
        # find the rows in features_df that match the sample_uid
        matching_rows = self.features_df.filter(pl.col("sample_uid") == sample_uid)
        if not matching_rows.is_empty():
            # Update rt values in ddaobj.features_df based on matching_rows
            rt_values = matching_rows["rt"].to_list()
            if len(rt_values) == len(ddaobj.features_df):
                ddaobj.features_df = ddaobj.features_df.with_columns(
                    pl.lit(rt_values).alias("rt"),
                )
        # save ddaobj
        ddaobj.save()
        sample_name = sample_row.row(0, named=True)["sample_name"]
        # Find the index of this sample in the original order for features_maps
        sample_index = next(
            (
                i
                for i, row_dict in enumerate(self.samples_df.iter_rows(named=True))
                if row_dict["sample_uid"] == sample_uid
            ),
            None,
        )
        if self.default_folder is not None:
            filename = os.path.join(
                self.default_folder,
                sample_name + ".featureXML",
            )
        else:
            filename = os.path.join(
                os.getcwd(),
                sample_name + ".featureXML",
            )
        fh = oms.FeatureXMLFile()
        if sample_index is not None and sample_index < len(self.features_maps):
            fh.store(filename, self.features_maps[sample_index])

    self.logger.debug("All samples saved successfully.")


def _save_consensusXML(self, filename:str):
    if self.consensus_map is None:
        self.logger.error("No consensus map found.")
        return

    fh = oms.ConsensusXMLFile()
    fh.store(filename, self.consensus_map)
    self.logger.info(f"Saved consensus map to {filename}")


def save_consensus(self, **kwargs):
    """Save the consensus map to a file."""
    if self.consensus_map is None:
        self.logger.error("No consensus map found.")
        return
    self._save_consensusXML(**kwargs)
