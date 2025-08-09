"""
Find Features Parameters Module

This module defines parameters for feature detection in mass spectrometry data.
It consolidates all parameters used in the find_features() method with type checking,
validation, and comprehensive descriptions.

Classes:
    find_features_defaults: Configuration parameters for the find_features() method.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class find_features_defaults:
    """
    Parameters for mass spectrometry feature detection using OpenMS algorithms.

    This class consolidates all parameters used in the find_features() method including
    mass trace detection (MTD), elution peak detection (EPD), and feature finding (FFM).
    It provides type checking, validation, and comprehensive parameter descriptions.

    Mass Trace Detection (MTD) Parameters:
        tol_ppm: Mass error tolerance in parts-per-million for mass trace detection.
        noise: Noise threshold intensity to filter out low-intensity signals.
        min_trace_length_multiplier: Multiplier for minimum trace length (multiplied by chrom_fwhm_min).
        trace_termination_outliers: Number of outliers allowed before terminating a trace.

    Elution Peak Detection (EPD) Parameters:
        chrom_fwhm: Full width at half maximum for chromatographic peak shape.
        chrom_fwhm_min: Minimum FWHM for chromatographic peak detection.
        chrom_peak_snr: Signal-to-noise ratio required for chromatographic peaks.
        masstrace_snr_filtering: Whether to apply SNR filtering to mass traces.
        mz_scoring_13C: Whether to enable scoring of 13C isotopic patterns.
        width_filtering: Width filtering method for mass traces.

    Feature Finding (FFM) Parameters:
        remove_single_traces: Whether to remove mass traces without satellite isotopic traces.
        report_convex_hulls: Whether to report convex hulls for features.
        report_summed_ints: Whether to report summed intensities.
        report_chromatograms: Whether to report chromatograms.

    Post-processing Parameters:
        deisotope: Whether to perform deisotoping of detected features.
        deisotope_mz_tol: m/z tolerance for deisotoping.
        deisotope_rt_tol_factor: RT tolerance factor for deisotoping (multiplied by chrom_fwhm_min/4).
        eic_mz_tol: m/z tolerance for EIC extraction.
        eic_rt_tol: RT tolerance for EIC extraction.

    Available Methods:
        - validate(param_name, value): Validate a single parameter value
        - validate_all(): Validate all parameters at once
        - to_dict(): Convert parameters to dictionary
        - set_from_dict(param_dict, validate=True): Update multiple parameters from dict
        - set(param_name, value, validate=True): Set parameter value with validation
        - get(param_name): Get parameter value
        - get_description(param_name): Get parameter description
        - get_info(param_name): Get full parameter metadata
        - list_parameters(): Get list of all parameter names
    """

    # Mass Trace Detection parameters
    tol_ppm: float = 30.0
    noise: float = 200.0
    min_trace_length_multiplier: float = 2.0
    trace_termination_outliers: int = 2

    # Elution Peak Detection parameters
    chrom_fwhm: float = 1.0
    chrom_fwhm_min: float = 0.5
    chrom_peak_snr: float = 10.0
    masstrace_snr_filtering: bool = False
    mz_scoring_13C: bool = False
    width_filtering: str = "fixed"

    # Feature Finding parameters
    remove_single_traces: bool = False
    report_convex_hulls: bool = True
    report_summed_ints: bool = False
    report_chromatograms: bool = True

    # Post-processing parameters
    deisotope: bool = True
    deisotope_mz_tol: float = 0.02
    deisotope_rt_tol_factor: float = 0.25  # Will be multiplied by chrom_fwhm_min/4
    eic_mz_tol: float = 0.01
    eic_rt_tol: float = 10.0

    # Parameter metadata for validation and description
    _param_metadata: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "tol_ppm": {
                "dtype": float,
                "description": "Mass error tolerance in parts-per-million for mass trace detection",
                "min_value": 0.1,
                "max_value": 100.0,
            },
            "noise": {
                "dtype": float,
                "description": "VIP: Noise threshold intensity to filter out low-intensity signals",
                "min_value": 0.0,
                "max_value": float("inf"),
            },
            "min_trace_length_multiplier": {
                "dtype": float,
                "description": "Multiplier for minimum trace length calculation (multiplied by chrom_fwhm_min)",
                "min_value": 1.0,
                "max_value": 10.0,
            },
            "trace_termination_outliers": {
                "dtype": int,
                "description": "Number of outliers allowed before terminating a mass trace",
                "min_value": 1,
                "max_value": 10,
            },
            "chrom_fwhm": {
                "dtype": float,
                "description": "VIP: Full width at half maximum for chromatographic peak shape in elution peak detection",
                "min_value": 0.1,
                "max_value": 30.0,
            },
            "chrom_fwhm_min": {
                "dtype": float,
                "description": "Minimum FWHM for chromatographic peak detection",
                "min_value": 0.1,
                "max_value": 5.0,
            },
            "chrom_peak_snr": {
                "dtype": float,
                "description": "VIP: Signal-to-noise ratio required for chromatographic peaks",
                "min_value": 1.0,
                "max_value": 100.0,
            },
            "masstrace_snr_filtering": {
                "dtype": bool,
                "description": "Whether to apply signal-to-noise filtering to mass traces",
            },
            "mz_scoring_13C": {
                "dtype": bool,
                "description": "Whether to enable scoring of 13C isotopic patterns during peak detection",
            },
            "width_filtering": {
                "dtype": str,
                "description": "Width filtering method for mass traces",
                "allowed_values": ["fixed", "auto"],
            },
            "remove_single_traces": {
                "dtype": bool,
                "description": "Whether to remove mass traces without satellite isotopic traces",
            },
            "report_convex_hulls": {
                "dtype": bool,
                "description": "Whether to report convex hulls for detected features",
            },
            "report_summed_ints": {
                "dtype": bool,
                "description": "Whether to report summed intensities for features",
            },
            "report_chromatograms": {
                "dtype": bool,
                "description": "Whether to report chromatograms for features",
            },
            "deisotope": {
                "dtype": bool,
                "description": "Whether to perform deisotoping of detected features to remove redundant isotope peaks",
            },
            "deisotope_mz_tol": {
                "dtype": float,
                "description": "m/z tolerance for deisotoping (Da)",
                "min_value": 0.001,
                "max_value": 0.1,
            },
            "deisotope_rt_tol_factor": {
                "dtype": float,
                "description": "RT tolerance factor for deisotoping (multiplied by chrom_fwhm_min/4)",
                "min_value": 0.1,
                "max_value": 2.0,
            },
            "eic_mz_tol": {
                "dtype": float,
                "description": "m/z tolerance for EIC extraction (Da)",
                "min_value": 0.001,
                "max_value": 0.1,
            },
            "eic_rt_tol": {
                "dtype": float,
                "description": "RT tolerance for EIC extraction (seconds)",
                "min_value": 1.0,
                "max_value": 60.0,
            },
        },
    )

    def get_info(self, param_name: str) -> dict[str, Any]:
        """
        Get information about a specific parameter.

        Args:
            param_name: Name of the parameter

        Returns:
            Dictionary containing parameter metadata

        Raises:
            KeyError: If parameter name is not found
        """
        if param_name not in self._param_metadata:
            raise KeyError(f"Parameter '{param_name}' not found")
        return self._param_metadata[param_name]

    def get_description(self, param_name: str) -> str:
        """
        Get description for a specific parameter.

        Args:
            param_name: Name of the parameter

        Returns:
            Parameter description string
        """
        return str(self.get_info(param_name)["description"])

    def validate(self, param_name: str, value: Any) -> bool:
        """
        Validate a parameter value against its constraints.

        Args:
            param_name: Name of the parameter
            value: Value to validate

        Returns:
            True if value is valid, False otherwise
        """
        if param_name not in self._param_metadata:
            return False

        metadata = self._param_metadata[param_name]
        expected_dtype = metadata["dtype"]

        # Check type
        if not isinstance(value, expected_dtype):
            try:
                # Try to convert to expected type
                value = expected_dtype(value)
            except (ValueError, TypeError):
                return False

        # Check range constraints for numeric types
        if expected_dtype in (int, float):
            if "min_value" in metadata and value < metadata["min_value"]:
                return False
            if "max_value" in metadata and value > metadata["max_value"]:
                return False

        # Check allowed values for strings
        if expected_dtype is str and "allowed_values" in metadata:
            if value not in metadata["allowed_values"]:
                return False

        return True

    def set(self, param_name: str, value: Any, validate: bool = True) -> bool:
        """
        Set a parameter value with optional validation.

        Args:
            param_name: Name of the parameter
            value: New value for the parameter
            validate: Whether to validate the value before setting

        Returns:
            True if parameter was set successfully, False otherwise
        """
        if not hasattr(self, param_name):
            return False

        if validate and not self.validate(param_name, value):
            return False

        # Convert to expected type if needed
        if param_name in self._param_metadata:
            expected_dtype = self._param_metadata[param_name]["dtype"]
            try:
                value = expected_dtype(value)
            except (ValueError, TypeError):
                if validate:
                    return False

        setattr(self, param_name, value)
        return True

    def get(self, param_name: str) -> Any:
        """
        Get the value of a parameter by name.
        Args:
            param_name: Name of the parameter
        Returns:
            Current value of the parameter
        """
        if not hasattr(self, param_name):
            raise KeyError(f"Parameter '{param_name}' not found")
        return getattr(self, param_name)

    def set_from_dict(
        self,
        param_dict: dict[str, Any],
        validate: bool = True,
    ) -> list[str]:
        """
        Update multiple parameters from a dictionary.

        Args:
            param_dict: Dictionary of parameter names and values
            validate: Whether to validate values before setting

        Returns:
            List of parameter names that could not be set
        """
        failed_params = []

        for param_name, value in param_dict.items():
            if not self.set(param_name, value, validate):
                failed_params.append(param_name)

        return failed_params

    def to_dict(self) -> dict[str, Any]:
        """
        Convert parameters to dictionary, excluding metadata.

        Returns:
            Dictionary of parameter names and values
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def list_parameters(self) -> list[str]:
        """
        Get list of all parameter names.

        Returns:
            List of parameter names
        """
        return [k for k in self.__dict__.keys() if not k.startswith("_")]

    def validate_all(self) -> tuple[bool, list[str]]:
        """
        Validate all parameters in the instance.

        Returns:
            Tuple of (all_valid, list_of_invalid_params)
            - all_valid: True if all parameters are valid, False otherwise
            - list_of_invalid_params: List of parameter names that failed validation
        """
        invalid_params = []

        for param_name in self.list_parameters():
            if param_name in self._param_metadata:
                current_value = getattr(self, param_name)
                if not self.validate(param_name, current_value):
                    invalid_params.append(param_name)

        return len(invalid_params) == 0, invalid_params
