"""
Report Formatting
"""
import importlib.resources
import os
from dataclasses import field
from datetime import datetime
from functools import cached_property
from importlib.metadata import version
from io import BytesIO
from io import StringIO
from typing import Any

import dacite
import matplotlib.dates as mdates
import numpy as np
import packaging
import pandas
import seaborn as sns
from cycler import cycler
from matplotlib import pyplot as plt
from matplotlib import rc
from matplotlib import rcdefaults
from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import _Edge_integer  # noqa
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import scale_range  # noqa
from natsort import natsorted
from pydantic import field_validator
from pydantic.dataclasses import dataclass as validating_dataclass
from pydantic_core.core_schema import ValidationInfo
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable
from reportlab.platypus import Image
from reportlab.platypus import KeepTogether
from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.platypus.tableofcontents import TableOfContents


def nso_raw_ticks(self, vmin, vmax):
    """
    This overrides the `MaxNLocator._raw_ticks` method in matplotlib, which has a bug.
    The bug was introduced in matplotlib 3.8.0 and resolved in matplotlib 3.9.1.
    Bug details:   https://github.com/matplotlib/matplotlib/issues/27603
    """
    if self._nbins == "auto":
        if self.axis is not None:
            nbins = np.clip(self.axis.get_tick_space(), max(1, self._min_n_ticks - 1), 9)
        else:
            nbins = 9
    else:
        nbins = self._nbins

    scale, offset = scale_range(vmin, vmax, nbins)
    _vmin = vmin - offset
    _vmax = vmax - offset
    steps = self._extended_steps * scale
    if self._integer:
        # For steps > 1, keep only integer values.
        igood = (steps < 1) | (np.abs(steps - np.round(steps)) < 0.001)
        steps = steps[igood]

    raw_step = (_vmax - _vmin) / nbins
    large_steps = steps >= raw_step

    # This is the source of the matplotlib error
    # If all large_steps are False, then
    #  `np.nonzero(large_steps)[0][0]` results in `IndexError: index 0 is out of bounds for axis 0 with size 0`
    if rcParams["axes.autolimit_mode"] == "round_numbers":
        # Classic round_numbers mode may require a larger step.
        # Get first multiple of steps that are <= _vmin
        floored_vmins = (_vmin // steps) * steps
        floored_vmaxs = floored_vmins + steps * nbins
        large_steps = large_steps & (floored_vmaxs >= _vmax)

    # Find index of smallest large step
    # istep = np.nonzero(large_steps)[0][0]

    # This is the temporary fix
    if any(large_steps):
        istep = np.nonzero(large_steps)[0][0]
    else:
        istep = len(steps) - 1

    # Start at smallest of the steps greater than the raw step, and check
    # if it provides enough ticks. If not, work backwards through
    # smaller steps until one is found that provides enough ticks.
    for step in steps[: istep + 1][::-1]:

        if self._integer and np.floor(_vmax) - np.ceil(_vmin) >= self._min_n_ticks - 1:
            step = max(1, step)
        best_vmin = (_vmin // step) * step

        # Find tick locations spanning the vmin-vmax range, taking into
        # account degradation of precision when there is a large offset.
        # The edge ticks beyond vmin and/or vmax are needed for the
        # "round_numbers" autolimit mode.
        edge = _Edge_integer(step, offset)
        low = edge.le(_vmin - best_vmin)
        high = edge.ge(_vmax - best_vmin)
        ticks = np.arange(low, high + 1) * step + best_vmin
        # Count only the ticks that will be displayed.
        nticks = ((ticks <= _vmax) & (ticks >= _vmin)).sum()
        if nticks >= self._min_n_ticks:
            break
    return ticks + offset


version_loaded = packaging.version.parse(version("matplotlib"))
version_380 = packaging.version.parse("3.8.0")
version_390 = packaging.version.parse("3.9.0")
if version_380 <= version_loaded <= version_390:
    MaxNLocator._raw_ticks = nso_raw_ticks


class ReportFormattingException(Exception):
    """
    Error formatting the quality report data into the expected template
    """


"""
Reusable Style Elements
Can see example styles here reportlab.lib.styles.getSampleStyleSheet()
"""


class ConditionalSpacer(Spacer):
    def wrap(self, availWidth, availHeight):
        height = min(self.height, availHeight - 1e-8)
        return availWidth, height


# Default size for a spacer i.e. how to vertically space out  elements
spacer = ConditionalSpacer(1, 10)

# Register official DKIST fonts
font_dir = importlib.resources.files("dkist_quality") / "fonts"
with importlib.resources.as_file(font_dir) as font_path:
    pdfmetrics.registerFont(TTFont("Oswald-Bold", os.path.join(font_path, "Oswald-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Oswald-Regular", os.path.join(font_path, "Oswald-Regular.ttf")))

style_normal = ParagraphStyle(
    name="Normal", fontSize=10, leading=12, textColor=colors.black, fontName="Times-Roman"
)
style_bold = ParagraphStyle(name="Bold", parent=style_normal, fontName="Times-Bold")
style_warn = ParagraphStyle(
    name="Warning",
    parent=style_normal,
    fontSize=8,
    leading=12,
    textColor=colors.red,
    fontName="Courier",
)
style_title = ParagraphStyle(
    name="Title",
    parent=style_normal,
    fontSize=20,
    leading=22,
    alignment=1,  # Top Align Center
    spaceAfter=6,
    fontName="Oswald-Bold",
)
style_subtitle = ParagraphStyle(
    name="SubTitle", parent=style_title, fontSize=10, fontName="Oswald-Regular"
)
style_heading = ParagraphStyle(
    name="Heading1",
    parent=style_normal,
    fontSize=14,
    leading=18,
    spaceBefore=16,
    spaceAfter=6,
    fontName="Oswald-Regular",
)
style_toc_entry = ParagraphStyle(
    name="TOC entry",
    fontName="Oswald-Regular",
    fontSize=10,
    leading=20,
    spaceAfter=0,
    spaceBefore=0,
    firstLineIndent=0,
    leftIndent=20,
)

# Syntax here is weird, but well documented in the API doc
# Summary: it's a list of formatting command tuples, each with the format:
#  (COMMAND, (start_cell_x, start_cell_y), (end_cell_x, end_cell_y), argument)
#
#  So (TOPPADDING, (0, 0), (-1, -1), 0) means give all cells ([0:-1] in both x and y) a
#   top padding value of 0.
table_style_toc = TableStyle(
    [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]
)

"""
Quality Report Schema
"""


@validating_dataclass
class Plot2D:
    xlabel: str
    ylabel: str
    ylabel_horizontal: bool | None
    # Need to use `dataclasses.field` b/c `dacite` doesn't like `pydantic.Field`
    series_data: dict[str, list[list[Any]]] = field(default_factory=dict)
    plot_kwargs: dict[str, dict[str, Any]] = field(default_factory=dict)
    series_name: str | None = None
    ylim: tuple[float, float] | None = None
    sort_series: bool = True

    @property
    def is_multi_series(self):
        return len(self.series_data) > 1

    @property
    def x_axis_is_time(self):
        if not self.series_data:
            return False
        x_value = list(self.series_data.values())[0][0][0]
        return isinstance(x_value, datetime)


@validating_dataclass
class VerticalMultiPanePlot2D:
    top_to_bottom_plot_list: list[Plot2D]
    match_x_axes: bool = True
    no_gap: bool = True
    top_to_bottom_height_ratios: list[float] | None = None

    @field_validator("top_to_bottom_height_ratios")
    @classmethod
    def ensure_same_number_of_height_ratios_and_plots(
        cls, height_ratios: list[float] | None, info: ValidationInfo
    ) -> list[float]:
        """
        Make sure that the number of height ratios is the same as the number of plots.

        Also populates default, same-size ratios if no ratios were given.
        """
        try:
            plot_list = info.data["top_to_bottom_plot_list"]
        except KeyError:
            # The plot list didn't validate for some reason. We're about to error anyway.
            return [1.0]

        num_plots = len(plot_list)
        if height_ratios is None:
            return [1.0] * num_plots

        if len(height_ratios) != num_plots:
            raise ValueError(
                f"The number of items in `top_to_bottom_height_ratios` list ({len(height_ratios)}) is not "
                f"the same as the number of plots ({num_plots})"
            )

        return height_ratios


@validating_dataclass
class PlotHistogram:
    xlabel: str
    series_data: dict[str, list[float]]
    series_name: str | None = None
    vertical_lines: dict[str, float] | None = None

    @property
    def is_multi_series(self):
        return len(self.series_data) > 1


@validating_dataclass
class PlotModulationMatrices:
    modmat_list: list[list[list[float]]]


@validating_dataclass
class PlotRaincloud:
    xlabel: str
    ylabel: str
    categorical_column_name: str
    distribution_column_name: str
    hue_column_name: str | None
    ylabel_horizontal: bool | None
    dataframe_json: str


@validating_dataclass
class PlotModulationEfficiency:
    efficiency_list: list[list[float]]


@validating_dataclass
class SimpleTable:
    rows: list[list[Any]]
    header_row: bool = True
    header_column: bool = False


@validating_dataclass
class ReportMetric:
    """
    A Quality Report is made up of a list of metrics with the schema defined by this class.
      Additionally, this class can produce a Flowable or List of Flowables to be rendered
      in the PDF Report
    """

    name: str
    description: str
    statement: str | list[str] | None = None
    plot_data: Plot2D | list[Plot2D] | None = None
    multi_plot_data: VerticalMultiPanePlot2D | None = None
    table_data: SimpleTable | list[SimpleTable] | None = None
    histogram_data: PlotHistogram | list[PlotHistogram] | None = None
    modmat_data: PlotModulationMatrices | None = None
    raincloud_data: PlotRaincloud | None = None
    efficiency_data: PlotModulationEfficiency | None = None
    warnings: list[str] | None = None

    def generate_flowables(self, register_with_toc: bool = True) -> KeepTogether:
        """
        Instance metadata transformed to flowables
        """
        elements = [
            LinkingHeading(f"{self.name}", register_with_toc=register_with_toc),
            Paragraph(f"{self.description}", style_normal),
        ]
        if self.statement:
            elements.append(self.make_statement())
        if self.table_data:
            elements.append(self.make_table())
        if self.plot_data:
            elements.append(self.make_simple_plot())
        if self.multi_plot_data:
            elements.append(self.make_vertical_multi_pane_plot())
        if self.modmat_data:
            elements.append(self.make_modulation_matrices_histograms())
        if self.raincloud_data:
            elements.append(self.make_raincloud_plot())
        if self.histogram_data:
            elements.append(self.make_histogram())
        if self.efficiency_data:
            elements.append(self.make_efficiency_plot())
        if self.warnings:
            elements += [
                Paragraph(
                    f"{w}",
                    style_warn,
                )
                for w in self.warnings
            ]
        return KeepTogether(self.join_flowables(*elements))

    def make_statement(self) -> list[Flowable]:
        """
        Format metric statement(s)
        """
        statement_list = self.statement
        if isinstance(statement_list, str):
            statement_list = [statement_list]

        elements_list = []
        for statement in statement_list:
            elements_list.append(spacer)
            elements_list.append(Paragraph(f"{statement}", style_bold))

        return elements_list

    def make_table(self) -> list[Flowable]:
        """
        Format a table data and Table flowable
        """
        dkist_blue = colors.HexColor(0x1E317A)
        dkist_orange = colors.HexColor(0xFAA61C)

        table_list = self.table_data
        if isinstance(table_list, SimpleTable):
            table_list = [table_list]

        elements_list = []
        for table_data in table_list:
            table = Table(
                table_data.rows,
            )
            if table_data.header_row:
                row_width = len(table_data.rows[0])
                table.setStyle(
                    [
                        ("BACKGROUND", (0, 0), (row_width, 0), dkist_blue),
                        ("TEXTCOLOR", (0, 0), (row_width, 0), dkist_orange),
                    ]
                )
            if table_data.header_column:
                col_height = len(table_data.rows)
                table.setStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, col_height), dkist_blue),
                        ("TEXTCOLOR", (0, 0), (0, col_height), dkist_orange),
                    ]
                )
            elements_list += [spacer, table, spacer]
        return elements_list

    def make_simple_plot(self) -> list[Flowable]:
        """
        Format plot data as an Image flowable depicting a line plot of the data
        """
        self.setup_plot_style()

        plot_list = self.plot_data
        if isinstance(plot_list, Plot2D):
            plot_list = [plot_list]

        elements_list = []
        for plot_data in plot_list:
            # Set up the axis and figure objects
            fig, ax = plt.subplots()

            self._fill_single_ax(
                ax=ax,
                fig=fig,
                plot_data=plot_data,
            )

            ## More formatting again
            self.format_plot(ax)

            # Save
            image_flowable = self.save_fig_object(fig)
            elements_list += [spacer, image_flowable, spacer]

        return elements_list

    def make_vertical_multi_pane_plot(self) -> list[Flowable]:
        """Construct a collection of plots that are in the same figure and stacked vertically."""
        self.setup_plot_style()

        plots = self.multi_plot_data
        num_plots = len(plots.top_to_bottom_plot_list)
        fig = plt.figure()

        normed_by_min_heights = [
            i / min(plots.top_to_bottom_height_ratios) for i in plots.top_to_bottom_height_ratios
        ]
        if plots.no_gap:
            fig.subplots_adjust(hspace=0.05)
            # Give each subplot an extra 10% in height
            new_fig_height = self.default_fig_height_in * (1 + sum(normed_by_min_heights) * 0.1)
        else:
            fig.subplots_adjust(hspace=0.6)
            # Give each subplot an extra 5% in height and add in the horizontal space between the two panes
            new_fig_height = (
                self.default_fig_height_in * (1 + sum(normed_by_min_heights) * 0.05) + 0.5
            )

        # Report lab doesn't like flowables taller than 9 inches
        new_fig_height = min(new_fig_height, 9)
        ax_list = fig.subplots(
            nrows=num_plots,
            sharex=plots.match_x_axes,
            height_ratios=plots.top_to_bottom_height_ratios,
        )

        any_ax_have_legend = any([pd.is_multi_series for pd in plots.top_to_bottom_plot_list])

        for i, (plot_data, ax) in enumerate(zip(plots.top_to_bottom_plot_list, ax_list)):
            self._fill_single_ax(
                ax=ax,
                fig=fig,
                plot_data=plot_data,
            )

            if any_ax_have_legend and not plot_data.is_multi_series:
                # If the other panes are going to be adjusted to make room for their legends then adjust
                # panes without legends to match.
                box = ax.get_position()
                legend_frac = self.default_fig_width_in / (
                    self.default_fig_width_in + self.default_legend_width_in
                )
                ax.set_position([box.x0, box.y0, box.width * legend_frac, box.height])

            # Don't pad the xlims if we're sharing the X axis because the padding will keep compounding
            self.format_plot(ax, pad_x_lims=not plots.match_x_axes)

            if plots.match_x_axes and i < num_plots - 1:
                ax.tick_params(axis="x", labelbottom=False)
                ax.set_xlabel("")

        if plots.match_x_axes:
            # A single pad now on the last axis will pad all panes by the same amount
            self.format_plot(ax, pad_x_lims=True)

        # Move any scientific notation offset text that would overlap with the plot above down inside its own plot
        for i, ax in enumerate(ax_list):
            # Need to draw so the actual offset text gets populated
            ax.figure.canvas.draw()
            offset_text = ax.yaxis.get_offset_text()
            if i > 0 and plots.no_gap and offset_text.get_text():
                ax.yaxis.offsetText.set_visible(False)
                ax.text(
                    ax.get_xlim()[0],
                    ax.get_ylim()[1],
                    f"  {offset_text.get_text()}",
                    ha="left",
                    va="top",
                    fontsize=offset_text.get_fontsize(),
                )

        # For some reason we need to reset the size here at the end or it doesn't work
        fig.set_figheight(new_fig_height)
        image_flowable = self.save_fig_object(fig)
        elements_list = [spacer, image_flowable, spacer]

        return elements_list

    def _fill_single_ax(
        self,
        *,
        ax: Axes,
        fig: Figure,
        plot_data: Plot2D,
    ) -> None:
        """Fill a single `Axes` instance with data in a given `Plot2D` object"""
        series_data = plot_data.series_data.items()
        if plot_data.sort_series:
            series_data = natsorted(series_data)
        for k, v in series_data:
            plot_kwargs = self.default_plot_kwargs | plot_data.plot_kwargs.get(k, dict())

            # `plot` used because `scatter` does not interact with the cycler in a nice way
            l = ax.plot(v[0], v[1], label=k, **plot_kwargs)[0]

            # Set y limits if provided
            if plot_data.ylim is not None:
                ymin, ymax = plot_data.ylim
                ax.set_ylim(ymin=ymin, ymax=ymax)
                self.draw_arrows_out_of_range(ax, v[0], v[1])

            if plot_data.is_multi_series and (
                plot_kwargs.get("ls") == "none" or plot_kwargs.get("linestyle") == "none"
            ):
                # Plot a faint line to guide the eye
                ax.plot(
                    v[0],
                    v[1],
                    linestyle="-",
                    color=l.get_color(),
                    alpha=self.default_connecting_line_alpha,
                )
        if plot_data.is_multi_series:
            fig.set_size_inches(
                self.default_fig_width_in + self.default_legend_width_in, self.default_fig_height_in
            )
            box = ax.get_position()
            legend_frac = self.default_fig_width_in / (
                self.default_fig_width_in + self.default_legend_width_in
            )
            ax.set_position([box.x0, box.y0, box.width * legend_frac, box.height])
            ax.legend(
                loc="upper left",
                bbox_to_anchor=(1, 1),
                title=plot_data.series_name,
            )
        # Time axis labels need special handling
        if plot_data.x_axis_is_time:
            locator = mdates.AutoDateLocator()
            formatter = mdates.ConciseDateFormatter(locator)
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)
        ax.set_xlabel(plot_data.xlabel)
        ax.set_ylabel(plot_data.ylabel, rotation=0 if plot_data.ylabel_horizontal else 90)

    def make_histogram(self) -> list[Flowable]:
        """Construct a simple histogram.

        Multiple series are overlapped and vertical lines are supported.
        """
        self.setup_plot_style()

        histogram_list = self.histogram_data
        if isinstance(histogram_list, PlotHistogram):
            histogram_list = [histogram_list]

        element_list = []
        for histogram_data in histogram_list:
            # Set up the axis and figure objects
            fig, ax = plt.subplots()

            for k, v in natsorted(histogram_data.series_data.items()):
                ax.hist(v, bins="auto", alpha=0.6, label=k, edgecolor="none")

            if histogram_data.vertical_lines:
                ax.set_prop_cycle(None)  # Reset cylcer
                ymax = ax.get_ylim()[1]
                for label, val in histogram_data.vertical_lines.items():
                    ax.axvline(val, ls=":", alpha=0.5)
                    ax.text(val, ymax * 1.07, label, ha="center", va="bottom")

            if histogram_data.is_multi_series:
                fig.set_size_inches(
                    self.default_fig_width_in + self.default_legend_width_in,
                    self.default_fig_height_in,
                )
                box = ax.get_position()
                legend_frac = self.default_fig_width_in / (
                    self.default_fig_width_in + self.default_legend_width_in
                )
                ax.set_position([box.x0, box.y0, box.width * legend_frac, box.height])
                ax.legend(
                    loc="upper left",
                    bbox_to_anchor=(1, 1),
                    title=histogram_data.series_name,
                )

            ax.set_xlabel(histogram_data.xlabel)
            ax.set_ylabel("N")

            self.format_plot(ax, pad_y_lims=False)

            image_flowable = self.save_fig_object(fig)
            element_list += [spacer, image_flowable, spacer]

        return element_list

    def make_modulation_matrices_histograms(self) -> list[Flowable]:
        """Construct a grid of histograms that show the distribution of each modulation matrix element."""
        self.setup_plot_style()

        # Turn off minor ticks to avoid clutter
        rc("xtick.minor", visible=False)
        rc("ytick.minor", visible=False)

        grid_alpha = 0.2
        grid_hex_str = "#" + hex(int(255 * (1 - grid_alpha)))[-2:] * 3

        data_array = np.array(self.modmat_data.modmat_list)
        num_mod = data_array.shape[0]

        # Set up the axis and figure objects
        fig, axs = plt.subplots(nrows=num_mod, ncols=4)
        fig.set_size_inches(
            self.default_fig_width_in, self.default_fig_height_in * 2.8
        )  # Just barely fit on a page with the metric description

        # Plot histogram for each modulation matrix element
        stokes_labels = ["I", "Q", "U", "V"]
        for stokes in range(4):
            for mod in range(num_mod):
                ax = axs[mod, stokes]
                # Put stokes labels along top row
                if mod == 0:
                    ax.text(
                        0.5,
                        1.5,
                        stokes_labels[stokes],
                        ha="center",
                        va="bottom",
                        transform=ax.transAxes,
                    )

                # Put modulation state labels down right side
                if stokes == 3:
                    ax.text(1.4, 0.5, mod + 1, ha="left", va="center", transform=ax.transAxes)

                # Don't plot OI
                if stokes == mod == 0:
                    ax.axis("off")
                    continue

                # Actually plot the data
                ax.hist(data_array[mod, stokes], bins="sqrt", alpha=1, edgecolor="none")

                # Put only 2 ticks on each axis to avoid clutter
                ax.yaxis.set_major_locator(MaxNLocator(1))
                ax.xaxis.set_major_locator(MaxNLocator(1))

                # Reduce opacity of box and ticks to reduce clutter
                ax.spines["bottom"].set_color(grid_hex_str)
                ax.spines["left"].set_color(grid_hex_str)
                ax.tick_params(colors=grid_hex_str)

                self.format_plot(ax, pad_y_lims=False)

                ax.set_ylim(0, ax.get_ylim()[1])

        fig.subplots_adjust(hspace=0.9, wspace=0.3)

        # Common axes with all lines/ticks turned off to be used for labels
        label_ax = fig.add_subplot(111)
        label_ax.set_facecolor([0, 0, 0, 0])  # Transparent
        label_ax.spines["top"].set_color("none")
        label_ax.spines["bottom"].set_color("none")
        label_ax.spines["left"].set_color("none")
        label_ax.spines["right"].set_color("none")
        label_ax.tick_params(
            labelcolor="none", which="both", top=False, bottom=False, left=False, right=False
        )

        label_ax.set_xlabel("Modulation Matrix Element")
        label_ax.set_ylabel("N")

        image_flowable = self.save_fig_object(fig)
        return [spacer, image_flowable, spacer]

    def make_raincloud_plot(self) -> list[Flowable]:
        """Make a wild plot showing KDE's of the fit residuals for each CS step.

        Also show the actual points to highlight the contribution from each modstate.
        KDE = Kernel Density Estimation; kind of like a histogram
        """
        # Much of this taken from https://towardsdatascience.com/violin-strip-swarm-and-raincloud-plots-in-python-as-better-sometimes-alternatives-to-a-boxplot-15019bdff8f8
        self.setup_plot_style()

        # Turn off minor ticks to avoid clutter
        rc("xtick.minor", visible=False)

        # Load data into a DataFrame
        data_frame = pandas.read_json(StringIO(self.raincloud_data.dataframe_json))

        # Make the violin plot. This shows the KDE's
        ax = sns.violinplot(
            y=self.raincloud_data.distribution_column_name,
            x=self.raincloud_data.categorical_column_name,
            data=data_frame,
            color="lightgrey",
            cut=0,
            density_norm="width",
            inner=None,
            width=1,
            linewidth=0.0,
        )

        # Clip the right half of each violin to make room for the strip plot
        for item in ax.collections:
            x0, y0, width, height = item.get_paths()[0].get_extents().bounds
            item.set_clip_path(plt.Rectangle((x0, y0), width / 2, height, transform=ax.transData))

        # Create strip plots with partially transparent points of different colors depending on the group.
        last_violin_idx = len(ax.collections)
        sns.stripplot(
            y=self.raincloud_data.distribution_column_name,
            x=self.raincloud_data.categorical_column_name,
            hue=self.raincloud_data.hue_column_name,
            data=data_frame,
            ax=ax,
            alpha=0.4,
            size=1,
            legend="full",
            palette="Paired",
        )

        # Shift each strip plot strictly below the corresponding violin.
        for item in ax.collections[last_violin_idx:]:
            item.set_offsets(item.get_offsets() + np.array([0.15, 0]))

        fig = ax.figure
        ax.set_ylabel(
            self.raincloud_data.ylabel, rotation=0 if self.raincloud_data.ylabel_horizontal else 90
        )
        ax.set_xlabel(self.raincloud_data.xlabel)

        # Make the legend
        if self.raincloud_data.hue_column_name:
            fig.set_size_inches(
                self.default_fig_width_in + self.default_legend_width_in,
                self.default_fig_height_in * 1.5,
            )
            box = ax.get_position()
            legend_frac = self.default_fig_width_in / (
                self.default_fig_width_in + self.default_legend_width_in
            )
            ax.set_position([box.x0, box.y0, box.width * legend_frac, box.height])
            legend = ax.legend(
                loc="upper left",
                bbox_to_anchor=(1, 1),
                title=self.raincloud_data.hue_column_name,
            )
            for modstate in legend.legend_handles:
                modstate.set_alpha(1.0)
                modstate.set_markersize(7)

        self.format_plot(ax)
        ax.set_xlim(
            data_frame[self.raincloud_data.categorical_column_name].min() - 2,
            data_frame[self.raincloud_data.categorical_column_name].max(),
        )

        # Only show axis spines over the range of data values
        #  based on seaborn's `despine` method
        yticks = np.r_[ax.yaxis.get_minorticklocs(), ax.yaxis.get_majorticklocs()]
        firsttick = np.compress(yticks >= min(ax.get_ylim()), yticks).min()
        lasttick = np.compress(yticks <= max(ax.get_ylim()), yticks).max()
        ax.spines["left"].set_bounds(firsttick, lasttick)

        xticks = np.r_[ax.xaxis.get_minorticklocs(), ax.xaxis.get_majorticklocs()]
        firsttick = np.compress(xticks >= min(ax.get_xlim()), xticks).min()
        lasttick = np.compress(xticks <= max(ax.get_xlim()), xticks).max()
        ax.spines["bottom"].set_bounds(firsttick, lasttick)

        image_flowable = self.save_fig_object(fig, DPI=600)
        return [spacer, image_flowable, spacer]

    def make_efficiency_plot(self) -> list[Flowable]:
        """Make a stack of 4 histograms showing the modulation efficiency for each Stokes parameter."""
        self.setup_plot_style()

        # Turn off minor ticks to avoid clutter
        rc("ytick.minor", visible=False)

        data_array = np.array(self.efficiency_data.efficiency_list)

        # Set up the axis and figure objects
        fig, axs = plt.subplots(nrows=4, ncols=1)
        fig.set_size_inches(self.default_fig_width_in, self.default_fig_height_in * 2)

        stokes_list = ["I", "Q", "U", "V"]
        for s, stokes in enumerate(stokes_list):
            ax = axs[s]
            ax.hist(data_array[s], bins="sqrt", alpha=0.6, edgecolor="none")
            ax.text(1, 0.8, stokes, transform=ax.transAxes)
            self.format_plot(ax, pad_y_lims=False)
            if s < 3:
                ax.set_xticklabels([])

        # Set all xlims to be the same
        limit_list = [ax.get_xlim() for ax in axs]
        xmin = np.min(limit_list)
        xmax = min(np.max(limit_list), 1.0)
        for ax in axs:
            ax.set_xlim(xmin, xmax)

        # Small gap between
        fig.subplots_adjust(hspace=0.1)

        axs[-1].set_xlabel("Modulation Efficiency")

        # Common axes with all lines/ticks turned off to be used for labels
        label_ax = fig.add_subplot(111)
        label_ax.set_facecolor([0, 0, 0, 0])  # Transparent
        label_ax.spines["top"].set_color("none")
        label_ax.spines["bottom"].set_color("none")
        label_ax.spines["left"].set_color("none")
        label_ax.spines["right"].set_color("none")
        label_ax.tick_params(
            labelcolor="none", which="both", top=False, bottom=False, left=False, right=False
        )
        label_ax.set_ylabel("N")

        image_flowable = self.save_fig_object(fig)
        return [spacer, image_flowable, spacer]

    def save_fig_object(self, fig: plt.Figure, DPI: int = 300) -> Image:
        """Save a figure to disk and ingest that image as a flowable Image"""
        image_target = BytesIO()
        fig.savefig(image_target, dpi=DPI)
        plt.clf()
        plt.close("all")
        image_target.seek(0)
        return Image(image_target, lazy=0, useDPI=DPI)

    def draw_arrows_out_of_range(self, ax, x, y):
        """
        Take an existing axis object with data points and draw arrows to data points that fall out of y range.
        """
        ymin, ymax = ax.get_ylim()
        yrange = ymax - ymin
        for xi, yi in zip(x, y):
            if yi > ymax:
                ax.annotate(
                    "",
                    xy=(xi, ymax),
                    xytext=(xi, ymax - yrange * 0.1),
                    arrowprops=dict(arrowstyle="->", alpha=0.5),
                )
            elif yi < ymin:
                ax.annotate(
                    "",
                    xy=(xi, ymin),
                    xytext=(xi, ymin + yrange * 0.1),
                    arrowprops=dict(arrowstyle="->", alpha=0.5),
                )

    def format_plot(
        self,
        ax: Axes,
        pad_x_lims: bool = True,
        pad_y_lims: bool = True,
    ):
        """Take an existing Axis object and massage the formatting a bit for enhanced visual appeal."""
        # Truncate long numbers using scientific notation
        ax.ticklabel_format(style="scientific", axis="y", scilimits=(0, 3))
        try:
            # We use 10,000 as the upper limit for X specifically so IR wavelengths don't get printed in sci-notation
            ax.ticklabel_format(style="scientific", axis="x", scilimits=(0, 4))
            ax.ticklabel_format(axis="x", useOffset=False)
        except AttributeError:
            # X axis must have non-number labels (i.e., dates)
            pass

        # Turn off the top and right axis lines
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.yaxis.set_ticks_position("left")
        ax.xaxis.set_ticks_position("bottom")

        # Pad the limits just a bit
        if pad_x_lims:
            x_limit_padding_fraction = 0.07
            xmin, xmax = ax.get_xlim()
            x_stretch = (xmax - xmin) * x_limit_padding_fraction
            ax.set_xlim(xmin - x_stretch, xmax + x_stretch)

        # Histograms look better with no padding on the bottom
        if pad_y_lims:
            y_limit_padding_fraction = 0.05
            ymin, ymax = ax.get_ylim()
            y_stretch = (ymax - ymin) * y_limit_padding_fraction
            ax.set_ylim(ymin - y_stretch, ymax + y_stretch)

        self._scale_label_to_fit_axis(ax)

    def _scale_label_to_fit_axis(self, ax: Axes) -> None:
        """Automatically reduce the fontsize of an axis label if it will extend too far beyond the axis."""
        ax_bounding_box = ax.get_window_extent()
        for single_ax, size_attr, size_limit in zip(
            [ax.xaxis, ax.yaxis],
            ["width", "height"],
            [ax_bounding_box.width, ax_bounding_box.height],
        ):
            ax_label = single_ax.label
            if (size_attr == "width" and ax_label.get_rotation() != 0) or (
                size_attr == "height" and ax_label.get_rotation() != 90
            ):
                # Non-default rotations, let's not mess with this
                continue

            label_font_size = ax_label.get_size()
            label_box_size = getattr(ax_label.get_window_extent(), size_attr)

            # `* 1.5` because we want to allow *some* bleeding. Othewise the integerization of the font size can force
            # the final text to be too small. This number was arrived at via trial and error. Feel free to change it.
            while label_box_size > size_limit * 1.5:
                label_font_size -= 1
                ax_label.set_size(label_font_size)
                label_box_size = getattr(ax_label.get_window_extent(), size_attr)

    @cached_property
    def default_fig_width_in(self) -> float:
        """Default figure width [in]."""
        return 6.0

    @cached_property
    def default_fig_height_in(self) -> float:
        """Default figure height [in]."""
        return self.default_fig_width_in / 2  # A nice ratio

    @cached_property
    def default_legend_width_in(self) -> float:
        """Default legend width [in]. How much space a legend takes up on the page."""
        return 2.0

    @cached_property
    def default_connecting_line_alpha(self) -> float:
        """Default alpha given to lines that connect points."""
        return 0.2

    @cached_property
    def default_plot_kwargs(self) -> dict[str, Any]:
        """Default non-label kwargs to the call to `ax.plot`."""
        return {"ls": "none", "marker": ".", "ms": 6}

    def setup_plot_style(self):
        """Initialize nice-looking defaults for matplotlib."""
        # Set up some style-defaults
        rcdefaults()
        axis_line_width = 0.3
        dkist_blue = "#1E317A"
        dkist_orange = "#FAA61C"
        plt.style.use("classic")
        rc("figure", figsize=(self.default_fig_width_in, self.default_fig_height_in))
        rc("font", family="serif", weight=100, size=10)
        # rc("mathtext", default="regular", fontset="cm")
        rc("xtick", labelsize=8)
        rc("ytick", labelsize=8)
        rc("xtick.major", size=5, width=axis_line_width)
        rc("ytick.major", size=5, width=axis_line_width)
        rc("xtick.minor", size=2, width=axis_line_width, visible=True)
        rc("ytick.minor", size=2, width=axis_line_width, visible=True)
        rc(
            "lines",  # Most of this isn't used now, but maybe for weirder plots later
            markeredgewidth=1,
            linewidth=0.7,  # Line width is used, though
            dashed_pattern=[6, 6],
            dashdot_pattern=[3, 5, 1, 5],
            dotted_pattern=[1, 3],
            scale_dashes=False,
        )

        # Defines how much space around the plot for non-plot stuff
        rc("figure.subplot", top=0.90, bottom=0.2)
        # Default legend style is trash
        rc("legend", numpoints=1, scatterpoints=1, frameon=False, handletextpad=0.3, fontsize=10)
        rc("axes", linewidth=axis_line_width, labelweight=10, labelsize=12, labelpad=15)

        # The cycle of colors that will be used when plotting multiple lines.
        # This particular set is the tableau-colorblind10 sequence with the blue and orange replaced with dkist values
        colors = cycler(
            color=[
                dkist_orange,
                dkist_blue,
                "#ABABAB",
                "#595959",
                "#5F9ED1",
                "#C85200",
                "#898989",
                "#A2C8EC",
                "#FFBC79",
                "#CFCFCF",
            ]
        )
        rc("axes", prop_cycle=colors)

        return

    @staticmethod
    def join_flowables(*flowables) -> list[Flowable]:
        """
        Helper to join instances and lists of flowables together as a single list
        """
        result = []
        for f in flowables:
            if isinstance(f, list):
                result += f
            else:
                result.append(f)
        return result

    @classmethod
    def from_dict(cls, data: dict):
        """
        Convert a dict report data to ReportMetric instance accepting extra
          keys in the data dictionary but validating known keys
        :param data: report data dictionary
        :return: instance of the ReportMetric class
        :raises: ReportFormattingException
        """
        if not isinstance(data, dict):
            raise ReportFormattingException("Report data must be a dict to validate schema")
        valid_args = {k: v for k, v in data.items() if k in cls.__dataclass_fields__.keys()}
        try:
            return dacite.from_dict(cls, valid_args, dacite.Config(check_types=False))
        except (UnicodeDecodeError, TypeError, ValueError, dacite.exceptions.DaciteFieldError) as e:
            # Catch parsing Failure
            raise ReportFormattingException(f"Report metric validation failed. detail={e}") from e


