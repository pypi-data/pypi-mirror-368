"""
Volcano plots for visualising effect size and statistical significance.

This module provides a template to create volcano plots for highlighting
results based on both the magnitude of effect and their statistical
significance. Typically, the x-axis shows an effect estimate and the y-axis
the negative log-transformed p-value. Dots can be coloured to distinguish
significant from non-significant results, and selected points may be annotated
with text labels.

Functions
---------
plot_volcano(data, y_column, x_column, point_label=None,  ...)
    Draws a volcano plot, optionally adding a vertical reference line and
    labels for significant points.

Notes
-----
These implementations are designed to work directly with matplotlib `Axes`
objects, and optionally allow de-overlapping of text using `adjustText`.
Appearance can be modified using standard matplotlib arguments and optional
keyword dictionaries for fine control over scatter and text elements.
"""

import numpy as np
import matplotlib.pyplot as plt
import warnings
from adjustText import adjust_text
from pandas.core.frame import DataFrame
from plot_misc.constants import Real
from plot_misc.utils.utils import(
    _update_kwargs,
)
from plot_misc.errors import(
    is_type,
    is_df,
)
from typing import Any

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def plot_volcano(data:DataFrame, y_column:str, x_column:str,
                 point_label:str | None = None,
                 fsize:tuple[float,float] | None = None, adjust:bool=False,
                 lim:int=1000, vline:Real=0, alpha:float=1e-5,
                 col:tuple[str, str, str]=('orangered','dimgrey','lightcoral'),
                 xlab:str='Point estimate', ylab:str=r'$-log_{10}(pvalue)$',
                 ylim:tuple[float, float] | None = None, msize:Real=10,
                 lsize:Real=5, transparency_ns:Real=0.6,
                 index_label:list[str] | None = None,
                 font_label: str | None = None,
                 ax:plt.Axes | None = None,
                 label_kwargs_dict:dict[Any,Any] | None = None,
                 scatter_sig_kwargs_dict:dict[Any,Any] | None = None,
                 scatter_nonsig_kwargs_dict:dict[Any,Any] | None = None,
                 ) -> tuple[plt.Figure, plt.Axes]:
    """
    Generate a volcano plot from a set of effect estimates and p-values.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        A DataFrame containing at least two columns: the effect estimate and
        the (negative log-transformed) p-value.
    y_column : `str`
        Name of the column containing the y-axis values (typically –log10 p).
    x_column : `str`
        Name of the column containing the x-axis values (effect sizes).
    point_label : `str` or `None`, default `NoneType`
        Column name in `data` to use for point labels. If `None`, no labels
        are added.
    fsize : `tuple` [`float`, `float`] or `None`, default `None`
        Figure size in inches (width, height). Ignored if `ax` is provided.
    adjust : `bool`, default `False`
        Whether to apply label de-overlapping using `adjustText`.
    lim : `int`, default 1000
        The tolerance for overplotting, higher numbers indicate lower tolerance
        and increases the distance between labels; also increasing the run time.
    vline : `real`, default 0
        The x-position of the vertical line
    alpha : `float`, default 1e-5
        P-value threshold for significance (used on –log10 scale).
    col : `tuple` [`str`, `str`, `str`]
        Colours for (1) significant points, (2) non-significant points,
        and (3) vertical line.
    xlab : `str`, default 'Point estimate'
        x-axis label.
    ylab : `str`, default '-log10(pvalue)'
        y-axis label.
    ylim : `tuple` [`float`,`float`]
        The y-limit, by default is simply uses the data limits.
    msize : `float`, default 10
        Marker size for scatter points.
    lsize : `float`, default 5
        Font size for text annotations.
    transparency_ns : `float`, default 0.6
        Transparency for non-significant points.
    index_label : `list` [`str`] or `None`
        Subset of rows indices to annotate. If `None`, all significant points
        are eligible.
    font_label : `str` or `None`, default `None`
        Font family to use for point labels (e.g. 'monospace', 'Arial').
    ax : `plt.axes` or `None`, default `None`
        Axis object to plot on. If `None`, a new figure and axis are created.
    *_kwargs_dict : dict, default `None`
        Optional arguments supplied to the various plotting functions:
            label_kwargs_dict          --> adjust_text
            scatter_sig_kwargs_dict    --> ax.bar
            scatter_nonsig_kwargs_dict --> ax.bar
    
    Returns
    -------
    figure : `matplotlib.figure.Figure`
        The created figure (if `ax` was not provided).
    ax : `matplotlib.axes.Axes`
        The matplotlib axis containing the plot.
    
    Notes
    -----
    When `adjust=True`, text labels are repositioned using the `adjustText`
    package to reduce overlaps. This is particularly helpful when multiple
    points are labelled in a crowded region. Additional options can be passed
    to `adjustText` via `label_kwargs_dict`.
    
    Please see the module documentation `here <https://pypi.org/project/adjustText/>`_.
    """
    FT_FAM = 'font.family'
    # ###### Check input
    is_df(data)
    is_type(y_column, str)
    is_type(x_column, str)
    is_type(point_label, (str, type(None)))
    is_type(font_label, (type(None), str))
    is_type(col, tuple)
    if len(col) != 3:
        raise ValueError("Please make sure `col` is a tuple with 3 elements, "
                         f"not:{len(col)}.")
    # map None to dict
    label_kwargs_dict = label_kwargs_dict or {}
    scatter_sig_kwargs_dict = scatter_sig_kwargs_dict or {}
    scatter_nonsig_kwargs_dict = scatter_nonsig_kwargs_dict or {}
    # raise warning
    if (adjust == True and point_label == None):
        warnings.warn('`adjust` is ignored if `point_label` is None',
                      SyntaxWarning)
    ### getting figure
    # should we create a figure and axis
    if ax is None:
        f, ax = plt.subplots(figsize=fsize)
    else:
        f = ax.figure
    ### significance level
    threshold = -1 * np.log10(alpha)
    ### setting a reference line (zorder=1; behind)
    ax.axvline(x=vline, c=col[2], linestyle='--', zorder=1, linewidth=1)
    ### getting data above threshold
    above = data[data[y_column] >= threshold]
    xs = above[x_column]
    ys = above[y_column]
    # kwargs
    new_sig_kwargs = _update_kwargs(
        update_dict=scatter_sig_kwargs_dict,
        edgecolor=(1, 1, 1, 0), zorder=2, c=col[0], s=msize,
    )
    ax.scatter(xs, ys, **new_sig_kwargs)
    ### getting data below threshold
    below = data[data[y_column] < threshold]
    xns = below[x_column]
    yns = below[y_column]
    # kwargs
    new_nonsig_kwargs = _update_kwargs(
        update_dict=scatter_nonsig_kwargs_dict,
        edgecolor=(1, 1, 1, 0), zorder=2, linewidths=0.0, s=msize,
        alpha=transparency_ns, c=col[1],
    )
    ax.scatter(xns, yns,  **new_nonsig_kwargs,)
    ### adding annotations
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ### do we want to set the ylim
    if not ylim is None:
        ax.set_ylim(ylim[0], ylim[1])
    # adjust text only if labels are specified
    if not point_label is None:
        # check if column is present
        if not point_label in data.columns:
            raise IndexError('`point_label` is not present in data.columns.')
        # get text, do we want to subset
        if not index_label is None:
            text_data = data.loc[index_label]
            above = text_data[text_data[y_column] >= threshold]
            xs = above[x_column]
            ys = above[y_column]
        try:
            # NOTE warpping this in try/finally to reset the default font.
            default_font = plt.rcParams[FT_FAM]
            if not font_label is None:
                plt.rcParams[FT_FAM] = font_label
            # getting the actual labels
            texts = []
            for x, y, l in zip(xs, ys, above[point_label]):
                texts.append(ax.text(x, y, l, size=lsize))
            if adjust:
                new_label_kwargs = _update_kwargs(
                    update_dict=label_kwargs_dict,
                    lim=lim, zorder=3, ax=ax,
                    arrowprops=dict(arrowstyle="-", color='k', lw=0.5),
                )
                adjust_text(texts, **new_label_kwargs,)
        finally:
            plt.rcParams[FT_FAM] = default_font
    # return the figure and axes
    return f, ax
