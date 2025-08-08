"""
_study_h5.py

This module provides HDF5-based save/load functionality for the Study class.
It handles serialization and deserialization of Polars DataFrames with complex objects
like Chromatogram and Spectrum instances.

Key Features:
- **HDF5 Storage**: Efficient compressed storage using HDF5 format
- **Complex Object Serialization**: JSON-based serialization for Chromatogram and Spectrum objects
- **Schema-based loading**: Uses study5_schema.json for proper type handling
- **Error Handling**: Robust error handling and logging

Dependencies:
- `h5py`: For HDF5 file operations
- `polars`: For DataFrame handling
- `json`: For complex object serialization
- `numpy`: For numerical array operations

Functions:
- `_save_study5()`: Save study to .study5 HDF5 file (new format)
- `_load_study5()`: Load study from .study5 HDF5 file (new format)
- `_save_h5()`: Save study to .h5 file (legacy format)
- `_load_h5()`: Load study from .h5 file (legacy format)
"""

import json
import os

import h5py
import polars as pl

from masster.chromatogram import Chromatogram
from masster.spectrum import Spectrum


# Helper functions for HDF5 operations
def _load_schema(schema_path: str) -> dict:
    """Load schema from JSON file with error handling."""
    try:
        with open(schema_path) as f:
            return json.load(f)  # type: ignore
    except FileNotFoundError:
        return {}


def _decode_bytes_attr(attr_value):
    """Decode metadata attribute, handling both bytes and string types."""
    if isinstance(attr_value, bytes):
        return attr_value.decode("utf-8")
    return str(attr_value) if attr_value is not None else ""