class LinkingHeading(Paragraph):
    """Subclass for document headings that produce anchors for internal links.

    In other words, use this class if you want a paragraph to be linkable and/or automatically show up as a TOC entry.
    """

    def __init__(self, text, register_with_toc: bool = True, **kwargs):
        # Force the style to be our heading style
        super().__init__(text=text, style=style_heading, **kwargs)
        self.anchor_name = text
        self.register_with_toc = register_with_toc

    def draw(self):
        """Draw the paragraph element.

        Overloaded so we can add an anchor that allows for linking from the table of contents.
        """
        super().draw()

        # The vertical offset makes the link take the reader to just above the actual heading
        vertical_offset = style_heading.__dict__["fontSize"] + style_heading.__dict__["spaceAfter"]
        self.canv.bookmarkHorizontal(self.anchor_name, 0, vertical_offset)


class WarningLinkParagraph(Paragraph):
    """Subclass for bold style text that will link to LinkingHeading paragraph that shares its text content

    This is used to make a list of warnings that can link down to the actual metric.
    """

    def __init__(self, text, **kwargs):
        super().__init__(text=text, style=style_bold, **kwargs)

        # The link destination needs to be exactly the same as the metric name, so here we remove a trailing colon, if present
        self.link_destination = text
        if text[-1] == ":":
            self.link_destination = text[:-1]

    def drawOn(self, canvas, x, y, _sW=0):
        """Overloaded to draw the active link rectangle.

        This is here because `drawOn` is when this flowable finally knows its location on the page.
        """
        # Idea taken from https://stackoverflow.com/questions/18114820/is-it-possible-to-get-a-flowables-coordinate-position-once-its-rendered-using/18156649#18156649
        RECT = (x, y, x + self.width, y + self.height)
        canvas.linkRect(
            f"Go to {self.link_destination} warning",
            self.link_destination,
            Rect=RECT,
            Border="[0, 0, 0, 0]",
        )
        super().drawOn(canvas, x, y, _sW=_sW)


