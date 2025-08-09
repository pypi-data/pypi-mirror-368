"""
study.py

This module provides tools for multi-sample mass spectrometry data analysis and cross-sample feature alignment.
It defines the `study` class, which manages collections of DDA files, performs feature alignment across samples,
generates consensus features, and provides study-level visualization and reporting capabilities.

Key Features:
- **Multi-Sample Management**: Handle collections of mass spectrometry files with metadata.
- **Feature Alignment**: Align features across multiple samples using retention time and m/z tolerances.
- **Consensus Features**: Generate consensus feature tables from aligned data.
- **Batch Processing**: Automated processing of entire studies with configurable parameters.
- **Study Visualization**: Generate comparative plots and alignment visualizations.
- **Export Capabilities**: Export study results in various formats for downstream analysis.

Dependencies:
- `pyopenms`: For mass spectrometry data handling and algorithms.
- `polars` and `pandas`: For efficient data manipulation and analysis.
- `bokeh`, `holoviews`, `panel`: For interactive visualizations and dashboards.
- `numpy`: For numerical computations and array operations.

Classes:
- `study`: Main class for multi-sample study management, providing methods for file loading,
  feature alignment, consensus generation, and study-level analysis.

Example Usage:
```python
from study import study

# Create study from multiple files
study_obj = study()
study_obj.load_files(["sample1.mzML", "sample2.mzML", "sample3.mzML"])
study_obj.process_all()
study_obj.align()
study_obj.plot_alignment_bokeh()
study_obj.export_consensus()
```

See Also:
- `single.py`: For individual file processing before study-level analysis.
- `parameters.study_parameters`: For study-specific parameter configuration.


"""

from __future__ import annotations

import importlib
import os
import sys

import polars as pl

# Study-specific imports
from masster.study.h5 import _load_study5
from masster.study.h5 import _save_study5
from masster.study.helpers import _get_consensus_uids
from masster.study.helpers import _get_feature_uids
from masster.study.helpers import _get_sample_uids
from masster.study.helpers import compress
from masster.study.helpers import fill_reset
from masster.study.helpers import get_chrom
from masster.study.helpers import get_consensus
from masster.study.helpers import get_consensus_matches
from masster.study.helpers import get_consensus_matrix
from masster.study.helpers import get_orphans
from masster.study.helpers import get_gaps_matrix
from masster.study.helpers import get_gaps_stats
from masster.study.helpers import align_reset
from masster.study.helpers import set_default_folder
from masster.study.load import add_folder
from masster.study.load import add_sample
from masster.study.load import (
    fill_chrom_single,
    fill_chrom,
    _process_sample_for_parallel_fill,
)
from masster.study.load import _get_missing_consensus_sample_combinations
from masster.study.load import load
from masster.study.load import _load_consensusXML
from masster.study.load import load_features
from masster.study.load import sanitize

from masster.study.plot import plot_alignment
from masster.study.plot import plot_alignment_bokeh
from masster.study.plot import plot_chrom
from masster.study.plot import plot_consensus_2d
from masster.study.plot import plot_samples_2d
from masster.study.processing import align
from masster.study.processing import filter_consensus
from masster.study.processing import filter_features
from masster.study.processing import find_consensus
from masster.study.processing import integrate_chrom
from masster.study.processing import find_ms2
from masster.study.parameters import store_history
from masster.study.parameters import get_parameters
from masster.study.parameters import update_parameters
from masster.study.parameters import get_parameters_property
from masster.study.parameters import set_parameters_property
from masster.study.save import save
from masster.study.save import save_consensus
from masster.study.save import _save_consensusXML
from masster.study.save import save_samples
from masster.study.export import export_mgf

from masster.logger import MassterLogger
from masster.study.defaults.study_def import study_defaults


