"""
Pie chart plotting with flexible annotation control.

This module provides a `piechart` function to create labelled pie charts using
`matplotlib`. It allows for full control over arrow and text positioning via
scaling factors and provides mechanisms to handle exploded slices, tight label
spacing, and custom annotation styling. The function integrates input validation,
axis reuse, and visual tuning options such as wedge transparency, label placement,
and arrow bending behaviour.

Functions
---------
piechart
    Draws a pie chart with optional annotations on an existing or new Axes,
    using customisable options for text and arrow positioning.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plot_misc.constants import Real
from plot_misc.errors import (
    is_df,
    are_columns_in_df,
    is_type,
    same_len,
)
from typing import Any
from plot_misc.utils.utils import (
    adjust_labels,
    _update_kwargs,
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def piechart(
    data: pd.DataFrame, col_values: str, col_labels:str | None = None,
    ax: plt.Axes | None = None, figsize: tuple[float, float] = (8, 4),
    colours: list[str] = ['black', 'grey', 'lightgrey'],
    fontsize: Real = 8, min_dist_lables: Real = 0.13,
    text_pos_scaling:list[tuple[float,float]] | tuple[float,float]=(1.15,1.15),
    line_start_scaling:list[tuple[float,float]] | tuple[float,float]=(1.00, 1.00),
    arrowprops: dict[str, Any] | None = None,
    bboxprops: dict[str, Any] | None = None,
    pie_kwargs:dict[Any,Any] | None = None,
    annotate_kwargs:dict[Any,Any] | None = None,
):
    """
    Draws a pie chart with optional labels and annotation arrows.
    
    This function draws a pie chart from the provided DataFrame, with optional
    label annotations and arrows indicating wedge boundaries. It supports
    both uniform and wedge-specific scaling for label and arrow placement,
    making it suitable for charts with exploded slices or dense label sets.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        A DataFrame containing the numeric values and (optional) labels for
        each wedge in the pie chart.
    col_values : `str`
        Name of the column containing the numeric values that determine wedge
        sizes.
    col_labells : `str` or `None`, default `None`
        Name of the column containing wedge labels. If None, the pie chart is
        drawn without annotations.
    figsize : `tuple` [`float`, `float`], default `(8, 4)`
        Size of the figure in inches if `ax` is not provided.
    colours : `list` [`str`, `str`], default [`black`, 'grey`, 'lightgrey']
        List of colours to apply to the wedges. Cycled if fewer than the number
        of data points.
    fontsize : `float`, default 8.0
        Font size used for annotation labels.
    min_dist_lables : `float`, default 0.13
        Minimum spacing between labels after adjustment.
    text_pos_scaling : `tuple` [`float`, `float`], default (1.15, 1.15)
        Scaling factor applied to the label position, controlling how far labels
        are placed from the wedge centre. A single tuple applies the same scaling
        to all wedges; a list allows for per-wedge positioning.  The first
        values moves the text left or right, the second value up or down.
    line_start_scaling : `tuple` [`float`, `float`], default (1.00, 1.00)
        Scaling factor applied to the arrow starting point (on the wedge).
        A value > 1 pushes the arrow start outward from the centre. Like
        `text_pos_scaling`, a list allows per-wedge values.
    ax : `plt.Axes` or `None`, default `NoneType`
        Axes on which to draw the pie chart. If None, a new figure and axes
        are created.
    arrowprops : `dict` [`str`, 'any`] or `None`, default `NoneType'
        keyword arguments passed to `FancyArrowPatch` to style the arrow
        connecting label to wedge.
    bboxprops : `dict` [`str`, `any`] or `None`, default `NoneType`
        keyword arguments passed to the annotation text bounding box (`bbox`).
    pie_kwargs : `dict`, default `NoneType`
        Additional keyword arguments passed to `ax.pie`.
    annotate_kwargs :`` dict, default `NoneType`
        Additional keyword arguments passed to `ax.annotate`.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure containing the pie chart.
    ax : matplotlib.axes.Axes
        The axes containing the pie chart and annotations.
    
    Raises
    ------
    ValueError
        If `data[col_values]` contains any values less than or equal to zero.
    TypeError
        If positional scaling parameters are of the wrong type.
    """
    # #### check input
    is_df(data)
    is_type(ax, (plt.Axes, type(None)))
    is_type(col_labels, (type(None), str))
    is_type(col_values, str)
    is_type(min_dist_lables, Real)
    is_type(text_pos_scaling, (list, tuple))
    is_type(line_start_scaling, (list, tuple))
    col_list = [col_labels, col_values]
    # confirms columns are available
    if col_labels is None:
        col_list = [col_values]
    are_columns_in_df(data, col_list)
    if isinstance(text_pos_scaling, tuple):
        text_pos_scaling = [text_pos_scaling] * data.shape[0]
    if isinstance(line_start_scaling, tuple):
        line_start_scaling = [line_start_scaling] * data.shape[0]
    # confirm lengths
    same_len(text_pos_scaling, data, ['text_pos_scaling', 'data'])
    same_len(line_start_scaling, data, ['text_pos_scaling', 'data'])
    # set defaults
    if bboxprops is None:
        bboxprops = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.0,
                          alpha=0.0)
    if arrowprops is None:
        arrowprops=dict(arrowstyle="-", lw=0.4)
    # map None to dict
    pie_kwargs = pie_kwargs or {}
    annotate_kwargs = annotate_kwargs or {}
    # update kwargs
    pie_kwargs = _update_kwargs(update_dict = pie_kwargs,
                                autopct = '', startangle = 135,
                                colors = colours, wedgeprops = {
                                    'alpha' : 0.5, 'edgecolor': 'k',
                                    'linewidth' : 0.5},
                                )
    # Create new ax if not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
    # Are there zero counts
    if (data[col_values] <= 0).sum() > 0:
        raise ValueError("Input data includes zero values.")
    # draw piechart
    wedges, _, _ = ax.pie(data[col_values], **pie_kwargs)
    # equal aspect ratio ensures that pie is drawn as a circle
    ax.axis('equal')
    # Define annotation properties
    if col_labels is not None:
        # NOTE consider making this into a separate function
        # get wedges from ax.patches
        annot_kwargs = _update_kwargs(update_dict = annotate_kwargs,
                                      arrowprops=arrowprops,
                                      bbox=bboxprops, zorder=0, va="center")
        # Create a list to store annotations for adjusting labels
        labels = data[col_labels].to_list()
        annotations = []
        for i, p in enumerate(wedges):
            # wedge center
            cx, cy = p.center
            # gets the angle of each wedge
            ang = (p.theta2 - p.theta1) / 2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            # whether the alignment is right or left of the center
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            # the angle of the arrow/line
            connectionstyle = f"angle,angleA=0,angleB={ang}"
            annot_kwargs["arrowprops"].update(
                {"connectionstyle": connectionstyle})
            # Annotate labels and store them in the list
            annot_kwargs = _update_kwargs(update_dict = annot_kwargs,
                                          fontsize=fontsize,)
            ann = ax.annotate(labels[i], xy=(cx + line_start_scaling[i][0]*x,
                                             cy + line_start_scaling[i][1]*y),
                              xytext=(text_pos_scaling[i][0] * np.sign(x),
                                      text_pos_scaling[i][1] * y),
                              horizontalalignment=horizontalalignment,
                              **annot_kwargs,)
            # add annotations
            annotations.append(ann)
        # Adjust labels
        adjust_labels(annotations, ax, min_distance=min_dist_lables)
    # return figure and axes
    return fig, ax