def _save_dataframe_column(group, col: str, data, dtype: str, logger, compression="gzip"):
    """
    Save a single DataFrame column to an HDF5 group with optimized compression.
    
    This optimized version uses context-aware compression strategies for better
    performance and smaller file sizes. Different compression algorithms are 
    selected based on data type and column name patterns.
    
    Args:
        group: HDF5 group to save to
        col: Column name
        data: Column data
        dtype: Data type string
        logger: Logger instance
        compression: Default compression (used for compatibility, but overridden by optimization)
    
    Compression Strategy:
        - LZF + shuffle: Fast access data (consensus_uid, rt, mz, intensity, scan_id)
        - GZIP level 6: JSON objects (chromatograms, spectra) and string data
        - GZIP level 9: Bulk storage data (large collections)
        - LZF: Standard numeric arrays
    """
    
    # Optimized compression configuration
    COMPRESSION_CONFIG = {
        'fast_access': {'compression': 'lzf', 'shuffle': True},  # Fast I/O for IDs, rt, mz
        'numeric': {'compression': 'lzf'},  # Standard numeric data
        'string': {'compression': 'gzip', 'compression_opts': 6},  # String data
        'json': {'compression': 'gzip', 'compression_opts': 6},  # JSON objects
        'bulk': {'compression': 'gzip', 'compression_opts': 9}  # Large bulk data
    }

    def get_optimal_compression(column_name, data_type, data_size=None):
        """Get optimal compression settings based on column type and usage pattern."""
        # Fast access columns (frequently read IDs and coordinates)
        if column_name in ['consensus_uid', 'feature_uid', 'scan_id', 'rt', 'mz', 'intensity', 'rt_original', 'mz_original']:
            return COMPRESSION_CONFIG['fast_access']
        
        # JSON object columns (complex serialized data)
        elif column_name in ['spectrum', 'chromatogram', 'chromatograms', 'ms2_specs', 'chrom']:
            return COMPRESSION_CONFIG['json']
        
        # String/text columns
        elif data_type in ['string', 'object'] and column_name in ['sample_name', 'file_path', 'label', 'file_type']:
            return COMPRESSION_CONFIG['string']
        
        # Large bulk numeric data
        elif data_size and data_size > 100000:
            return COMPRESSION_CONFIG['bulk']
        
        # Standard numeric data
        else:
            return COMPRESSION_CONFIG['numeric']
    
    # Get data size for optimization decisions
    data_size = len(data) if hasattr(data, '__len__') else None
    
    # Get optimal compression settings
    optimal_compression = get_optimal_compression(col, dtype, data_size)
    if dtype == "object":
        if col == "chrom":
            # Handle Chromatogram objects
            data_as_str = []
            for item in data:
                if item is not None:
                    data_as_str.append(item.to_json())
                else:
                    data_as_str.append("None")
            group.create_dataset(col, data=data_as_str, compression=compression)
        elif col == "ms2_scans":
            # Handle MS2 scan lists
            data_as_json_strings = []
            for item in data:
                if item is not None:
                    data_as_json_strings.append(json.dumps(list(item)))
                else:
                    data_as_json_strings.append("None")
            group.create_dataset(col, data=data_as_json_strings, **optimal_compression)
        elif col == "ms2_specs":
            # Handle MS2 spectrum lists
            data_as_lists_of_strings = []
            for item in data:
                if item is not None:
                    json_strings = []
                    for spectrum in item:
                        if spectrum is not None:
                            json_strings.append(spectrum.to_json())
                        else:
                            json_strings.append("None")
                    data_as_lists_of_strings.append(json_strings)
                else:
                    data_as_lists_of_strings.append(["None"])
            # Convert to serialized data
            serialized_data = [json.dumps(item) for item in data_as_lists_of_strings]
            group.create_dataset(col, data=serialized_data, **optimal_compression)
        elif col == "spec":
            # Handle single Spectrum objects
            data_as_str = []
            for item in data:
                if item is not None:
                    data_as_str.append(item.to_json())
                else:
                    data_as_str.append("None")
            group.create_dataset(col, data=data_as_str, compression=compression)
        else:
            logger.warning(f"Unexpectedly, column '{col}' has dtype 'object'. Implement serialization for this column.")
    elif dtype == "string":
        # Handle string columns
        string_data = ["None" if x is None else str(x) for x in data]
        group.create_dataset(col, data=string_data, **optimal_compression)
    else:
        # Handle numeric columns
        try:
            # Convert None values to -123 sentinel value for numeric columns
            import numpy as np
            data_array = np.array(data)
            
            # Check if it's a numeric dtype that might have None/null values
            if data_array.dtype == object:
                # Convert None values to -123 for numeric columns with mixed types
                processed_data = []
                for item in data:
                    if item is None:
                        processed_data.append(-123)
                    else:
                        try:
                            # Try to convert to float to check if it's numeric
                            processed_data.append(int(float(item)))
                        except (ValueError, TypeError):
                            # If conversion fails, keep original value (might be string)
                            processed_data.append(item)
                data_array = np.array(processed_data)
            
            group.create_dataset(col, data=data_array, **optimal_compression)
        except Exception as e:
            logger.warning(f"Failed to save column '{col}': {e}")


def _reconstruct_object_column(data_col, col_name: str):
    """Reconstruct object columns from serialized HDF5 data."""
    reconstructed_data: list = []
    
    for item in data_col:
        if isinstance(item, bytes):
            item = item.decode("utf-8")
        
        if item == "None" or item == "":
            reconstructed_data.append(None)
            continue
            
        try:
            if col_name == "chrom":
                reconstructed_data.append(Chromatogram.from_json(item))
            elif col_name == "ms2_scans":
                scan_list = json.loads(item)
                reconstructed_data.append(scan_list)
            elif col_name == "ms2_specs":
                json_list = json.loads(item)
                if json_list == ["None"]:
                    reconstructed_data.append(None)
                else:
                    spectrum_list: list = []
                    for json_str in json_list:
                        if json_str == "None":
                            spectrum_list.append(None)
                        else:
                            spectrum_list.append(Spectrum.from_json(json_str))
                    reconstructed_data.append(spectrum_list)
            elif col_name == "spec":
                reconstructed_data.append(Spectrum.from_json(item))
            else:
                # Unknown object column
                reconstructed_data.append(None)
        except (json.JSONDecodeError, ValueError):
            reconstructed_data.append(None)
    
    return reconstructed_data


