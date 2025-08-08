from __future__ import annotations

import os

import numpy as np
import pandas as pd
import polars as pl

# Remove StudyParameters import as we'll use hardcoded values for seed


def get_chrom(self, uids=None, samples=None):
    # Check if consensus_df is empty or doesn't have required columns
    if self.consensus_df.is_empty() or "consensus_uid" not in self.consensus_df.columns:
        self.logger.error("No consensus data found. Please run find_consensus() first.")
        return None

    ids = self._get_consensus_uids(uids)
    sample_uids = self._get_sample_uids(samples)

    if self.consensus_map is None:
        self.logger.error("No consensus map found.")
        return None

    # Pre-filter all DataFrames to reduce join sizes
    filtered_consensus_mapping = self.consensus_mapping_df.filter(
        pl.col("consensus_uid").is_in(ids),
    )

    # Get feature_uids that we actually need
    relevant_feature_uids = filtered_consensus_mapping["feature_uid"].to_list()

    self.logger.debug(
        f"Filtering features_df for {len(relevant_feature_uids)} relevant feature_uids.",
    )
    # Pre-filter features_df to only relevant features and samples
    filtered_features = self.features_df.filter(
        pl.col("feature_uid").is_in(relevant_feature_uids)
        & pl.col("sample_uid").is_in(sample_uids),
    ).select([
        "feature_uid",
        "chrom",
        "rt",
        "rt_original",
        "sample_uid",
    ])

    # Pre-filter samples_df
    filtered_samples = self.samples_df.filter(
        pl.col("sample_uid").is_in(sample_uids),
    ).select(["sample_uid", "sample_name"])

    # Perform a three-way join to get all needed data
    self.logger.debug("Joining DataFrames to get complete chromatogram data.")
    df_combined = (
        filtered_consensus_mapping.join(
            filtered_features,
            on="feature_uid",
            how="inner",
        )
        .join(filtered_samples, on="sample_uid", how="inner")
        .with_columns(
            (pl.col("rt") - pl.col("rt_original")).alias("rt_shift"),
        )
    )

    # Update chrom objects with rt_shift efficiently
    self.logger.debug("Updating chromatogram objects with rt_shift values.")
    chrom_data = df_combined.select(["chrom", "rt_shift"]).to_dict(as_series=False)
    for chrom_obj, rt_shift in zip(chrom_data["chrom"], chrom_data["rt_shift"]):
        if chrom_obj is not None:
            chrom_obj.rt_shift = rt_shift

    # Get all unique combinations for complete matrix
    all_consensus_uids = sorted(df_combined["consensus_uid"].unique().to_list())
    all_sample_names = sorted(df_combined["sample_name"].unique().to_list())

    # Create a mapping dictionary for O(1) lookup instead of O(n) filtering
    self.logger.debug("Creating lookup dictionary for chromatogram objects.")
    chrom_lookup = {}
    for row in df_combined.select([
        "consensus_uid",
        "sample_name",
        "chrom",
    ]).iter_rows():
        key = (row[0], row[1])  # (consensus_uid, sample_name)
        chrom_lookup[key] = row[2]  # chrom object

    # Build pivot data efficiently using the lookup dictionary
    pivot_data = []
    total_iterations = len(all_consensus_uids)
    progress_interval = max(1, total_iterations // 10)  # Show progress every 10%

    for i, consensus_uid in enumerate(all_consensus_uids):
        if i % progress_interval == 0:
            progress_percent = (i / total_iterations) * 100
            self.logger.debug(
                f"Building pivot data: {progress_percent:.0f}% complete ({i}/{total_iterations})",
            )

        row_data = {"consensus_uid": consensus_uid}
        for sample_name in all_sample_names:
            key = (consensus_uid, sample_name)
            row_data[sample_name] = chrom_lookup.get(key, None)
        pivot_data.append(row_data)

    self.logger.debug(
        f"Building pivot data: 100% complete ({total_iterations}/{total_iterations})",
    )

    # Create Polars DataFrame with complex objects
    df2_pivoted = pl.DataFrame(pivot_data)

    # Return as Polars DataFrame (can handle complex objects like Chromatogram)
    return df2_pivoted

def set_default_folder(self, folder):
    """
    Set the default folder for saving and loading files.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    self.default_folder = folder


def align_reset(self):
    if self.alignment_ref_index is None:
        return
    self.logger.debug("Resetting alignment.")
    # iterate over all feature maps and set RT to original RT
    for feature_map in self.features_maps:
        for feature in feature_map:
            rt = feature.getMetaValue("original_RT")
            if rt is not None:
                feature.setRT(rt)
                feature.removeMetaValue("original_RT")
    self.alignment_ref_index = None


# TODO I don't get this param
def get_consensus(self, quant="chrom_area"):
    if self.consensus_df is None:
        self.logger.error("No consensus map found.")
        return None

    # Convert Polars DataFrame to pandas for this operation since the result is used for export
    df1 = self.consensus_df.to_pandas().copy()

    # set consensus_id as uint64
    df1["consensus_id"] = df1["consensus_id"].astype("uint64")
    # set consensus_id as index
    df1.set_index("consensus_uid", inplace=True)
    # sort by consensus_id
    df1 = df1.sort_index()

    df2 = self.get_consensus_matrix(quant=quant)
    # sort df2 row by consensus_id
    df2 = df2.sort_index()
    # merge df and df2 on consensus_id
    df = pd.merge(df1, df2, left_index=True, right_index=True, how="left")

    return df


# TODO I don't get this param
def get_consensus_matrix(self, quant="chrom_area"):
    """
    Get a matrix of consensus features with samples as columns and consensus features as rows.
    """
    if quant not in self.features_df.columns:
        self.logger.error(
            f"Quantification method {quant} not found in features_df.",
        )
        return None

    # Use Polars join instead of pandas merge
    features_subset = self.features_df.select(["feature_uid", "sample_uid", quant])
    consensus_mapping_subset = self.consensus_mapping_df.select([
        "consensus_uid",
        "feature_uid",
    ])

    df1 = features_subset.join(
        consensus_mapping_subset,
        on="feature_uid",
        how="left",
    )

    # Convert to pandas for pivot operation (Polars pivot is still evolving)
    df1_pd = df1.to_pandas()
    df2 = df1_pd.pivot_table(
        index="consensus_uid",
        columns="sample_uid",
        values=quant,
        aggfunc="max",
    )

    # Create sample_uid to sample_name mapping using Polars
    sample_mapping = dict(
        self.samples_df.select(["sample_uid", "sample_name"]).iter_rows(),
    )
    # replace sample_uid with sample_name in df2
    df2 = df2.rename(columns=sample_mapping)

    # round to integer
    df2 = df2.round()
    # set consensus_id as uint64
    df2.index = df2.index.astype("uint64")
    # set index to consensus_id
    df2.index.name = "consensus_uid"
    return df2


def get_gaps_matrix(self, uids=None):
    """
    Get a matrix of gaps between consensus features with samples as columns and consensus features as rows.
    """
    if self.consensus_df is None:
        self.logger.error("No consensus map found.")
        return None
    uids = self._get_consensus_uids(uids)

    df1 = self.get_consensus_matrix(quant="filled")
    if df1 is None or df1.empty:
        self.logger.warning("No gap data found.")
        return None
    # keep only rows where consensus_id is in ids - use pandas indexing since df1 is already pandas
    df1 = df1[df1.index.isin(uids)]
    return df1


def get_gaps_stats(self, uids=None):
    """
    Get statistics about gaps in the consensus features.
    """

    df = self.get_gaps_matrix(uids=uids)

    # For each column, count how many times the value is True, False, or None. Summarize in a new df with three rows: True, False, None.
    if df is None or df.empty:
        self.logger.warning("No gap data found.")
        return None
    gaps_stats = pd.DataFrame(
        {
            "aligned": df.apply(lambda x: (~x.astype(bool)).sum()),
            "filled": df.apply(lambda x: x.astype(bool).sum() - pd.isnull(x).sum()),
            "missing": df.apply(lambda x: pd.isnull(x).sum()),
        },
    )
    return gaps_stats


# TODO is uid not supposed to be a list anymore?
def get_consensus_matches(self, uids=None):
    uids = self._get_consensus_uids(uids)

    # find all rows in consensus_mapping_df with consensus_id=id - use Polars filtering
    fid = (
        self.consensus_mapping_df.filter(
            pl.col("consensus_uid").is_in(uids),
        )
        .select("feature_uid")
        .to_series()
        .to_list()
    )
    # select all rows in features_df with uid in fid
    matches = self.features_df.filter(pl.col("feature_uid").is_in(fid)).clone()
    return matches


def fill_reset(self):
    # remove all features with filled=True
    if self.features_df is None:
        self.logger.warning("No features found.")
        return
    l1 = len(self.features_df)
    self.features_df = self.features_df.filter(~pl.col("filled"))
    # remove all rows in consensus_mapping_df where feature_uid is not in features_df['uid']

    feature_uids_to_keep = self.features_df["feature_uid"].to_list()
    self.consensus_mapping_df = self.consensus_mapping_df.filter(
        pl.col("feature_uid").is_in(feature_uids_to_keep),
    )
    self.logger.info(
        f"Reset filled chromatograms. Chroms removed: {l1 - len(self.features_df)}",
    )


def _get_feature_uids(self, uids=None, seed=42):
    """
    Helper function to get feature_uids from features_df based on input uids.
    If uids is None, returns all feature_uids.
    If uids is a single integer, returns a random sample of feature_uids.
    If uids is a list of strings, returns feature_uids corresponding to those feature_uids.
    If uids is a list of integers, returns feature_uids corresponding to those feature_uids.
    """
    if uids is None:
        # get all feature_uids from features_df
        return self.features_df["feature_uid"].to_list()
    elif isinstance(uids, int):
        # choose a random sample of feature_uids
        if len(self.features_df) > uids:
            np.random.seed(seed)
            return np.random.choice(
                self.features_df["feature_uid"].to_list(),
                uids,
                replace=False,
            ).tolist()
        else:
            return self.features_df["feature_uid"].to_list()
    else:
        # iterate over all uids. If the item is a string, assume it's a feature_uid
        feature_uids = []
        for uid in uids:
            if isinstance(uid, str):
                matching_rows = self.features_df.filter(pl.col("feature_uid") == uid)
                if not matching_rows.is_empty():
                    feature_uids.append(
                        matching_rows.row(0, named=True)["feature_uid"],
                    )
            elif isinstance(uid, int):
                if uid in self.features_df["feature_uid"].to_list():
                    feature_uids.append(uid)
        # remove duplicates
        feature_uids = list(set(feature_uids))
        return feature_uids


def _get_consensus_uids(self, uids=None, seed=42):
    """
    Helper function to get consensus_uids from consensus_df based on input uids.
    If uids is None, returns all consensus_uids.
    If uids is a single integer, returns a random sample of consensus_uids.
    If uids is a list of strings, returns consensus_uids corresponding to those consensus_ids.
    If uids is a list of integers, returns consensus_uids corresponding to those consensus_uids.
    """
    # Check if consensus_df is empty or doesn't have required columns
    if self.consensus_df.is_empty() or "consensus_uid" not in self.consensus_df.columns:
        return []

    if uids is None:
        # get all consensus_uids from consensus_df
        return self.consensus_df["consensus_uid"].to_list()
    elif isinstance(uids, int):
        # choose a random sample of consensus_uids
        if len(self.consensus_df) > uids:
            np.random.seed(seed)  # for reproducibility
            return np.random.choice(
                self.consensus_df["consensus_uid"].to_list(),
                uids,
                replace=False,
            ).tolist()
        else:
            return self.consensus_df["consensus_uid"].to_list()
    else:
        # iterate over all uids. If the item is a string, assume it's a consensus_id
        consensus_uids = []
        for uid in uids:
            if isinstance(uid, str):
                matching_rows = self.consensus_df.filter(pl.col("consensus_id") == uid)
                if not matching_rows.is_empty():
                    consensus_uids.append(
                        matching_rows.row(0, named=True)["consensus_uid"],
                    )
            elif isinstance(uid, int):
                if uid in self.consensus_df["consensus_uid"].to_list():
                    consensus_uids.append(uid)
        # remove duplicates
        consensus_uids = list(set(consensus_uids))
        return consensus_uids


def _get_sample_uids(self, samples=None, seed=42):
    """
    Helper function to get sample_uids from samples_df based on input samples.
    If samples is None, returns all sample_uids.
    If samples is a single integer, returns a random sample of sample_uids.
    If samples is a list of strings, returns sample_uids corresponding to those sample_names.
    If samples is a list of integers, returns sample_uids corresponding to those sample_uids.
    """
    if samples is None:
        # get all sample_uids from samples_df
        return self.samples_df["sample_uid"].to_list()
    elif isinstance(samples, int):
        # choose a random sample of sample_uids
        if len(self.samples_df) > samples:
            np.random.seed(seed)  # for reproducibility
            return np.random.choice(
                self.samples_df["sample_uid"].to_list(),
                samples,
                replace=False,
            ).tolist()
        else:
            return self.samples_df["sample_uid"].to_list()
    else:
        # iterate over all samples. If the item is a string, assume it's a sample_name
        sample_uids = []
        for sample in samples:
            if isinstance(sample, str):
                matching_rows = self.samples_df.filter(pl.col("sample_name") == sample)
                if not matching_rows.is_empty():
                    sample_uids.append(
                        matching_rows.row(0, named=True)["sample_uid"],
                    )
            elif isinstance(sample, int):
                if sample in self.samples_df["sample_uid"].to_list():
                    sample_uids.append(sample)
        # remove duplicates
        sample_uids = list(set(sample_uids))
        return sample_uids

def get_orphans(self):
    """ 
    Get all features that are not in the consensus mapping.
    """
    not_in_consensus = self.features_df.filter(~self.features_df['feature_uid'].is_in(self.consensus_mapping_df['feature_uid'].to_list()))
    return not_in_consensus

def compress(self):
    """
    Compress the study data.
    """
    self.logger.info("Compressing study data...")
    # self.features_maps = []
    # drop all features that are not in consensus_mapping_df
    if self.features_df is not None and not self.features_df.is_empty():
        l1 = len(self.features_df)
        self.features_df = self.features_df.filter(
            pl.col("feature_uid").is_in(
                self.consensus_mapping_df["feature_uid"].to_list(),
            ),
        )
    self.logger.info(f"Removed {l1 - len(self.features_df)} features.")
