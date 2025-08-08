from __future__ import annotations

from datetime import datetime
from typing import Any

import holoviews as hv
import numpy as np
import panel
import polars as pl

from bokeh.io.export import export_png
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.palettes import Turbo256
from bokeh.plotting import figure
from bokeh.plotting import output_file
from bokeh.plotting import show
from tqdm import tqdm

hv.extension("bokeh")


def plot_alignment(self, filename=None):
    import matplotlib.pyplot as plt
    import numpy as np

    if self.features_maps is None or len(self.features_maps) == 0:
        self.load_features()

    feature_maps = self.features_maps
    ref_index = self.alignment_ref_index
    if ref_index is None:
        self.logger.error("No alignment performed yet.")
        return

    fmaps = [
        feature_maps[ref_index],
        *feature_maps[:ref_index],
        *feature_maps[ref_index + 1 :],
    ]

    fig = plt.figure(figsize=(12, 6))

    ax = fig.add_subplot(1, 2, 1)
    ax.set_title("Feature maps before alignment")
    ax.set_ylabel("m/z")
    ax.set_xlabel("RT")

    # use alpha value to display feature intensity
    ax.scatter(
        [f.getRT() for f in fmaps[0]],
        [f.getMZ() for f in fmaps[0]],
        alpha=np.asarray([f.getIntensity() for f in fmaps[0]])
        / max([f.getIntensity() for f in fmaps[0]]),
        s=4,
    )

    for fm in fmaps[1:]:
        ax.scatter(
            [f.getMetaValue("original_RT") for f in fm],
            [f.getMZ() for f in fm],
            alpha=np.asarray([f.getIntensity() for f in fm])
            / max([f.getIntensity() for f in fm]),
            s=2,  # Set symbol size to 3
        )

    ax = fig.add_subplot(1, 2, 2)
    ax.set_title("Feature maps after alignment")
    ax.set_ylabel("m/z")
    ax.set_xlabel("RT")

    for fm in fmaps:
        ax.scatter(
            [f.getRT() for f in fm],
            [f.getMZ() for f in fm],
            alpha=np.asarray([f.getIntensity() for f in fm])
            / max([f.getIntensity() for f in fm]),
            s=2,  # Set symbol size to 3
        )

    fig.tight_layout()


def plot_alignment_bokeh(self, filename=None):
    from bokeh.plotting import figure, show, output_file
    from bokeh.layouts import gridplot

    feature_maps = self.features_maps
    ref_index = self.alignment_ref_index
    if ref_index is None:
        self.logger.warning("No alignment performed yet.")
        return

    fmaps = [
        feature_maps[ref_index],
        *feature_maps[:ref_index],
        *feature_maps[ref_index + 1 :],
    ]

    # Create Bokeh figures
    p1 = figure(
        title="Feature maps before alignment",
        width=600,
        height=400,
    )
    p1.xaxis.axis_label = "RT"
    p1.yaxis.axis_label = "m/z"
    p2 = figure(
        title="Feature maps after alignment",
        width=600,
        height=400,
    )
    p2.xaxis.axis_label = "RT"
    p2.yaxis.axis_label = "m/z"

    # Plot before alignment
    p1.scatter(
        x=[f.getRT() for f in fmaps[0]],
        y=[f.getMZ() for f in fmaps[0]],
        size=4,
        alpha=[
            f.getIntensity() / max([f.getIntensity() for f in fmaps[0]])
            for f in fmaps[0]
        ],
        color="blue",
    )

    for fm in fmaps[1:]:
        p1.scatter(
            x=[f.getMetaValue("original_RT") for f in fm],
            y=[f.getMZ() for f in fm],
            size=2,
            alpha=[f.getIntensity() / max([f.getIntensity() for f in fm]) for f in fm],
            color="green",
        )

    # Plot after alignment
    for fm in fmaps:
        p2.scatter(
            x=[f.getRT() for f in fm],
            y=[f.getMZ() for f in fm],
            size=2,
            alpha=[f.getIntensity() / max([f.getIntensity() for f in fm]) for f in fm],
            color="red",
        )

    # Arrange plots in a grid
    # Link the x_range and y_range of both plots for synchronized zooming/panning
    p2.x_range = p1.x_range
    p2.y_range = p1.y_range

    grid = gridplot([[p1, p2]])

    # Output to file and show
    if filename:
        output_file(filename)
    show(grid)