class AutoIndexingReport(SimpleDocTemplate):
    """Subclass of SimpleDocTemplate that automatically registers all flowables with a potential Table of Contents.

    If a TableOfContents is not added then this acts just like a SimpleDocTemplate
    """

    # Got the idea from https://stackoverflow.com/questions/70880125/problem-with-tableofcontent-reportlab-doc-notify-does-not-generate-in-toc
    def __init__(self, filename: str | BytesIO, **kwargs):
        super().__init__(filename, **kwargs)

    def afterFlowable(self, flowable):
        """Check if flowable is our special LinkingHeading type and register it if it is."""
        if isinstance(flowable, LinkingHeading) and flowable.register_with_toc:
            text = flowable.getPlainText()
            # Syntax of the entry is (TOC level, entry text, page number, link anchor name).
            #  For our purposes the TOC level will always be 0
            entry = (0, text, self.page, flowable.anchor_name)
            self.notify("TOCEntry", entry)


def initialize_table_of_content() -> list[Flowable]:
    """Return a list of flowables that defines the full Table of Contents"""
    flowables = []
    flowables.append(Paragraph("Metrics", style_heading))
    toc = TableOfContents(levelStyles=[style_toc_entry], tableStyle=table_style_toc)
    flowables.append(toc)

    # Force a page break after the TOC.
    # I'm not sure why, but without this line a table of contents that is large enough to span multiple pages
    #  will cause *subsequent* flowables to raise a LayoutError because they're too large.
    # I don't get it, but that's the way it is.
    flowables.append(PageBreak())

    # We can't use KeepTogether here because it breaks the TOC machinery for some reason
    return flowables