def _clean_string_nulls(df: pl.DataFrame) -> pl.DataFrame:
    """Convert string null representations to proper nulls."""
    for col in df.columns:
        if df[col].dtype == pl.Utf8:
            df = df.with_columns([
                pl.when(pl.col(col).is_in(["None", "", "null", "NULL"]))
                .then(None)
                .otherwise(pl.col(col))
                .alias(col),
            ])
    return df


def _apply_schema_casting(df: pl.DataFrame, schema: dict, df_name: str) -> pl.DataFrame:
    """Apply schema-based type casting to DataFrame columns."""
    if df_name not in schema or "columns" not in schema[df_name]:
        return df
    
    schema_columns = schema[df_name]["columns"]
    cast_exprs = []
    
    for col in df.columns:
        if col in schema_columns:
            dtype_str = schema_columns[col]["dtype"]
            # Convert string representation to actual Polars type
            if dtype_str == "pl.Object":
                cast_exprs.append(pl.col(col))  # Keep Object type as is
            elif dtype_str == "pl.Int64":
                cast_exprs.append(pl.col(col).cast(pl.Int64, strict=False))
            elif dtype_str == "pl.Float64":
                cast_exprs.append(pl.col(col).cast(pl.Float64, strict=False))
            elif dtype_str == "pl.Utf8":
                cast_exprs.append(pl.col(col).cast(pl.Utf8, strict=False))
            elif dtype_str == "pl.Int32":
                cast_exprs.append(pl.col(col).cast(pl.Int32, strict=False))
            elif dtype_str == "pl.Boolean":
                cast_exprs.append(pl.col(col).cast(pl.Boolean, strict=False))
            elif dtype_str == "pl.Null":
                cast_exprs.append(pl.col(col).cast(pl.Null, strict=False))
            else:
                cast_exprs.append(pl.col(col))  # Keep original type
        else:
            cast_exprs.append(pl.col(col))  # Keep original type
    
    if cast_exprs:
        df = df.with_columns(cast_exprs)
    
    return df


def _reorder_columns_by_schema(df: pl.DataFrame, schema: dict, df_name: str) -> pl.DataFrame:
    """Reorder DataFrame columns to match schema order."""
    if df_name not in schema or "columns" not in schema[df_name]:
        return df
    
    schema_columns = list(schema[df_name]["columns"].keys())
    # Only reorder columns that exist in both schema and DataFrame
    existing_columns = [col for col in schema_columns if col in df.columns]
    # Add any extra columns not in schema at the end
    extra_columns = [col for col in df.columns if col not in schema_columns]
    final_column_order = existing_columns + extra_columns
    
    return df.select(final_column_order)


def _create_dataframe_with_objects(data: dict, object_columns: list) -> pl.DataFrame:
    """Create DataFrame handling Object columns properly."""
    object_data = {k: v for k, v in data.items() if k in object_columns}
    regular_data = {k: v for k, v in data.items() if k not in object_columns}
    
    # Create DataFrame with regular columns first
    if regular_data:
        df = pl.DataFrame(regular_data)
        # Add Object columns one by one
        for col, values in object_data.items():
            df = df.with_columns([pl.Series(col, values, dtype=pl.Object)])
    else:
        # Only Object columns
        df = pl.DataFrame()
        for col, values in object_data.items():
            df = df.with_columns([pl.Series(col, values, dtype=pl.Object)])
    
    return df