def plot_consensus_2d(
    self,
    filename=None,
    colorby="number_samples",
    sizeby="inty_mean",
    markersize=6,
    alpha=0.7,
    cmap=None,
):
    if self.consensus_df is None:
        self.logger.error("No consensus map found.")
        return
    data = self.consensus_df.clone()
    if colorby not in data.columns:
        self.logger.error(f"Column {colorby} not found in consensus_df.")
        return
    if sizeby not in data.columns:
        self.logger.warning(f"Column {sizeby} not found in consensus_df.")
        sizeby = None
    # if sizeby is not None, set markersize to sizeby
    if sizeby is not None:
        # set markersize to sizeby
        if sizeby in ["inty_mean"]:
            # use log10 of sizeby
            # Filter out empty or all-NA entries before applying np.log10
            data = data.with_columns([
                pl.when(
                    (pl.col(sizeby).is_not_null())
                    & (pl.col(sizeby).is_finite())
                    & (pl.col(sizeby) > 0),
                )
                .then((pl.col(sizeby).log10() * markersize / 12).pow(2))
                .otherwise(markersize)
                .alias("markersize"),
            ])
        else:
            max_size = data[sizeby].max()
            data = data.with_columns([
                (pl.col(sizeby) / max_size * markersize).alias("markersize"),
            ])
    else:
        data = data.with_columns([pl.lit(markersize).alias("markersize")])
    # sort by ascending colorby
    data = data.sort(colorby)
    # convert consensus_id to string - check if column exists
    if "consensus_id" in data.columns:
        # Handle Object dtype by converting to string first
        data = data.with_columns([
            pl.col("consensus_id")
            .map_elements(
                lambda x: str(x) if x is not None else None,
                return_dtype=pl.Utf8,
            )
            .alias("consensus_id"),
        ])
    elif "consensus_uid" in data.columns:
        data = data.with_columns([
            pl.col("consensus_uid").cast(pl.Utf8).alias("consensus_id"),
        ])

    if cmap is None:
        cmap = "vi"
    elif cmap == "grey":
        cmap = "Greys256"

    # plot with bokeh
    import bokeh.plotting as bp

    from bokeh.models import BasicTicker
    from bokeh.models import ColumnDataSource
    from bokeh.models import HoverTool
    from bokeh.models import LinearColorMapper
    try:
        from bokeh.models import ColorBar  # type: ignore[attr-defined]
    except ImportError:
        from bokeh.models.annotations import ColorBar
    from bokeh.palettes import viridis

    # Convert Polars DataFrame to pandas for Bokeh compatibility
    data_pd = data.to_pandas()
    source = ColumnDataSource(data_pd)
    color_mapper = LinearColorMapper(
        palette=viridis(256),
        low=data[colorby].min(),
        high=data[colorby].max(),
    )
    # scatter plot rt vs mz
    p = bp.figure(
        width=800,
        height=600,
        title="Consensus map",
    )
    p.xaxis.axis_label = "Retention Time (min)"
    p.yaxis.axis_label = "m/z"
    scatter_renderer = p.scatter(
        x="rt",
        y="mz",
        size="markersize",
        fill_color={"field": colorby, "transform": color_mapper},
        line_color=None,
        alpha=alpha,
        source=source,
    )
    # add hover tool
    hover = HoverTool(
        tooltips=[
            ("consensus_uid", "@consensus_uid"),
            ("consensus_id", "@consensus_id"),
            ("number_samples", "@number_samples"),
            ("number_ms2", "@number_ms2"),
            ("rt", "@rt"),
            ("mz", "@mz"),
            ("inty_mean", "@inty_mean"),
            ("iso_mean", "@iso_mean"),
            ("coherence_mean", "@chrom_coherence_mean"),
            ("prominence_mean", "@chrom_prominence_mean"),
        ],
        renderers=[scatter_renderer],
    )
    p.add_tools(hover)

    # add colorbar
    color_bar = ColorBar(
        color_mapper=color_mapper,
        label_standoff=12,
        location=(0, 0),
        title=colorby,
        ticker=BasicTicker(desired_num_ticks=8),
    )
    p.add_layout(color_bar, "right")

    if filename is not None:
        bp.output_file(filename)
    bp.show(p)
    return p


