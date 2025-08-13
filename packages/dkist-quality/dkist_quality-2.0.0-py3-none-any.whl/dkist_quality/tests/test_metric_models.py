import pytest
from pydantic import ValidationError

from dkist_quality.report import Plot2D
from dkist_quality.report import VerticalMultiPanePlot2D


def test_validate_vertical_multi_pane_plot_model():
    """
    Given: A `VerticalMultiPanePlot2D` model and some `Plot2D` models
    When: Instantiating the `VerticalMultiPanePlot2D` with various parameters
    Then: The `top_to_bottom_plot_ratios` property is correctly populated
    """
    plot2d = Plot2D(
        xlabel="X", ylabel="Y", ylabel_horizontal=False, series_data={"Foo": [[1.0], [2.0]]}
    )

    # Test given ratios valid case
    _ = VerticalMultiPanePlot2D(
        top_to_bottom_plot_list=[plot2d, plot2d], top_to_bottom_height_ratios=[1.0, 2.0]
    )

    # Test None ratios
    vertical_plots = VerticalMultiPanePlot2D(
        top_to_bottom_plot_list=[plot2d, plot2d], top_to_bottom_height_ratios=None
    )
    assert vertical_plots.top_to_bottom_height_ratios == [1.0, 1.0]

    # Test invalid case
    with pytest.raises(
        ValidationError,
        match="The number of items in `top_to_bottom_height_ratios` list \(3\) is not "
        "the same as the number of plots \(2\)",
    ):
        _ = VerticalMultiPanePlot2D(
            top_to_bottom_plot_list=[plot2d, plot2d], top_to_bottom_height_ratios=[1.0, 2.0, 3.0]
        )
