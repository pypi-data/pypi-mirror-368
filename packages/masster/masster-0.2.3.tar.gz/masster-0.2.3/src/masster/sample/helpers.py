from __future__ import annotations

import polars as pl

import numpy as np

# Parameters removed - using hardcoded defaults


def get_dda_stats(self):
    # filter self.scans_df with mslevel 1
    ms1 = self.scans_df.filter(pl.col("ms_level") == 1)
    return ms1


# TODO


def get_feature(self, feature_uid):
    # get the feature with feature_uid == feature_uid
    feature = self.features_df.filter(pl.col("feature_uid") == feature_uid)
    if len(feature) == 0:
        self.logger.warning(f"Feature {feature_uid} not found.")
        return None
    else:
        return feature.row(0, named=True)


def _get_scan_uids(self, scans=None, verbose=True):
    if scans is None:
        # fromuids scan all get_dfans
        scans_uids = self.scans_df.get_column("scan_uid").to_list()
    elif isinstance(scans, list):
        # if scans is a list, ensure all elements are valid scan_uids
        scans_uids = [
            s for s in scans if s in self.scans_df.get_column("scan_uid").to_list()
        ]
        if verbose and not scans_uids:
            self.logger.error("No valid scan_uids provided.")

    return scans_uids


def _get_feature_uids(self, features=None, verbose=True):
    if features is None:
        # fromuids scan all get_dfans
        feature_uids = self.features_df.get_column("feature_uid").to_list()
    elif isinstance(features, list):
        # if features is a list, ensure all elements are valid feature_uids
        feature_uids = [
            f
            for f in features
            if f in self.features_df.get_column("feature_uid").to_list()
        ]
        if verbose and not feature_uids:
            self.logger.error("No valid feature_uids provided.")

    return feature_uids


def get_scan(self, scans: list | None = None, verbose=True):
    scan_uids = self._get_scan_uids(scans, verbose=False)
    if not scan_uids:
        if verbose:
            self.logger.warning("No valid scan_uids provided.")
        return None

    scan = self.scans_df.filter(pl.col("scan_uid").is_in(scan_uids))
    return scan


def find_closest_scan(
    self,
    rt,
    prec_mz=None,
    mz_tol=0.01,
):
    """
    Find the closest scan based on retention time (rt), applying additional filtering on precursor m/z (prec_mz) if provided.
    Parameters:
        rt (float): The target retention time to find the closest scan.
        prec_mz (float, optional): The precursor m/z value used to filter scans. If given, only scans with ms_level 2 are considered
                                    and filtered to include only those within mz_tol of prec_mz.
        mz_tol (float, optional): The tolerance to apply when filtering scans by precursor m/z. Defaults to 0.01.
    Returns:
        dict or None: A dictionary representing the closest scan if a matching scan is found;
                        otherwise, returns None.
    Notes:
        - If the scans_df attribute is None, the function prints an error message and returns None.
        - When prec_mz is provided, it filters scans where ms_level equals 2 and the precursor m/z is within the given mz_tol range.
        - If prec_mz is not provided, scans with ms_level equal to 1 are considered.
        - The function calculates the absolute difference between each scan's rt and the given rt, sorting the scans by this difference.
        - If no scans match the criteria, an error message is printed before returning None.
    """
    # check if scans_df is None
    if self.scans_df is None:
        self.logger.warning("No scans found.")
        return None
    if prec_mz is not None:
        ms_level = 2
        scans = self.scans_df.filter(pl.col("ms_level") == ms_level)
        # find all scans with prec_mz within mz_tol of prec_mz
        scans = scans.filter(pl.col("prec_mz") > prec_mz - mz_tol)
        scans = scans.filter(pl.col("prec_mz") < prec_mz + mz_tol)
        # sort by distance to rt
        scans = scans.with_columns((pl.col("rt") - rt).abs().alias("rt_diff"))
        scans = scans.sort("rt_diff")
        # return the closest scan
        if len(scans) > 0:
            scan = scans[0]
        else:
            self.logger.warning(
                f"No scans found with prec_mz {prec_mz} within {mz_tol} of rt {rt}.",
            )
            return None
    else:
        mslevel = 1
        scans = self.scans_df.filter(pl.col("ms_level") == mslevel)
        # sort by distance to rt
        scans = scans.with_columns((pl.col("rt") - rt).abs().alias("rt_diff"))
        scans = scans.sort("rt_diff")
        # return the closest scan
        if len(scans) > 0:
            scan = scans[0]
        else:
            self.logger.warning(
                f"No scans found with ms_level {mslevel} within {mz_tol} of rt {rt}.",
            )
            return None
    # convert to dict

    return scan.row(0, named=True)