def plot_samples_2d(
    self,
    samples=None,
    filename=None,
    markersize=2,
    size="const",
    alpha_max=0.8,
    alpha="inty",
    cmap="Turbo256",
    max_features=50000,  # Reduced default for better performance with many samples
):
    """
    Plot all feature maps for sample_uid in parameter uids in an overlaid scatter plot.
    Each sample is a different color. Alpha scales with intensity.
    OPTIMIZED VERSION: Uses vectorized operations and batch processing.
    """

    sample_uids = self._get_sample_uids(samples)

    if not sample_uids:
        self.logger.error("No valid sample_uids provided.")
        return

    colors = Turbo256
    color_map = {
        uid: colors[i * (256 // max(1, len(sample_uids)))]
        for i, uid in enumerate(sample_uids)
    }

    p = figure(
        width=600,
        height=600,
        title="Sample Features",
    )
    p.xaxis.axis_label = "Retention Time (RT)"
    p.yaxis.axis_label = "m/z"

    # OPTIMIZATION 1: Batch filter all features for selected samples at once
    features_batch = self.features_df.filter(pl.col("sample_uid").is_in(sample_uids))

    if features_batch.is_empty():
        self.logger.error("No features found for the selected samples.")
        return

    # OPTIMIZATION 8: Fast sampling for very large datasets to maintain interactivity
    max_features_per_plot = max_features  # Limit for interactive performance
    total_features = len(features_batch)

    if total_features > max_features_per_plot:
        # OPTIMIZED: Much faster random sampling without groupby operations
        sample_ratio = max_features_per_plot / total_features
        self.logger.info(
            f"Large dataset detected ({total_features:,} features). "
            f"Sampling {sample_ratio:.1%} for visualization performance.",
        )

        # FAST: Use simple random sampling instead of expensive stratified sampling
        n_samples = min(max_features_per_plot, total_features)
        features_batch = features_batch.sample(n=n_samples, seed=42)

    # OPTIMIZATION 2: Join with samples_df to get sample names in one operation
    samples_info = self.samples_df.filter(pl.col("sample_uid").is_in(sample_uids))
    features_with_names = features_batch.join(
        samples_info.select(["sample_uid", "sample_name"]),
        on="sample_uid",
        how="left",
    )

    # OPTIMIZATION 4: Fast pre-calculation of alpha values for all features
    if alpha == "inty":
        # OPTIMIZED: Use efficient Polars operations instead of pandas groupby transform
        # Calculate max intensity per sample in Polars (much faster)
        max_inty_per_sample = features_with_names.group_by("sample_uid").agg(
            pl.col("inty").max().alias("max_inty"),
        )

        # Join back and calculate alpha efficiently
        features_batch = (
            features_with_names.join(
                max_inty_per_sample,
                on="sample_uid",
                how="left",
            )
            .with_columns(
                (pl.col("inty") / pl.col("max_inty") * alpha_max).alias("alpha"),
            )
            .drop("max_inty")
        )

        # Convert to pandas once after all Polars operations
        features_pd = features_batch.to_pandas()
    else:
        # Convert to pandas and add constant alpha
        features_pd = features_with_names.to_pandas()
        features_pd["alpha"] = alpha_max

    # OPTIMIZATION 9: NEW - Batch create all ColumnDataSources at once
    # Group all data by sample_uid and create sources efficiently
    sources = {}
    renderers: list[Any] = []

    # Pre-compute color mapping to avoid repeated lookups
    color_values = {}
    sample_names = {}

    for uid in sample_uids:
        sample_data = features_pd[features_pd["sample_uid"] == uid]
        if sample_data.empty:
            continue

        sample_name = sample_data["sample_name"].iloc[0]
        sample_names[uid] = sample_name
        color_values[uid] = color_map[uid]

    # OPTIMIZATION 10: Batch renderer creation with pre-computed values
    for uid in sample_uids:
        sample_data = features_pd[features_pd["sample_uid"] == uid]
        if sample_data.empty:
            continue

        sample_name = sample_names[uid]
        color_values[uid]

        # OPTIMIZATION 11: Direct numpy array access for better performance
        source = ColumnDataSource(
            data={
                "rt": sample_data["rt"].values,
                "mz": sample_data["mz"].values,
                "inty": sample_data["inty"].values,
                "alpha": sample_data["alpha"].values,
                "sample": np.full(len(sample_data), sample_name, dtype=object),
            },
        )

        sources[uid] = source

        # OPTIMIZATION 12: Use pre-computed color value
        # Create renderer with pre-computed values  
        renderer: Any
        if size.lower() in ["dyn", "dynamic"]:
            renderer = p.circle(
                x="rt",
                y="mz",
                radius=markersize / 10,
                color=color_values[uid],
                alpha="alpha",
                legend_label=sample_name,
                source=source,
            )
        else:
            renderer = p.scatter(
                x="rt",
                y="mz",
                size=markersize,
                color=color_values[uid],
                alpha="alpha",
                legend_label=sample_name,
                source=source,
            )
        renderers.append(renderer)

    # OPTIMIZATION 13: Simplified hover tool for better performance with many samples
    if renderers:
        hover = HoverTool(
            tooltips=[
                ("sample", "@sample"),
                ("rt", "@rt{0.00}"),
                ("mz", "@mz{0.0000}"),
                ("intensity", "@inty{0.0e+0}"),
            ],
            renderers=renderers,
        )
        p.add_tools(hover)

    # Remove legend from plot
    p.legend.visible = False
    if filename:
        if filename.endswith(".html"):
            output_file(filename)
            show(p)
        elif filename.endswith(".png"):
            export_png(p, filename=filename)
        else:
            output_file(filename)
            show(p)
    else:
        show(p)
    return


def plot_chrom(
    self,
    uids=None,
    samples=None,
    filename=None,
    aligned=True,
    width=800,
    height=300,
):
    cons_uids = self._get_consensus_uids(uids)
    sample_uids = self._get_sample_uids(samples)

    chroms = self.get_chrom(uids=cons_uids, samples=sample_uids)

    if chroms is None or chroms.is_empty():
        self.logger.error("No chromatogram data found.")
        return

    # Assign a fixed color to each sample/column
    sample_names = [col for col in chroms.columns if col not in ["consensus_uid"]]
    if not sample_names:
        self.logger.error("No sample names found in chromatogram data.")
        return
    color_map = {
        sample: Turbo256[i * (256 // max(1, len(sample_names)))]
        for i, sample in enumerate(sample_names)
    }

    plots = []
    self.logger.info(f"Plotting {chroms.shape[0]} chromatograms...")
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for row in tqdm(
        chroms.iter_rows(named=True),
        total=chroms.shape[0],
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Plot chromatograms",
        disable=tdqm_disable,
    ):
        consensus_uid = row["consensus_uid"]  # Get consensus_uid from the row
        consensus_id = consensus_uid  # Use the same value for consensus_id
        curves = []
        rt_min = np.inf
        rt_max = 0
        for sample in sample_names:
            chrom = row[sample]
            if chrom is not None:
                # check if chrom is nan
                if isinstance(chrom, float) and np.isnan(chrom):
                    continue

                chrom = chrom.to_dict()
                rt = chrom["rt"].copy()
                if len(rt) == 0:
                    continue
                if aligned and "rt_shift" in chrom:
                    rt_shift = chrom["rt_shift"]
                    if rt_shift is not None:
                        # Convert to numpy array if it's a list, then add scalar
                        if isinstance(rt, list):
                            rt = np.array(rt)
                        rt = rt + rt_shift  # Add scalar to array

                # update rt_min and rt_max
                if rt[0] < rt_min:
                    rt_min = rt[0]
                if rt[-1] > rt_max:
                    rt_max = rt[-1]

                inty = chrom["inty"]

                # Convert both rt and inty to numpy arrays if they're lists
                if isinstance(rt, list):
                    rt = np.array(rt)
                if isinstance(inty, list):
                    inty = np.array(inty)

                # Ensure both rt and inty are arrays and have the same length and are not empty
                if rt.size > 0 and inty.size > 0 and rt.shape == inty.shape:
                    # sort rt and inty by rt
                    sorted_indices = np.argsort(rt)
                    rt = rt[sorted_indices]
                    inty = inty[sorted_indices]
                    curve = hv.Curve((rt, inty), kdims=["RT"], vdims=["inty"]).opts(
                        color=color_map[sample],
                        line_width=1,
                    )
                    curves.append(curve)

                    if "feature_start" in chrom and "feature_end" in chrom:
                        # Add vertical lines for feature start and end
                        feature_start = chrom["feature_start"]
                        feature_end = chrom["feature_end"]
                        if aligned and "rt_shift" in chrom:
                            rt_shift = chrom["rt_shift"]
                            if rt_shift is not None:
                                feature_start += rt_shift
                                feature_end += rt_shift
                        if feature_start < rt_min:
                            rt_min = feature_start
                        if feature_end > rt_max:
                            rt_max = feature_end
                        # Add vertical lines to the curves
                        curves.append(
                            hv.VLine(feature_start).opts(
                                color=color_map[sample],
                                line_dash="dotted",
                                line_width=1,
                            ),
                        )
                        curves.append(
                            hv.VLine(feature_end).opts(
                                color=color_map[sample],
                                line_dash="dotted",
                                line_width=1,
                            ),
                        )
        if curves:
            # find row in consensus_df with consensus_id
            consensus_row = self.consensus_df.filter(
                pl.col("consensus_uid") == consensus_id,
            )
            rt_start_mean = consensus_row["rt_start_mean"][0]
            rt_end_mean = consensus_row["rt_end_mean"][0]
            # Add vertical lines to overlay
            curves.append(hv.VLine(rt_start_mean).opts(color="black", line_width=2))
            curves.append(hv.VLine(rt_end_mean).opts(color="black", line_width=2))

            overlay = hv.Overlay(curves).opts(
                height=height,
                width=width,
                title=f"Consensus UID: {consensus_id}, mz: {consensus_row['mz'][0]:.4f}, rt: {consensus_row['rt'][0]:.2f}{' (aligned)' if aligned else ''}",
                xlim=(rt_min, rt_max),
                shared_axes=False,
            )
            plots.append(overlay)

    if not plots:
        self.logger.warning("No valid chromatogram curves to plot.")
        return

    # stack vertically.
    # Stack all plots vertically in a Panel column
    layout = panel.Column(*[panel.panel(plot) for plot in plots])
    if filename is not None:
        if filename.endswith(".html"):
            panel.panel(layout).save(filename, embed=True)  # type: ignore[attr-defined]
        else:
            # Save as PNG using Panel's export_png if filename ends with .png
            if filename.endswith(".png"):
                from panel.io.save import save_png

                # Convert Holoviews overlays to Bokeh models before saving
                bokeh_layout = panel.panel(layout).get_root()  # type: ignore[attr-defined]
                save_png(bokeh_layout, filename=filename)
            else:
                panel.panel(layout).save(filename, embed=True)  # type: ignore[attr-defined]
    else:
        # In a server context, return the panel object instead of showing or saving directly
        # return panel.panel(layout)
        panel.panel(layout).show()
