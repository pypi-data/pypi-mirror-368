# MASSter

**MASSter** is a comprehensive Python package for mass spectrometry data analysis, designed for metabolomics and LC-MS data processing. It provides tools for feature detection, alignment, consensus building, and interactive visualization of mass spectrometry datasets. It is designed to deal with DDA, and hides functionalities for DIA and ZTScan DIA data. 

Most core processing functions are derived from OpenMS. We use the same nomenclature and refer to their documentation for an explanation of the parameters. To a large extent, however, you should be able to use the defaults (=no parameters) when calling processing steps.

This is a poorly documented, stable branch of the development codebase in use in the Zamboni lab. Novel functionalities will be added based on need and requests.

## Installation

```bash
pip install masster
```

### Basic Workflow for analyzing LC-MS study with 2-... samples

```python
import masster

# Initialize the Study object with the default folder
study = masster.Study(default_folder=r'D:\...\mylcms')

# Load data from folder with raw data, here: WIFF
study.add_folder(r'D:\...\...\...\*.wiff')

# Align maps
study.align(rt_max_diff=2.0)

# Find consensus features
study.find_consensus(min_samples=3)

# Retrieve missing data for quantification
study.fill_chrom(abs_)

# Integrate according to consensus metadata
study.integrate_chrom()

# link MS2 across the whole study and export them
study.find_ms2()
study.export_mgf()

# Save the study to .study5
study.save()
```

## Requirements

- Python ≥ 3.11
- Key dependencies: pandas, polars, numpy, scipy, matplotlib, bokeh, holoviews, panel
- See `pyproject.toml` for complete dependency list

## License

GNU Affero General Public License v3

## Citation

If you use Masster in your research, please cite this repository.