# TODO the variables here do not follow the rest (mz, rt being tuples, etc.)


def filter_features(
    self,
    inplace=False,
    mz=None,
    rt=None,
    coherence=None,
    inty=None,
    rt_delta=None,
    iso=None,
    iso_of=None,
    has_MS2=None,
    prominence_scaled=None,
    height_scaled=None,
    prominence=None,
    height=None,
):
    # remove all features with coherence < coherence
    if self.features_df is None:
        # self.logger.info("No features found. R")
        return
    feats = self.features_df.clone()
    if coherence is not None:
        has_coherence = "chrom_coherence" in self.features_df.columns
        if not has_coherence:
            self.logger.warning("No coherence data found in features.")
        else:
            # record len for logging
            feats_len_before_filter = len(feats)
            if isinstance(coherence, tuple) and len(coherence) == 2:
                min_coherence, max_coherence = coherence
                feats = feats.filter(
                    (pl.col("chrom_coherence") >= min_coherence)
                    & (pl.col("chrom_coherence") <= max_coherence),
                )
            else:
                feats = feats.filter(pl.col("chrom_coherence") >= coherence)
            self.logger.debug(
                f"Filtered features by coherence. Features removed: {feats_len_before_filter - len(feats)}",
            )

    if mz is not None:
        feats_len_before_filter = len(feats)
        if isinstance(mz, tuple) and len(mz) == 2:
            min_mz, max_mz = mz
            feats = feats.filter((pl.col("mz") >= min_mz) & (pl.col("mz") <= max_mz))
        else:
            feats = feats.filter(pl.col("mz") >= mz)
        self.logger.debug(
            f"Filtered features by mz. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if rt is not None:
        feats_len_before_filter = len(feats)
        if isinstance(rt, tuple) and len(rt) == 2:
            min_rt, max_rt = rt
            feats = feats.filter((pl.col("rt") >= min_rt) & (pl.col("rt") <= max_rt))
        else:
            feats = feats.filter(pl.col("rt") >= rt)
        self.logger.debug(
            f"Filtered features by rt. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if inty is not None:
        feats_len_before_filter = len(feats)
        if isinstance(inty, tuple) and len(inty) == 2:
            min_inty, max_inty = inty
            feats = feats.filter(
                (pl.col("inty") >= min_inty) & (pl.col("inty") <= max_inty),
            )
        else:
            feats = feats.filter(pl.col("inty") >= inty)
        self.logger.debug(
            f"Filtered features by intensity. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if rt_delta is not None:
        feats_len_before_filter = len(feats)
        if "rt_delta" not in feats.columns:
            self.logger.warning("No rt_delta data found in features.")
            return
        if isinstance(rt_delta, tuple) and len(rt_delta) == 2:
            min_rt_delta, max_rt_delta = rt_delta
            feats = feats.filter(
                (pl.col("rt_delta") >= min_rt_delta)
                & (pl.col("rt_delta") <= max_rt_delta),
            )
        else:
            feats = feats.filter(pl.col("rt_delta") >= rt_delta)
        self.logger.debug(
            f"Filtered features by rt_delta. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if iso is not None:
        feats_len_before_filter = len(feats)
        if isinstance(iso, tuple) and len(iso) == 2:
            min_iso, max_iso = iso
            feats = feats.filter(
                (pl.col("iso") >= min_iso) & (pl.col("iso") <= max_iso),
            )
        else:
            feats = feats.filter(pl.col("iso") == iso)
        self.logger.debug(
            f"Filtered features by iso. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if iso_of is not None:
        feats_len_before_filter = len(feats)
        if isinstance(iso_of, tuple) and len(iso_of) == 2:
            min_iso_of, max_iso_of = iso_of
            feats = feats.filter(
                (pl.col("iso_of") >= min_iso_of) & (pl.col("iso_of") <= max_iso_of),
            )
        else:
            feats = feats.filter(pl.col("iso_of") == iso_of)
        self.logger.debug(
            f"Filtered features by iso_of. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if has_MS2 is not None:
        feats_len_before_filter = len(feats)
        if has_MS2:
            feats = feats.filter(pl.col("ms2_scans").is_not_null())
        else:
            feats = feats.filter(pl.col("ms2_scans").is_null())
        self.logger.debug(
            f"Filtered features by MS2 presence. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if prominence_scaled is not None:
        feats_len_before_filter = len(feats)
        if isinstance(prominence_scaled, tuple) and len(prominence_scaled) == 2:
            min_prominence_scaled, max_prominence_scaled = prominence_scaled
            feats = feats.filter(
                (pl.col("chrom_prominence_scaled") >= min_prominence_scaled)
                & (pl.col("chrom_prominence_scaled") <= max_prominence_scaled),
            )
        else:
            feats = feats.filter(pl.col("chrom_prominence_scaled") >= prominence_scaled)
        self.logger.debug(
            f"Filtered features by prominence_scaled. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if height_scaled is not None:
        feats_len_before_filter = len(feats)
        if isinstance(height_scaled, tuple) and len(height_scaled) == 2:
            min_height_scaled, max_height_scaled = height_scaled
            feats = feats.filter(
                (pl.col("chrom_height_scaled") >= min_height_scaled)
                & (pl.col("chrom_height_scaled") <= max_height_scaled),
            )
        else:
            feats = feats.filter(pl.col("chrom_height_scaled") >= height_scaled)
        self.logger.debug(
            f"Filtered features by height_scaled. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if prominence is not None:
        feats_len_before_filter = len(feats)
        if isinstance(prominence, tuple) and len(prominence) == 2:
            min_prominence, max_prominence = prominence
            feats = feats.filter(
                (pl.col("chrom_prominence") >= min_prominence)
                & (pl.col("chrom_prominence") <= max_prominence),
            )
        else:
            feats = feats.filter(pl.col("chrom_prominence") >= prominence)
        self.logger.debug(
            f"Filtered features by prominence. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if height is not None:
        feats_len_before_filter = len(feats)
        # Check if chrom_height column exists, if not use chrom_height_scaled
        height_col = (
            "chrom_height" if "chrom_height" in feats.columns else "chrom_height_scaled"
        )
        if isinstance(height, tuple) and len(height) == 2:
            min_height, max_height = height
            feats = feats.filter(
                (pl.col(height_col) >= min_height) & (pl.col(height_col) <= max_height),
            )
        else:
            feats = feats.filter(pl.col(height_col) >= height)
        self.logger.debug(
            f"Filtered features by {height_col}. Features removed: {feats_len_before_filter - len(feats)}",
        )

    self.logger.info(f"Filtered features. Features left: {len(feats)}")
    if inplace:
        self.features_df = feats
    else:
        return feats


def _delete_ms2(self):
    """
    Unlinks MS2 spectra from features in the dataset.
    This method removes the association between MS2 spectra and features in the features dataframe by setting
    the 'ms2_scans' and 'ms2_specs' columns to None. It also updates the scans dataframe to remove the feature
    id (feature_uid) association for the linked MS2 spectra.
    Parameters:
    Returns:
        None
    Side Effects:
        Updates self.features_df by setting 'ms2_scans' and 'ms2_specs' columns to None. Also, updates self.scans_df
        by resetting the 'feature_uid' column for linked MS2 spectra.
    """
    if self.features_df is None:
        # self.logger.warning("No features found.")
        return

    self.logger.debug("Unlinking MS2 spectra from features...")

    # Set ms2_scans and ms2_specs to None using Polars syntax
    self.features_df = self.features_df.with_columns([
        pl.lit(None).alias("ms2_scans"),
        pl.lit(None).alias("ms2_specs"),
    ])

    # Update scans_df to remove feature_uid association for linked MS2 spectra
    self.scans_df = self.scans_df.with_columns(
        pl.when(pl.col("ms_level") == 2)
        .then(None)
        .otherwise(pl.col("feature_uid"))
        .alias("feature_uid"),
    )
    self.logger.info("MS2 spectra unlinked from features.")
