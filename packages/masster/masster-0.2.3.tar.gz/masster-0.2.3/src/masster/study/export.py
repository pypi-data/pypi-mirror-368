from __future__ import annotations

import os

from datetime import datetime

import numpy as np
import pandas as pd


from tqdm import tqdm

from masster.spectrum import combine_peaks
from masster.study.defaults import export_mgf_defaults


def export_mgf(self, **kwargs):
    """
    Export consensus features as MGF format for database searching.

    Parameters:
        **kwargs: Keyword arguments for export parameters. Can include:
            - An export_defaults instance to set all parameters at once
            - Individual parameter names and values (see export_defaults for details)

    Key Parameters:
        filename (str): Output MGF file name (default: "features.mgf").
        selection (str): "best" for first scan, "all" for every scan (default: "best").
        split_energy (bool): Process MS2 scans by unique energy (default: True).
        merge (bool): If selection="all", merge MS2 scans into one spectrum (default: False).
        mz_start (float): Minimum m/z for feature selection (default: None).
        mz_end (float): Maximum m/z for feature selection (default: None).
        rt_start (float): Minimum RT for feature selection (default: None).
        rt_end (float): Maximum RT for feature selection (default: None).
        centroid (bool): Apply centroiding to spectra (default: True).
        inty_min (float): Minimum intensity threshold (default: None).
        deisotope (bool): Apply deisotoping to spectra (default: True).
        verbose (bool): Enable verbose logging (default: False).
        precursor_trim (float): Precursor trimming value (default: -10).
        centroid_algo (str): Centroiding algorithm (default: "lmp").
    """
    # parameters initialization
    params = export_mgf_defaults()
    for key, value in kwargs.items():
        if isinstance(value, export_mgf_defaults):
            params = value
            self.logger.debug("Using provided export_defaults parameters")
        else:
            if hasattr(params, key):
                if params.set(key, value, validate=True):
                    self.logger.debug(f"Updated parameter {key} = {value}")
                else:
                    self.logger.warning(
                        f"Failed to set parameter {key} = {value} (validation failed)",
                    )
            else:
                self.logger.debug(f"Unknown parameter {key} ignored")
    # end of parameter initialization

    # Store parameters in the Study object
    self.store_history(["export_mgf"], params.to_dict())
    self.logger.debug("Parameters stored to export_mgf")

    # Get parameter values for use in the method
    filename = params.get("filename")
    selection = params.get("selection")
    split_energy = params.get("split_energy")
    merge = params.get("merge")
    mz_start = params.get("mz_start")
    mz_end = params.get("mz_end")
    rt_start = params.get("rt_start")
    rt_end = params.get("rt_end")
    centroid = params.get("centroid")
    inty_min = params.get("inty_min")
    deisotope = params.get("deisotope")

    if self.consensus_df is None:
        self.logger.error("No consensus map found. Please run find_consensus() first.")
        return
    if self.consensus_ms2 is None:
        self.logger.error("No consensus MS2 data found. Please run link_ms2() first.")
        return

    # Convert to pandas for merge operation since the result is used for groupby
    consensus_df_pd = self.consensus_df.to_pandas()
    consensus_ms2_pd = self.consensus_ms2.to_pandas()

    features = pd.merge(
        consensus_df_pd,
        consensus_ms2_pd,
        how="right",
        on="consensus_uid",
    )
    if len(features) == 0:
        self.logger.warning("No features found.")
        return

    # Pre-group by consensus_uid for fast access
    grouped = features.groupby("consensus_uid")

    def filter_peaks(spec, inty_min=None):
        spec = spec.copy()
        length = len(spec.mz)
        mask = np.ones(length, dtype=bool)
        if inty_min is not None and inty_min > 0:
            mask = mask & (spec.inty >= inty_min)
        for attr in spec.__dict__:
            arr = getattr(spec, attr)
            if (
                isinstance(arr, list | np.ndarray)
                and hasattr(arr, "__len__")
                and len(arr) == length
            ):
                setattr(spec, attr, np.array(arr)[mask])
        return spec

    def write_ion(f, title, id, uid, mz, rt, charge, spect):
        if spect is None:
            return
        f.write(f"BEGIN IONS\nTITLE={title}\n")
        f.write(f"FEATURE_ID={id}\n")
        f.write(f"FEATURE_UID={uid}\n")
        f.write(f"CHARGE={charge}\nPEPMASS={mz}\nRTINSECONDS={rt}\n")
        if spect.ms_level is None:
            f.write("MSLEVEL=1\n")
        else:
            f.write(f"MSLEVEL={spect.ms_level}\n")
        if (
            spect.ms_level is not None
            and spect.ms_level > 1
            and hasattr(spect, "energy")
        ):
            f.write(f"ENERGY={spect.energy}\n")
        for mz, inty in zip(spect.mz, spect.inty, strict=False):
            f.write(f"{mz:.5f} {inty:.0f}\n")
        f.write("END IONS\n\n")

    # Prepare output path
    if not os.path.isabs(filename):
        if self.default_folder is not None:
            filename = os.path.join(self.default_folder, filename)
        else:
            filename = os.path.join(os.getcwd(), filename)

    skip = 0
    self.logger.info(f"Exporting MGF for {len(grouped)} consensus features...")
    with open(filename, "w", encoding="utf-8") as f:
        tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
        for _consensus_uid, cons_ms2 in tqdm(
            grouped,
            total=len(grouped),
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Feature",
            disable=tdqm_disable,
        ):
            # Use the first row for feature-level info
            row = cons_ms2.iloc[0]
            if mz_start is not None and row["mz"] < mz_start:
                continue
            if mz_end is not None and row["mz"] > mz_end:
                continue
            if rt_start is not None and row["rt"] < rt_start:
                continue
            if rt_end is not None and row["rt"] > rt_end:
                continue
            if len(cons_ms2) == 0:
                skip += 1
                continue

            if split_energy:
                energies = cons_ms2["energy"].unique()
                for e in energies:
                    cons_ms2_e = cons_ms2[cons_ms2["energy"] == e]
                    if selection == "best":
                        idx = cons_ms2_e["prec_inty"].idxmax()
                        cons_ms2_e_row = cons_ms2_e.loc[idx]
                        spect = cons_ms2_e_row["spec"]
                        if spect is None:
                            skip += 1
                            continue
                        if centroid:
                            spect = spect.centroid()
                        if deisotope:
                            spect = spect.deisotope()
                        spect = filter_peaks(spect, inty_min=inty_min)
                        write_ion(
                            f,
                            f"uid:{cons_ms2_e_row['consensus_uid']}, rt:{cons_ms2_e_row['rt']:.2f}, mz:{cons_ms2_e_row['mz']:.4f}, energy:{e}, sample_uid:{cons_ms2_e_row['sample_uid']}, scan_id:{cons_ms2_e_row['scan_id']}",
                            cons_ms2_e_row["consensus_id"],
                            cons_ms2_e_row["consensus_uid"],
                            cons_ms2_e_row["mz"],
                            cons_ms2_e_row["rt"],
                            round(cons_ms2_e_row["charge_mean"]),
                            spect,
                        )
                    else:
                        for row_e in cons_ms2_e.iter_rows(named=True):
                            spect = row_e["spec"]
                            if spect is None:
                                continue
                            if centroid:
                                spect = spect.centroid()
                            if deisotope:
                                spect = spect.deisotope()
                            spect = filter_peaks(spect, inty_min=inty_min)
                            write_ion(
                                f,
                                f"uid:{row_e['consensus_uid']}, rt:{row_e['rt']:.2f}, mz:{row_e['mz']:.4f}, energy:{e}, sample_uid:{row_e['sample_uid']}, scanid:{row_e['scan_id']}",
                                row_e["consensus_id"],
                                row_e["consensus_uid"],
                                row_e["mz"],
                                row_e["rt"],
                                round(row_e["charge_mean"]),
                                spect,
                            )
            else:
                if selection == "best":
                    idx = cons_ms2["prec_inty"].idxmax()
                    cons_ms2_e_row = cons_ms2.loc[idx]
                    spect = cons_ms2_e_row["spec"]
                    if spect is None:
                        continue
                    if centroid:
                        spect = spect.centroid()
                    if deisotope:
                        spect = spect.deisotope()
                    spect = filter_peaks(spect, inty_min=inty_min)
                    write_ion(
                        f,
                        f"uid:{cons_ms2_e_row['consensus_uid']}, rt:{cons_ms2_e_row['rt']:.2f}, mz:{cons_ms2_e_row['mz']:.4f}, energy:{cons_ms2_e_row['energy']}, sample_uid:{cons_ms2_e_row['sample_uid']}, scan_id:{cons_ms2_e_row['scan_id']}",
                        cons_ms2_e_row["consensus_id"],
                        cons_ms2_e_row["consensus_uid"],
                        cons_ms2_e_row["mz"],
                        cons_ms2_e_row["rt"],
                        round(cons_ms2_e_row["charge_mean"]),
                        spect,
                    )

                elif selection == "all":
                    if merge:
                        specs = [
                            row_e["spec"]
                            for row_e in cons_ms2.iter_rows(named=True)
                            if row_e["spec"] is not None
                        ]
                        if not specs:
                            continue
                        spect = combine_peaks(specs)
                        if centroid:
                            spect = spect.denoise()
                            spect = spect.centroid()
                            spect = spect.centroid()
                        if deisotope:
                            spect = spect.deisotope()
                        spect = filter_peaks(spect, inty_min=inty_min)
                        write_ion(
                            f,
                            f"uid:{row['consensus_uid']}, rt:{row['rt']:.2f}, mz:{row['mz']:.4f}, sample_uid:{row['sample_uid']}, scan_id:{row['scan_id']}",
                            row["consensus_id"],
                            row["consensus_uid"],
                            row["mz"],
                            row["rt"],
                            round(row["charge_mean"]),
                            spect,
                        )
                    else:
                        for row_e in cons_ms2.iter_rows(named=True):
                            spect = row_e["spec"]
                            if spect is None:
                                continue
                            if centroid:
                                spect = spect.centroid()
                            if deisotope:
                                spect = spect.deisotope()
                            spect = filter_peaks(spect, inty_min=inty_min)
                            write_ion(
                                f,
                                f"uid:{row_e['consensus_uid']}, rt:{row_e['rt']:.2f}, mz:{row_e['mz']:.4f}, energy:{row_e['energy']}, sample_uid:{row_e['sample_uid']}, scan_id:{row_e['scan_id']}",
                                row_e["consensus_id"],
                                row_e["consensus_uid"],
                                row_e["mz"],
                                row_e["rt"],
                                round(row_e["charge_mean"]),
                                spect,
                            )
        self.logger.info(
            f"Exported {len(grouped) - skip} features to {filename}. Skipped {skip} features due to missing data.",
        )