def construct_warning_summary(report_data: dict | list[dict]) -> Flowable:
    """Build up the special 'Warnings Summary' section.

    This section will list all warnings and provide links to their respective metrics.
    """
    if isinstance(report_data, dict):
        report_data = [report_data]

    warning_count = 0
    warning_flowables = []
    for metric in report_data:
        if metric.get("warnings", False):
            warning_count += 1
            # The linking magic happens in WarningLinkParagraph
            warning_flowables.append(WarningLinkParagraph(f"{metric['name']}:"))
            warning_flowables += [Paragraph(f"{w}", style_warn) for w in metric["warnings"]]
            warning_flowables.append(spacer)

    flowables = []
    flowables.append(LinkingHeading("Warnings Summary"))
    if warning_count == 0:
        summary_text = Paragraph(f"No warnings generated", style_normal)
        flowables.append(summary_text)
    flowables += warning_flowables

    return KeepTogether(flowables)


def format_report(report_data: dict | list[dict], dataset_id: str) -> bytes:
    """
    Format the report data into a PDF
    Report Lab documentation reference
    https://pythoncircle.com/post/729/automating-pdf-generation-using-python-reportlab-module/
    https://www.reportlab.com/docs/reportlab-userguide.pdf
    """
    if isinstance(report_data, dict):
        report_data = [report_data]
    if not isinstance(report_data, list):
        raise ReportFormattingException(
            f"Report data cannot be parsed as expected. "
            f"Expected a dict or list[dict] but received {type(report_data)}"
        )

    ## First, construct the pre-metric sections
    title_text = f"Quality Report for Dataset {dataset_id}"
    title = Paragraph(title_text, style_title)
    subtitle = Paragraph(
        f"Generated on {datetime.utcnow().strftime('%Y-%m-%d at %H:%M UTC')}", style_subtitle
    )
    preamble = Paragraph(
        f"The quality metrics that follow represent quantitative measures of the quality of the dataset.",
        style_normal,
    )

    # Make a table of contents
    TOC = initialize_table_of_content()

    # Generate the Warnings Summary section
    warnings_summary = construct_warning_summary(report_data)

    # Start document (i.e., flowables) with all pre-metric sections
    flowables = [title, subtitle, spacer, preamble, *TOC, warnings_summary]

    ## Now build and add all of the metrics
    # for page-space considerations we'll sort them into plot metrics and text metrics
    plot_metrics = [i for i in report_data if "plot_data" in i and i["plot_data"] is not None]
    non_plot_metrics = [i for i in report_data if "plot_data" not in i or i["plot_data"] is None]

    for data in plot_metrics:
        flowables.append(ReportMetric.from_dict(data).generate_flowables())

    text_flowables = []
    for data in non_plot_metrics:
        text_flowables.append(ReportMetric.from_dict(data).generate_flowables())
        text_flowables.append(spacer)
    flowables.append(KeepTogether(text_flowables))

    ## Finally, build the actual PDF
    target = BytesIO()
    report = AutoIndexingReport(target, author="DKIST Data Center", title=title_text)
    # multiBuild calls build a few times to link, index, and build the table of contents correctly.
    #  (it's like calling LaTeX twice to link the refs correctly, if that means anything to anyone)
    report.multiBuild(story=flowables)
    target.seek(0)
    return target.read()