def _load_dataframe_from_group(group, schema: dict, df_name: str, logger, object_columns: list = None) -> pl.DataFrame:
    """Load a DataFrame from HDF5 group using schema."""
    if object_columns is None:
        object_columns = []
    
    data: dict = {}
    missing_columns = []
    
    # Iterate through schema columns in order to maintain column ordering
    logger.debug(f"Loading {df_name} - schema type: {type(schema)}, content: {schema.keys() if isinstance(schema, dict) else 'Not a dict'}")
    schema_section = schema.get(df_name, {}) if isinstance(schema, dict) else {}
    logger.debug(f"Schema section for {df_name}: {schema_section}")
    schema_columns = schema_section.get("columns", []) if isinstance(schema_section, dict) else []
    logger.debug(f"Schema columns for {df_name}: {schema_columns}")
    if schema_columns is None:
        schema_columns = []
    
    for col in (schema_columns or []):
        if col not in group:
            logger.warning(f"Column '{col}' not found in {df_name}.")
            data[col] = None
            missing_columns.append(col)
            continue
        
        dtype = schema[df_name]["columns"][col].get("dtype", "native")
        if dtype == "pl.Object" and col in object_columns:
            # Handle object columns specially
            data[col] = _reconstruct_object_column(group[col][:], col)
        else:
            # Regular columns
            column_data = group[col][:]
            
            # Convert -123 sentinel values back to None for numeric columns
            if len(column_data) > 0:
                # Check if it's a numeric column that might contain sentinel values
                try:
                    import numpy as np
                    data_array = np.array(column_data)
                    if data_array.dtype in [np.float32, np.float64, np.int32, np.int64]:
                        # Replace -123 sentinel values with None
                        processed_data: list = []
                        for item in column_data:
                            if item == -123:
                                processed_data.append(None)
                            else:
                                processed_data.append(item)
                        data[col] = processed_data
                    else:
                        data[col] = column_data
                except Exception:
                    # If any error occurs, use original data
                    data[col] = column_data
            else:
                data[col] = column_data
    
    if not data:
        return None
    
    # Handle byte string conversion for non-object columns
    for col, values in data.items():
        if col not in object_columns and values is not None and len(values) > 0 and isinstance(values[0], bytes):
            processed_values = []
            for val in values:
                if isinstance(val, bytes):
                    val = val.decode("utf-8")
                processed_values.append(val)
            data[col] = processed_values
    
    # Create DataFrame with Object columns handled properly
    if object_columns:
        df = _create_dataframe_with_objects(data, object_columns)
    else:
        df = pl.DataFrame(data)
    
    # Clean null values and apply schema
    df = _clean_string_nulls(df)
    df = _apply_schema_casting(df, schema, df_name)
    df = _reorder_columns_by_schema(df, schema, df_name)
    
    return df