class Study:
    """
    A class for managing and analyzing multi-sample mass spectrometry studies.

    The `study` class provides comprehensive tools for handling collections of DDA
    (Data-Dependent Acquisition) mass spectrometry files, performing cross-sample
    feature alignment, generating consensus features, and conducting study-level
    analysis and visualization.

    Attributes:
        default_folder (str): Default directory for study files and outputs.
        ddafiles (dict): Dictionary containing loaded ddafile objects keyed by sample names.
        features_df (pl.DataFrame): Combined features from all samples in the study.
        consensus_df (pl.DataFrame): Consensus features generated from alignment.
        metadata_df (pl.DataFrame): Sample metadata and experimental information.

    Key Methods:
        - `add_folder()`: Load all files from a directory into the study.
        - `add_sample()`: Add individual sample files to the study.
        - `process_all()`: Batch process all samples with feature detection.
        - `align()`: Perform cross-sample feature alignment.
        - `plot_alignment_bokeh()`: Visualize alignment results.
        - `export_consensus()`: Export consensus features for downstream analysis.

    Example Usage:
        >>> from masster import study
        >>> study_obj = study(default_folder="./data")
        >>> study_obj.load_folder("./mzml_files")
        >>> study_obj.process_all()
        >>> study_obj.align()
        >>> study_obj.plot_alignment_bokeh()
        >>> study_obj.export_consensus("consensus_features.csv")

    See Also:
        - `ddafile`: For individual sample processing before study-level analysis.
        - `StudyParameters`: For configuring study-specific parameters.
    """

    def __init__(
        self,
        filename=None,
        **kwargs,
    ):
        """
        Initialize a Study instance for multi-sample mass spectrometry analysis.

        This constructor initializes various attributes related to file handling,
        data storage, and processing parameters used for study-level analysis.

        Parameters:
            filename (str, optional): Path to a .study5 file to load automatically.
                                    If provided, the default_folder will be set to the
                                    directory containing this file, and the study will
                                    be loaded automatically.
            **kwargs: Keyword arguments for setting study parameters. Can include:
                     - A study_defaults instance to set all parameters at once (pass as params=study_defaults(...))
                     - Individual parameter names and values (see study_defaults for available parameters)

                     Core initialization parameters:
                     - default_folder (str, optional): Default directory for study files and outputs
                     - label (str, optional): An optional label to identify the study
                     - log_level (str): The logging level to be set for the logger. Defaults to 'INFO'
                     - log_label (str, optional): Optional label for the logger
                     - log_sink (str): Output sink for logging. Default is "sys.stdout"

                     For backward compatibility, original signature is supported:
                     Study(default_folder=..., label=..., log_level=..., log_label=..., log_sink=...)
        """
        # Initialize default parameters

        # Handle filename parameter for automatic loading
        auto_load_filename = None
        if filename is not None:
            if not filename.endswith('.study5'):
                raise ValueError("filename must be a .study5 file")
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Study file not found: {filename}")
            
            # Set default_folder to the directory containing the file if not already specified
            if 'default_folder' not in kwargs:
                kwargs['default_folder'] = os.path.dirname(os.path.abspath(filename))
            
            auto_load_filename = filename

        # Check if a study_defaults instance was passed
        if "params" in kwargs and isinstance(kwargs["params"], study_defaults):
            params = kwargs.pop("params")
        else:
            # Create default parameters and update with provided values
            params = study_defaults()

            # Update with any provided parameters
            for key, value in kwargs.items():
                if hasattr(params, key):
                    params.set(key, value, validate=True)

        # Store parameter instance for method access
        self.parameters = params
        self.history = {}
        self.store_history(["study"], params.to_dict())

        # Set instance attributes (ensure proper string values for logger)
        self.default_folder = params.default_folder
        self.label = params.label
        self.log_level = params.log_level
        self.log_label = (params.log_label + " | " if params.log_label else "")
        self.log_sink = params.log_sink

        if self.default_folder is not None and not os.path.exists(self.default_folder):
            # create the folder if it does not exist
            os.makedirs(self.default_folder)

        self.samples_df = pl.DataFrame(
            {
                "sample_uid": [],
                "sample_name": [],
                "sample_path": [],
                "sample_type": [],
                "size": [],
                "map_id": [],
            },
            schema={
                "sample_uid": pl.Int64,
                "sample_name": pl.Utf8,
                "sample_path": pl.Utf8,
                "sample_type": pl.Utf8,
                "size": pl.Int64,
                "map_id": pl.Utf8,
            },
        )
        self.features_maps = []
        self.features_df = pl.DataFrame()
        self.consensus_ms2 = pl.DataFrame()
        self.consensus_df = pl.DataFrame()
        self.consensus_map = None
        self.consensus_mapping_df = pl.DataFrame()
        self.alignment_ref_index = None

        # Initialize independent logger
        self.logger = MassterLogger(
            instance_type="study",
            level=self.log_level,
            label=self.log_label,
            sink=self.log_sink
        )

        # Auto-load study file if filename was provided
        if auto_load_filename is not None:
            self.load(filename=auto_load_filename)

    

    # Attach module functions as class methods  
    load = load
    save = save 
    save_consensus = save_consensus 
    save_samples = save_samples 
    align = align 
    fill_chrom_single = fill_chrom_single 
    find_consensus = find_consensus 
    find_ms2 = find_ms2 
    integrate_chrom = integrate_chrom 
    store_history = store_history 
    get_parameters = get_parameters 
    update_parameters = update_parameters 
    get_parameters_property = get_parameters_property 
    set_parameters_property = set_parameters_property 
    plot_alignment = plot_alignment 
    plot_alignment_bokeh = plot_alignment_bokeh 
    plot_chrom = plot_chrom 
    plot_consensus_2d = plot_consensus_2d 
    plot_samples_2d = plot_samples_2d 
    get_consensus = get_consensus 
    get_chrom = get_chrom 
    get_consensus_matches = get_consensus_matches 
    compress = compress 
    fill_reset = fill_reset 
    align_reset = align_reset 

    # Additional method assignments for all imported functions
    add_folder = add_folder 
    add_sample = add_sample 
    _load_study5 = _load_study5 
    _save_study5 = _save_study5 
    _get_consensus_uids = _get_consensus_uids 
    _get_feature_uids = _get_feature_uids 
    _get_sample_uids = _get_sample_uids 
    get_consensus_matrix = get_consensus_matrix 
    get_gaps_matrix = get_gaps_matrix 
    get_gaps_stats = get_gaps_stats 
    get_orphans = get_orphans
    set_default_folder = set_default_folder 
    fill_chrom = fill_chrom 
    _process_sample_for_parallel_fill = _process_sample_for_parallel_fill 
    _get_missing_consensus_sample_combinations = _get_missing_consensus_sample_combinations 
    _load_consensusXML = _load_consensusXML 
    load_features = load_features 
    sanitize = sanitize 
    filter_consensus = filter_consensus 
    filter_features = filter_features 
    _save_consensusXML = _save_consensusXML 
    export_mgf = export_mgf 


    def reload(self):
        """
        Reloads all masster modules to pick up any changes to their source code,
        and updates the instance's class reference to the newly reloaded class version.
        This ensures that the instance uses the latest implementation without restarting the interpreter.
        """
        # Reset logger configuration flags to allow proper reconfiguration after reload
        try:
            import masster.sample.logger as logger_module

            if hasattr(logger_module, "_STUDY_LOGGER_CONFIGURED"):
                logger_module._STUDY_LOGGER_CONFIGURED = False
        except Exception:
            pass

        # Get the base module name (masster)
        base_modname = self.__class__.__module__.split(".")[0]
        current_module = self.__class__.__module__

        # Dynamically find all study submodules
        study_modules = []
        study_module_prefix = f"{base_modname}.study."

        # Get all currently loaded modules that are part of the study package
        for module_name in sys.modules:
            if (
                module_name.startswith(study_module_prefix)
                and module_name != current_module
            ):
                study_modules.append(module_name)

        # Add core masster modules
        core_modules = [
            f"{base_modname}._version",
            f"{base_modname}.chromatogram",
            f"{base_modname}.spectrum",
            f"{base_modname}.parameters",
        ]

        # Add any parameters submodules that are loaded
        for module_name in sys.modules:
            if (
                module_name.startswith(f"{base_modname}.parameters.")
                and module_name not in core_modules
            ):
                core_modules.append(module_name)

        all_modules_to_reload = core_modules + study_modules

        # Reload all discovered modules
        for full_module_name in all_modules_to_reload:
            try:
                if full_module_name in sys.modules:
                    mod = sys.modules[full_module_name]
                    importlib.reload(mod)
                    self.logger.debug(f"Reloaded module: {full_module_name}")
            except Exception as e:
                self.logger.warning(f"Failed to reload module {full_module_name}: {e}")

        # Finally, reload the current module (sample.py)
        try:
            mod = __import__(current_module, fromlist=[current_module.split(".")[0]])
            importlib.reload(mod)

            # Get the updated class reference from the reloaded module
            new = getattr(mod, self.__class__.__name__)
            # Update the class reference of the instance
            self.__class__ = new

            self.logger.debug("Module reload completed")
        except Exception as e:
            self.logger.error(f"Failed to reload current module {current_module}: {e}")

    def __str__(self):
        """
        Returns a string representation of the study.

        Returns:
            str: A summary string of the study.
        """
        return ""

    def logger_update(self, level: str | None = None, label: str | None = None, sink: str | None = None):
        """Update the logging configuration for this Study instance.
        
        Args:
            level: New logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
            label: New label for log messages
            sink: New output sink (file path, file object, or "sys.stdout")
        """
        if level is not None:
            self.log_level = level.upper()
            self.logger.update_level(level)
        
        if label is not None:
            self.log_label = label + " | " if len(label) > 0 else ""
            self.logger.update_label(self.log_label)
        
        if sink is not None:
            if sink == "sys.stdout":
                self.log_sink = sys.stdout
            else:
                self.log_sink = sink
            self.logger.update_sink(self.log_sink)

    def info(self):
        """
        Display study information with optimized performance.

        Returns a summary string of the study including folder, features count,
        samples count, and various statistics.
        """
        # Cache DataFrame lengths and existence checks
        consensus_df_len = (
            len(self.consensus_df) if not self.consensus_df.is_empty() else 0
        )
        samples_df_len = len(self.samples_df) if not self.samples_df.is_empty() else 0
        consensus_ms2_len = len(self.consensus_ms2) if not self.consensus_ms2.is_empty() else 0
        
        # Calculate consensus statistics only if consensus_df exists and has data
        if consensus_df_len > 0:
            # Execute the aggregation once
            stats_result = self.consensus_df.select([
                pl.col("number_samples").min().alias("min_samples"),
                pl.col("number_samples").mean().alias("mean_samples"),
                pl.col("number_samples").max().alias("max_samples")

            ]).row(0)

            min_samples = stats_result[0] if stats_result[0] is not None else 0
            mean_samples = stats_result[1] if stats_result[1] is not None else 0
            max_samples = stats_result[2] if stats_result[2] is not None else 0
        else:
            min_samples = 0
            mean_samples = 0
            max_samples = 0
        
        # Count only features where 'filled' == False
        if not self.features_df.is_empty() and 'filled' in self.features_df.columns:
            unfilled_features_count = self.features_df.filter(~self.features_df['filled']).height
        else:
            unfilled_features_count = 0

        # Optimize chrom completeness calculation
        if consensus_df_len > 0 and samples_df_len > 0 and not self.features_df.is_empty():
            
            # Use more efficient counting - count non-null chroms only for features in consensus mapping
            if not self.consensus_mapping_df.is_empty():
                non_null_chroms = self.features_df.join(
                    self.consensus_mapping_df.select("feature_uid"),
                    on="feature_uid",
                    how="inner"
                ).select(
                    pl.col("chrom").is_not_null().sum().alias("count")
                ).item()
            else:
                non_null_chroms = 0
            total_possible = samples_df_len * consensus_df_len
            chrom_completeness = (
                non_null_chroms / total_possible if total_possible > 0 else 0
            )
            not_in_consensus = len(self.features_df.filter(~self.features_df['feature_uid'].is_in(self.consensus_mapping_df['feature_uid'].to_list())))
            ratio_not_in_consensus_to_total = not_in_consensus / unfilled_features_count if unfilled_features_count > 0 else 0
            ratio_in_consensus_to_total = (unfilled_features_count- not_in_consensus) / len(self.features_df) if len(self.features_df) > 0 else 0

        else:
            chrom_completeness = 0
            not_in_consensus = 0
            ratio_not_in_consensus_to_total = 0
            ratio_in_consensus_to_total = 0
        

        
        # calculate for how many consensus features there is at least one MS2 spectrum linked
        consensus_with_ms2 = self.consensus_ms2.select(
            pl.col("consensus_uid").is_not_null().sum().alias("count")
        ).item() if not self.consensus_ms2.is_empty() else 0    

        # estimate memory usage
        memory_usage = (
            self.samples_df.estimated_size() +
            self.features_df.estimated_size() +
            self.consensus_df.estimated_size() +
            self.consensus_ms2.estimated_size() +
            self.consensus_mapping_df.estimated_size()
        )

        summary = (
            f"Default folder:         {self.default_folder}\n"
            f"Samples:                {samples_df_len}\n"
            f"Features:               {unfilled_features_count}\n"
            f"- in consensus:         {ratio_in_consensus_to_total*100:.0f}%\n"
            f"- non in consensus:     {ratio_not_in_consensus_to_total*100:.0f}%\n"
            f"Consensus:              {consensus_df_len}\n"
            f"- Min samples count:    {min_samples:.0f}\n"
            f"- Mean samples count:   {mean_samples:.0f}\n"
            f"- Max samples count:    {max_samples:.0f}\n"            
            f"- with MS2:             {consensus_with_ms2}\n"
            f"Chrom completeness:     {chrom_completeness*100:.0f}%\n"
            f"Memory usage:           {memory_usage / (1024 ** 2):.2f} MB\n"
        )

        print(summary)



if __name__ == "__main__":
    # This block is executed when the script is run directly
    pass
