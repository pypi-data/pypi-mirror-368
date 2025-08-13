"""
Tests for the report generation functionality
"""
import json
from copy import copy
from datetime import datetime
from io import BytesIO
from os import environ
from pathlib import Path
from uuid import uuid4

import numpy as np
import pytest
from pandas import DataFrame
from pypdf import PdfReader

from dkist_quality.json_encoder import datetime_json_object_hook
from dkist_quality.json_encoder import DatetimeEncoder
from dkist_quality.report import format_report
from dkist_quality.report import ReportFormattingException


def json_dump_and_load(data):
    """
    Run the data parameter through a dump + load process similar to how it is expected to
      happen in the operational system.
    """
    json_data = json.dumps(data, cls=DatetimeEncoder)
    return json.loads(json_data, object_hook=datetime_json_object_hook)


@pytest.fixture(
    params=[
        "TABLE_TYPE",
        "MULTIPLE_TABLES",
        "2D_PLOT_TIME_SERIES_TYPE",
        "2D_PLOT_TIME_MULTIPLE_SERIES",
        "2D_PLOT_BIG_TYPE",
        "2D_PLOT_CATEGORY",
        "MULTIPLE_2D_PLOTS",
        "VERTICAL_2_PANE_PLOTS",
        "VERTICAL_2_PANE_WITH_GAP_NOSHARE",
        "VERTICAL_3_PANE_PLOTS",
        "HISTOGRAM",
        "MULTIPLE_HISTOGRAMS",
        "MODULATION_MATRICES",
        "RAINCLOUD",
        "MODULATION_EFFICIENCY",
        "STATEMENT_TYPE",
        "COMPOUND_TYPE",
        "ALL_TYPES",
    ]
)
def report_data(request):
    key = request.param
    TABLE_ELEMENT = {
        "name": "TABLE_TYPE",
        "description": "The number of frames used to produce a calibrated L1 dataset, split by type",
        "statement": [
            "String statement that goes along with a table",
            "Another statement for some reason",
        ],
        "table_data": {
            "rows": [["Task type", "Number"], ["observe", 1800], ["dark", 135], ["gain", 91]],
            "header_row": True,
        },
        "warnings": ["62% of dark frames not used"],
    }
    MULTIPLE_TABLES_ELEMENT = {
        "name": "MULTIPLE_TABLES_TYPE",
        "description": "A single metric with multiple tables",
        "statement": "Repetition is the key to learning",
        "table_data": [TABLE_ELEMENT["table_data"]] * 3,
    }
    PLOT_2D_TIME_SERIES_ELEMENT = {
        "name": "2D_PLOT_TIME_SERIES_TYPE",
        "description": "A single data series using the `series_data` keyword and y limits set",
        "statement": "Average Fried Parameter for L1 dataset: 15.0 ± 0.22 cm",
        "plot_data": {
            "xlabel": "Time",
            "ylabel": "Fried Parameter (cm)",
            "ylim": (14.1, 15.2),
            "series_data": {
                "series a": [
                    [
                        datetime.fromisoformat("2021-01-01T00:10:00"),
                        datetime.fromisoformat("2021-01-01T00:10:10"),
                        datetime.fromisoformat("2021-01-01T00:10:20"),
                        datetime.fromisoformat("2021-01-01T00:10:30"),
                        datetime.fromisoformat("2021-01-01T00:10:45"),
                    ],
                    [14.0, 14.2, 14.7, 15.1, 15.3],
                ]
            },
        },
        "warnings": None,
    }
    PLOT_2D_TIME_MULTIPLE_SERIES_ELEMENT = {
        "name": "2D_PLOT_TIME_MULTIPLE_SERIES",
        "description": "Multiple sets of data shown on one plot",
        "statement": "These are multiple sets of data",
        "plot_data": {
            "xlabel": "Time",
            "ylabel": "Value",
            "series_name": "series",
            "series_data": {
                "3": [
                    [
                        datetime.fromisoformat("2021-01-01T00:10:00"),
                        datetime.fromisoformat("2021-01-01T00:10:30"),
                        datetime.fromisoformat("2021-01-01T00:10:45"),
                    ],
                    [14.7, 15.1, 15.3],
                ],
                "1": [
                    [
                        datetime.fromisoformat("2021-01-01T00:10:10"),
                        datetime.fromisoformat("2021-01-01T00:10:40"),
                        datetime.fromisoformat("2021-01-01T00:10:55"),
                    ],
                    [9.4, 8.7, 5.3],
                ],
                "2": [
                    [
                        datetime.fromisoformat("2021-01-01T00:10:20"),
                        datetime.fromisoformat("2021-01-01T00:10:50"),
                        datetime.fromisoformat("2021-01-01T00:11:00"),
                    ],
                    [10.6, 9.4, 14.5],
                ],
            },
        },
        "warnings": None,
    }
    PLOT_2D_CATEGORY_ELEMENT = {
        "name": "2D_CATEGORY_PLOT_TYPE",
        "description": "A number plotted against another number",
        "statement": "Average thing over another thing",
        "plot_data": {
            "xlabel": "Something",
            "ylabel": "Something else",
            "series_data": {
                "series 1": [
                    [1, 10, 11],
                    [14.7, 15.1, 15.3],
                ]
            },
        },
        "warnings": None,
    }
    PLOT_2D_BIG_ELEMENT = {
        "name": "2D_BIG_PLOT_TYPE",
        "description": "A lot of numbers plotted against a lot of other numbers",
        "statement": "Average thing over another thing",
        "plot_data": {
            "xlabel": "Something",
            "ylabel": "Something else",
            "series_data": {
                "series 1": [
                    list(range(1, 1000)),
                    list(range(1000, 1, -1)),
                ]
            },
        },
        "warnings": None,
    }
    TWO_PANE_PLOT_LIST = [
        {
            "xlabel": "X1",
            "ylabel": "Y",
            "series_data": {
                "Thing 1": [list(range(1000, 2000)), [i * 0.1 for i in range(1000, 2000)]],
                "Thing 2": [
                    [i + 300 for i in range(1000, 1500)],
                    [i**0.5 for i in range(1000, 1500)],
                ],
                "Final Thing": [
                    list(range(1200, 2001)),
                    [240_000.0 / i for i in range(1200, 2001)],
                ],
            },
            "plot_kwargs": {"Final Thing": {"ls": "-", "ms": 0, "alpha": 0.7, "lw": 1}},
            "sort_series": False,
        },
        {
            "xlabel": "X",
            "ylabel": "Y2",
            "ylabel_horizontal": True,
            "series_data": {
                "Bottom 1": [list(range(1000, 2200)), [i * 3 for i in range(1000, 2200)]],
                "Bottom 2": [
                    list(range(1000, 1100)),
                    [-((i - 50) ** 2) for i in range(1000, 1100)],
                ],
            },
        },
    ]
    THREE_PANE_PLOT_LIST = TWO_PANE_PLOT_LIST + [
        {
            "xlabel": "X3",
            "ylabel": "A Quite Long\nLabel Str",
            "series_data": {"Last": [list(range(1000, 1100)), [i * 2 for i in range(1000, 1100)]]},
        }
    ]
    VERTICAL_2_PANE_ELEMENT = {
        "name": "VERTICAL_2_PANE_TYPE",
        "description": "A vertical stack of 2 plots that share an X axis",
        "multi_plot_data": {
            "top_to_bottom_plot_list": TWO_PANE_PLOT_LIST,
            "top_to_bottom_height_ratios": [1.5, 1.0],
        },
    }
    VERTICAL_2_PANE_WITH_GAP_NOSHARE_ELEMENT = {
        "name": "VERTICAL_2_PANE_TYPE_WITH_GAP_NOSHARE_TYPE",
        "description": "A vertical stack of plots. These ones don't share an X axis",
        "multi_plot_data": {
            "top_to_bottom_plot_list": TWO_PANE_PLOT_LIST,
            "no_gap": False,
            "match_x_axes": False,
        },
    }
    VERTICAL_3_PANE_ELEMENT = {
        "name": "VERTICAL_3_PANE_TYPE",
        "description": "A vertical stack of 3 plots that share an X axis.",
        "multi_plot_data": {
            "top_to_bottom_plot_list": THREE_PANE_PLOT_LIST,
            "top_to_bottom_height_ratios": [2, 1, 1],
        },
    }
    PLOT_DATA_WITH_PLOT_KWARGS = copy(PLOT_2D_TIME_MULTIPLE_SERIES_ELEMENT["plot_data"])
    PLOT_DATA_WITH_PLOT_KWARGS["plot_kwargs"] = {
        "3": {"ls": ":", "color": "red", "ms": 0},
        "1": {"marker": "x", "color": "green"},
    }
    MULTIPLE_2D_PLOTS_ELEMENT = {
        "name": "MULTIPLE_2D_PLOTS_TYPE",
        "description": "Multiple plots for the same metric",
        "statement": "3 Plots that are cool",
        "plot_data": [
            # These three were chosen randomly
            PLOT_DATA_WITH_PLOT_KWARGS,
            # PLOT_2D_TIME_MULTIPLE_SERIES_ELEMENT["plot_data"],
            PLOT_2D_CATEGORY_ELEMENT["plot_data"],
            PLOT_2D_BIG_ELEMENT["plot_data"],
        ],
    }
    PLOT_HISTOGRAM_ELEMENT = {
        "name": "HISTOGRAM_TYPE",
        "description": "Multiple data on a single histogram",
        "statement": "I like turtles",
        "histogram_data": {
            "xlabel": "thing",
            "series_data": {
                "series 1": list(range(100)),
                "series 2": np.random.randn(100).tolist(),
            },
            "series_name": "Types",
            "vertical_lines": {"line": 0.0},
        },
    }
    MULTIPLE_HISTOGRAM_ELEMENT = {
        "name": "MULTIPLE_HISTOGRAM_TYPE",
        "description": "Multiple histogram plots",
        "statement": "I like lots of turtles",
        "histogram_data": [PLOT_HISTOGRAM_ELEMENT["histogram_data"]] * 3,
    }
    MODULATION_MATRICES_ELEMENT = {
        "name": "MODULATION_MATRIX_TYPE",
        "description": "Big ol' grid of histograms",
        "statement": "I like turtles",
        "modmat_data": {"modmat_list": np.random.randn(8, 4, 100).tolist()},
    }
    nummod = 8
    numstep = 10
    numpoints = 100
    points = np.random.randn(numpoints * numstep * nummod)
    mods = np.hstack([np.arange(nummod) + 1 for i in range(numstep * numpoints)])
    steps = np.hstack([np.arange(numstep) + 1 for i in range(nummod * numpoints)])
    data = np.vstack((points, mods, steps)).T
    PLOT_RAINCLOUD_ELEMENT = {
        "name": "RAINCLOUD_TYPE",
        "description": "Crazy-ass statistics shit",
        "statement": "I like turtles",
        "raincloud_data": {
            "xlabel": "Category number",
            "ylabel": r"$\alpha = \beta$",
            "ylabel_horizontal": True,
            "categorical_column_name": "A",
            "distribution_column_name": "B",
            "hue_column_name": "C",
            "dataframe_json": DataFrame(data=data, columns=["B", "C", "A"]).to_json(),
        },
    }
    PLOT_MODULATION_EFFICIENCY_ELEMENT = {
        "name": "EFFICIENCY_TYPE",
        "description": "Stacked histograms",
        "statement": "I don't like turtles",
        "efficiency_data": {"efficiency_list": ((np.random.randn(4, 100) - 0.5) * 0.3).tolist()},
    }
    STATEMENT_ELEMENT = {
        "name": "STATEMENT TYPE",
        "description": "Percentage of calibrated frames created from data taken during time the adaptive optics system was running",
        "statement": "Adaptive Optics system was running during 82% of observe frame acquisition",
    }
    COMPOUND_ELEMENT = {
        "name": "COMPOUND TYPE",
        "description": "Hypothetical example of table plus plot metric",
        "statement": "Average Fried Parameter for L1 dataset: 15.0 ± 0.22 cm",
        "plot_data": {
            "xlabel": "Something",
            "ylabel": "Fried Parameter (cm)",
            "series_data": {
                "series a": [
                    [1, 2, 3],
                    [14.7, 15.1, 15.3],
                ]
            },
        },
        "table_data": {
            "rows": [["Task type", "Number"], ["observe", 1800], ["dark", 135], ["gain", 91]],
            "header_row": True,
        },
        "warnings": ["62% of dark frames not used", "42% of dark frames not happy"],
    }
    report_metric_types = {
        "TABLE_TYPE": TABLE_ELEMENT,
        "MULTIPLE_TABLES": MULTIPLE_TABLES_ELEMENT,
        "2D_PLOT_TIME_SERIES_TYPE": PLOT_2D_TIME_SERIES_ELEMENT,
        "2D_PLOT_TIME_MULTIPLE_SERIES": PLOT_2D_TIME_MULTIPLE_SERIES_ELEMENT,
        "2D_PLOT_CATEGORY": PLOT_2D_CATEGORY_ELEMENT,
        "2D_PLOT_BIG_TYPE": PLOT_2D_BIG_ELEMENT,
        "MULTIPLE_2D_PLOTS": MULTIPLE_2D_PLOTS_ELEMENT,
        "VERTICAL_2_PANE_PLOTS": VERTICAL_2_PANE_ELEMENT,
        "VERTICAL_2_PANE_WITH_GAP_NOSHARE": VERTICAL_2_PANE_WITH_GAP_NOSHARE_ELEMENT,
        "VERTICAL_3_PANE_PLOTS": VERTICAL_3_PANE_ELEMENT,
        "HISTOGRAM": PLOT_HISTOGRAM_ELEMENT,
        "MULTIPLE_HISTOGRAMS": MULTIPLE_HISTOGRAM_ELEMENT,
        "MODULATION_MATRICES": MODULATION_MATRICES_ELEMENT,
        "RAINCLOUD": PLOT_RAINCLOUD_ELEMENT,
        "MODULATION_EFFICIENCY": PLOT_MODULATION_EFFICIENCY_ELEMENT,
        "STATEMENT_TYPE": STATEMENT_ELEMENT,
        "COMPOUND_TYPE": COMPOUND_ELEMENT,
        "ALL_TYPES": [
            TABLE_ELEMENT,
            MULTIPLE_TABLES_ELEMENT,
            PLOT_2D_TIME_SERIES_ELEMENT,
            PLOT_2D_TIME_MULTIPLE_SERIES_ELEMENT,
            PLOT_2D_CATEGORY_ELEMENT,
            PLOT_2D_BIG_ELEMENT,
            MULTIPLE_2D_PLOTS_ELEMENT,
            VERTICAL_2_PANE_ELEMENT,
            VERTICAL_2_PANE_WITH_GAP_NOSHARE_ELEMENT,
            VERTICAL_3_PANE_ELEMENT,
            PLOT_HISTOGRAM_ELEMENT,
            MULTIPLE_HISTOGRAM_ELEMENT,
            MODULATION_MATRICES_ELEMENT,
            PLOT_MODULATION_EFFICIENCY_ELEMENT,
            PLOT_RAINCLOUD_ELEMENT,
            STATEMENT_ELEMENT,
            COMPOUND_ELEMENT,
        ],
    }
    result = report_metric_types[key]
    return json_dump_and_load(result)