def _save_study5(self, filename=None):
    """
    Save the Study instance data to a .study5 HDF5 file with optimized schema-based format.

    This method saves all Study DataFrames (samples_df, features_df, consensus_df,
    consensus_mapping_df, consensus_ms2) using the schema defined in study5_schema.json
    for proper Polars DataFrame type handling.

    Args:
        filename (str, optional): Target file name. If None, uses default based on default_folder.

    Stores:
        - metadata/format (str): Data format identifier ("master-study-1")
        - metadata/default_folder (str): Study default folder path
        - metadata/label (str): Study label
        - metadata/parameters (str): JSON-serialized parameters dictionary
        - samples/: samples_df DataFrame data
        - features/: features_df DataFrame data with Chromatogram and Spectrum objects
        - consensus/: consensus_df DataFrame data
        - consensus_mapping/: consensus_mapping_df DataFrame data
        - consensus_ms2/: consensus_ms2 DataFrame data with Spectrum objects

    Notes:
        - Uses HDF5 format with compression for efficient storage.
        - Chromatogram objects are serialized as JSON for reconstruction.
        - MS2 scan lists and Spectrum objects are properly serialized.
        - Parameters dictionary (nested dicts) are JSON-serialized for storage.
        - Optimized for use with _load_study5() method.
    """

    # if no extension is given, add .study5
    if not filename.endswith(".study5"):
        filename += ".study5"

    self.logger.info(f"Saving study to {filename}")

    # delete existing file if it exists
    if os.path.exists(filename):
        os.remove(filename)

    # Load schema for column ordering
    schema_path = os.path.join(os.path.dirname(__file__), "study5_schema.json")
    schema = _load_schema(schema_path)
    if not schema:
        self.logger.warning(f"Could not load schema from {schema_path}")

    with h5py.File(filename, "w") as f:
        # Create groups for organization
        metadata_group = f.create_group("metadata")
        features_group = f.create_group("features")
        consensus_group = f.create_group("consensus")
        consensus_mapping_group = f.create_group("consensus_mapping")
        consensus_ms2_group = f.create_group("consensus_ms2")

        # Store metadata
        metadata_group.attrs["format"] = "master-study-1"
        metadata_group.attrs["default_folder"] = str(self.default_folder) if self.default_folder is not None else ""
        metadata_group.attrs["label"] = str(self.label) if hasattr(self, "label") and self.label is not None else ""

        # Store parameters as JSON
        if hasattr(self, "parameters") and self.history is not None:
            try:
                parameters_json = json.dumps(self.history, indent=2)
                metadata_group.create_dataset("parameters", data=parameters_json)
            except (TypeError, ValueError) as e:
                self.logger.warning(f"Failed to serialize history: {e}")
                metadata_group.create_dataset("parameters", data="")
        else:
            metadata_group.create_dataset("parameters", data="")

        # Store samples_df - only create group if there's data to store
        if self.samples_df is not None and not self.samples_df.is_empty():
            samples_group = f.create_group("samples")
            samples = _reorder_columns_by_schema(self.samples_df.clone(), schema, "samples_df")
            for col in samples.columns:
                dtype = str(samples[col].dtype).lower()
                data = samples[col].to_list()
                _save_dataframe_column(samples_group, col, data, dtype, self.logger)

        # Store features_df
        if self.features_df is not None:
            features = _reorder_columns_by_schema(self.features_df.clone(), schema, "features_df")
            for col in features.columns:
                dtype = str(features[col].dtype).lower()
                column_data: object = features[col] if dtype == "object" else features[col].to_list()
                _save_dataframe_column(features_group, col, column_data, dtype, self.logger)

        # Store consensus_df
        if self.consensus_df is not None:
            consensus = _reorder_columns_by_schema(self.consensus_df.clone(), schema, "consensus_df")
            for col in consensus.columns:
                dtype = str(consensus[col].dtype).lower()
                data = consensus[col].to_list()
                _save_dataframe_column(consensus_group, col, data, dtype, self.logger)

        # Store consensus_mapping_df
        if self.consensus_mapping_df is not None:
            consensus_mapping = self.consensus_mapping_df.clone()
            for col in consensus_mapping.columns:
                try:
                    data = consensus_mapping[col].to_numpy()
                    # Use LZF compression for consensus mapping data
                    consensus_mapping_group.create_dataset(col, data=data, compression="lzf", shuffle=True)
                except Exception as e:
                    self.logger.warning(f"Failed to save column '{col}' in consensus_mapping_df: {e}")

        # Store consensus_ms2
        if self.consensus_ms2 is not None:
            consensus_ms2 = self.consensus_ms2.clone()
            for col in consensus_ms2.columns:
                dtype = str(consensus_ms2[col].dtype).lower()
                data = consensus_ms2[col] if dtype == "object" else consensus_ms2[col].to_list()
                _save_dataframe_column(consensus_ms2_group, col, data, dtype, self.logger)

    self.logger.debug(f"Save completed for {filename}")


def _load_study5(self, filename=None):
    """
    Load Study instance data from a .study5 HDF5 file.

    Restores all Study DataFrames that were saved with _save_study5() method using the
    schema defined in study5_schema.json for proper Polars DataFrame reconstruction.

    Args:
        filename (str, optional): Path to the .study5 HDF5 file to load. If None, uses default.

    Returns:
        None (modifies self in place)

    Notes:
        - Restores DataFrames with proper schema typing from study5_schema.json
        - Handles Chromatogram and Spectrum object reconstruction
        - Properly handles MS2 scan lists and spectrum lists
        - Restores parameters dictionary from JSON serialization
    """
    from datetime import datetime
    from tqdm import tqdm
    
    self.logger.info(f"Loading study from {filename}")

    # Handle default filename
    if filename is None:
        if self.default_folder is not None:
            filename = os.path.join(self.default_folder, "study.study5")
        else:
            self.logger.error("Either filename or default_folder must be provided")
            return

    # Add .study5 extension if not provided
    if not filename.endswith(".study5"):
        filename += ".study5"

    if not os.path.exists(filename):
        self.logger.error(f"File {filename} does not exist")
        return

    # Load schema for proper DataFrame reconstruction
    schema_path = os.path.join(os.path.dirname(__file__), "study5_schema.json")
    schema = _load_schema(schema_path)
    if not schema:
        self.logger.warning(f"Schema file {schema_path} not found. Using default types.")

    # Define loading steps for progress tracking
    loading_steps = [
        "metadata",
        "samples_df", 
        "features_df",
        "consensus_df",
        "consensus_mapping_df",
        "consensus_ms2"
    ]
    
    # Check if progress bar should be disabled based on log level
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    with h5py.File(filename, "r") as f:
        # Use progress bar to show loading progress
        with tqdm(
            total=len(loading_steps),
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading study",
            disable=tdqm_disable,
        ) as pbar:
            
            # Load metadata
            pbar.set_description(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading metadata")
            if "metadata" in f:
                metadata = f["metadata"]
                self.default_folder = _decode_bytes_attr(metadata.attrs.get("default_folder", ""))
                if hasattr(self, "label"):
                    self.label = _decode_bytes_attr(metadata.attrs.get("label", ""))

                # Load parameters from JSON
                if "parameters" in metadata:
                    try:
                        parameters_data = metadata["parameters"][()]
                        if isinstance(parameters_data, bytes):
                            parameters_data = parameters_data.decode("utf-8")

                        if parameters_data and parameters_data != "":
                            self.history = json.loads(parameters_data)
                        else:
                            self.history = {}
                    except (json.JSONDecodeError, ValueError, TypeError) as e:
                        self.logger.warning(f"Failed to deserialize parameters: {e}")
                        self.history = {}
                else:
                    self.history = {}

                # Reconstruct self.parameters from loaded history
                from masster.study.defaults.study_def import study_defaults
                
                # Always create a fresh study_defaults object to ensure we have all defaults
                self.parameters = study_defaults()
                
                # Update parameters from loaded history if available
                if self.history and "study" in self.history:
                    study_params = self.history["study"]
                    if isinstance(study_params, dict):
                        failed_params = self.parameters.set_from_dict(study_params, validate=False)
                        if failed_params:
                            self.logger.debug(f"Could not set study parameters: {failed_params}")
                        else:
                            self.logger.debug("Successfully updated parameters from loaded history")
                    else:
                        self.logger.debug("Study parameters in history are not a valid dictionary")
                else:
                    self.logger.debug("No study parameters found in history, using defaults")
                
                # Synchronize instance attributes with parameters (similar to __init__)
                # Note: default_folder and label are already loaded from metadata attributes above
                # but we ensure they match the parameters for consistency
                if hasattr(self.parameters, 'default_folder') and self.parameters.default_folder is not None:
                    self.default_folder = self.parameters.default_folder
                if hasattr(self.parameters, 'label') and self.parameters.label is not None:
                    self.label = self.parameters.label
                if hasattr(self.parameters, 'log_level'):
                    self.log_level = self.parameters.log_level
                if hasattr(self.parameters, 'log_label'):
                    self.log_label = self.parameters.log_label if self.parameters.log_label is not None else ""
                if hasattr(self.parameters, 'log_sink'):
                    self.log_sink = self.parameters.log_sink
            pbar.update(1)

            # Load samples_df
            pbar.set_description(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading samples")
            if "samples" in f and len(f["samples"].keys()) > 0:
                self.samples_df = _load_dataframe_from_group(f["samples"], schema, "samples_df", self.logger)
            else:
                # Initialize empty samples_df with the correct schema if no data exists
                self.logger.debug("No samples data found in study5 file. Initializing empty samples_df.")
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
            pbar.update(1)

            # Load features_df
            pbar.set_description(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading features")
            if "features" in f and len(f["features"].keys()) > 0:
                object_columns = ["chrom", "ms2_scans", "ms2_specs"]
                self.features_df = _load_dataframe_from_group(f["features"], schema, "features_df", self.logger, object_columns)
            else:
                self.features_df = None
            pbar.update(1)

            # Load consensus_df
            pbar.set_description(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading consensus")
            if "consensus" in f and len(f["consensus"].keys()) > 0:
                self.consensus_df = _load_dataframe_from_group(f["consensus"], schema, "consensus_df", self.logger)
            else:
                self.consensus_df = None
            pbar.update(1)

            # Load consensus_mapping_df
            pbar.set_description(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading consensus mapping")
            if "consensus_mapping" in f and len(f["consensus_mapping"].keys()) > 0:
                self.consensus_mapping_df = _load_dataframe_from_group(f["consensus_mapping"], schema, "consensus_mapping_df", self.logger)
            else:
                self.consensus_mapping_df = None
            pbar.update(1)

            # Load consensus_ms2
            pbar.set_description(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading consensus MS2")
            if "consensus_ms2" in f and len(f["consensus_ms2"].keys()) > 0:
                object_columns = ["spec"]
                self.consensus_ms2 = _load_dataframe_from_group(f["consensus_ms2"], schema, "consensus_ms2", self.logger, object_columns)
            else:
                self.consensus_ms2 = None
            pbar.update(1)

    self.logger.info(f"Study loaded from {filename}")


def _load_h5(self, filename=None):
    """
    Load Study instance data from a legacy .h5 HDF5 file with progress tracking.

    This is a legacy method for loading older HDF5 format files. For new files,
    use _load_study5() which has improved schema handling and performance.

    Args:
        filename (str, optional): Path to the .h5 HDF5 file to load. If None, uses default.

    Returns:
        None (modifies self in place)

    Notes:
        - Legacy format loader with basic DataFrame reconstruction
        - Includes progress bar for loading steps
        - For new projects, prefer _load_study5() method
    """
    from datetime import datetime
    from tqdm import tqdm
    
    # Handle default filename
    if filename is None:
        if self.default_folder is not None:
            filename = os.path.join(self.default_folder, "study.h5")
        else:
            self.logger.error("Either filename or default_folder must be provided")
            return

    # Add .h5 extension if not provided
    if not filename.endswith(".h5"):
        filename += ".h5"

    if not os.path.exists(filename):
        self.logger.error(f"File {filename} does not exist")
        return

    # Define loading steps for progress tracking
    loading_steps = [
        "metadata",
        "samples_df", 
        "features_df",
        "consensus_df",
        "consensus_mapping_df"
    ]
    
    # Check if progress bar should be disabled based on log level
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    with h5py.File(filename, "r") as f:
        # Use progress bar to show loading progress
        with tqdm(
            total=len(loading_steps),
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading legacy study",
            disable=tdqm_disable,
        ) as pbar:
            
            # Load metadata
            pbar.set_description(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading metadata")
            if "metadata" in f:
                metadata = f["metadata"]
                self.default_folder = _decode_bytes_attr(metadata.attrs.get("default_folder", ""))
                if hasattr(self, "label"):
                    self.label = _decode_bytes_attr(metadata.attrs.get("label", ""))

                # Load parameters from JSON if available
                if "parameters" in metadata:
                    try:
                        parameters_data = metadata["parameters"][()]
                        if isinstance(parameters_data, bytes):
                            parameters_data = parameters_data.decode("utf-8")

                        if parameters_data and parameters_data != "":
                            self.history = json.loads(parameters_data)
                        else:
                            self.history = {}
                    except (json.JSONDecodeError, ValueError, TypeError) as e:
                        self.logger.warning(f"Failed to deserialize parameters: {e}")
                        self.history = {}
                else:
                    self.history = {}
            pbar.update(1)

            # Load samples_df (legacy format)
            pbar.set_description(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading samples")
            if "samples" in f and len(f["samples"].keys()) > 0:
                samples_data = {}
                for col in f["samples"].keys():
                    column_data = f["samples"][col][:]
                    # Handle byte strings
                    if len(column_data) > 0 and isinstance(column_data[0], bytes):
                        column_data = [item.decode("utf-8") if isinstance(item, bytes) else item for item in column_data]
                    samples_data[col] = column_data
                
                if samples_data:
                    self.samples_df = pl.DataFrame(samples_data)
                else:
                    # Initialize empty samples_df
                    self.samples_df = pl.DataFrame({
                        "sample_uid": [],
                        "sample_name": [],
                        "sample_path": [],
                        "sample_type": [],
                        "size": [],
                        "map_id": [],
                    })
            else:
                self.samples_df = pl.DataFrame({
                    "sample_uid": [],
                    "sample_name": [],
                    "sample_path": [],
                    "sample_type": [],
                    "size": [],
                    "map_id": [],
                })
            pbar.update(1)

            # Load features_df (legacy format)
            pbar.set_description(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading features")
            if "features" in f and len(f["features"].keys()) > 0:
                features_data = {}
                for col in f["features"].keys():
                    column_data = f["features"][col][:]
                    # Handle special object columns
                    if col in ["chrom", "ms2_specs"]:
                        reconstructed_data = _reconstruct_object_column(column_data, col)
                        features_data[col] = reconstructed_data
                    else:
                        # Handle byte strings
                        if len(column_data) > 0 and isinstance(column_data[0], bytes):
                            column_data = [item.decode("utf-8") if isinstance(item, bytes) else item for item in column_data]
                        features_data[col] = column_data
                
                if features_data:
                    # Create DataFrame with Object columns handled properly
                    object_columns = ["chrom", "ms2_specs"]
                    self.features_df = _create_dataframe_with_objects(features_data, object_columns)
                else:
                    self.features_df = None
            else:
                self.features_df = None
            pbar.update(1)

            # Load consensus_df (legacy format)
            pbar.set_description(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading consensus")
            if "consensus" in f and len(f["consensus"].keys()) > 0:
                consensus_data = {}
                for col in f["consensus"].keys():
                    column_data = f["consensus"][col][:]
                    # Handle byte strings
                    if len(column_data) > 0 and isinstance(column_data[0], bytes):
                        column_data = [item.decode("utf-8") if isinstance(item, bytes) else item for item in column_data]
                    consensus_data[col] = column_data
                
                if consensus_data:
                    self.consensus_df = pl.DataFrame(consensus_data)
                else:
                    self.consensus_df = None
            else:
                self.consensus_df = None
            pbar.update(1)

            # Load consensus_mapping_df (legacy format)
            pbar.set_description(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading consensus mapping")
            if "consensus_mapping" in f and len(f["consensus_mapping"].keys()) > 0:
                mapping_data = {}
                for col in f["consensus_mapping"].keys():
                    column_data = f["consensus_mapping"][col][:]
                    mapping_data[col] = column_data
                
                if mapping_data:
                    self.consensus_mapping_df = pl.DataFrame(mapping_data)
                else:
                    self.consensus_mapping_df = None
            else:
                self.consensus_mapping_df = None
            pbar.update(1)

    self.logger.info(f"Legacy study loaded from {filename}")