@pytest.fixture
def dataset_id() -> str:
    return f"ds_{uuid4().hex[:4]}"


def test_format_report(report_data, dataset_id):
    report_bytes = format_report(report_data, dataset_id)
    report_reader = BytesIO(report_bytes)
    pdf = PdfReader(report_reader)
    assert pdf.get_num_pages()
    # ---- Look and Feel Dev Support ----
    if environ.get("SAVE_PDF", False):
        report_output_path = Path("reports/")
        report_output_path.mkdir(exist_ok=True)
        report = report_output_path / f"{dataset_id}.pdf"
        with report.open(mode="wb") as f:
            f.write(report_bytes)


def test_format_invalid_report(dataset_id):
    bad_report_data = {"NotTheKeyYouAreLookingFor": "value"}
    with pytest.raises(ReportFormattingException):
        report_bytes = format_report(bad_report_data, dataset_id)


def test_temp_raw_ticks():
    """
    There is a matplotlib bug that causes an IndexError when `rcParams["axes.autolimit_mode"] = "round_numbers"`.
    A temporary fix has been implemented to address the bug.
    This test tests that temporary fix.
    """
    import matplotlib as mpl

    # valid values:  data | round_numbers
    mpl.rcParams["axes.autolimit_mode"] = "round_numbers"
    mnl = mpl.ticker.MaxNLocator()
    mnl._nbins = 1
    mnl._extended_steps = np.array([0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0])
    actual_raw_ticks = mnl._raw_ticks(-9.4, 18.9)
    expected_raw_ticks = np.array([-10.0, 0.0, 10.0, 20.0])
    assert np.array_equal(actual_raw_ticks, expected_raw_ticks)
