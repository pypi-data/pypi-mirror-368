"""
Incidence matrix plotting for categorical heatmaps and set visualisation.

This module provides a plotting function for drawing incidence matrices,
where each cell in a 2D grid is populated with a marker (dot) based on the
underlying matrix value. This is useful for visualising categorical
presence/absence patterns, binary annotations, or simplified heatmaps
without continuous shading.

The visual output is a grid of vertical and horizontal lines forming an
n-by-m lattice, with overlaid points coloured and sized according to
user-defined thresholds and formatting options.

Functions
---------
draw_incidencematrix(data, fsize=(6,6), ...)
    Draws a categorical incidence matrix, customising grid lines, dot styles,
    and axis labels using a DataFrame as input.

Notes
-----
Each dot is rendered using `matplotlib.pyplot.scatter`, and horizontal/vertical
lines define the grid. The mapping of dot appearance to values is governed by
user-supplied breakpoints and style parameters. Optional keyword dictionaries
enable fine-grained customisation of scatter and line elements.
"""

# importing
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
from typing import (
    Any,
    Literal,
)
from plot_misc.constants import (
    NamesIncidenceMatrix as NamesIM,
    Real,
)
from plot_misc.utils.utils import _update_kwargs
from plot_misc.errors import (
    is_type,
    is_df,
    are_columns_in_df,
    # same_len,
    Error_MSG,
)

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def draw_incidencematrix(
    data:pd.DataFrame, fsize:tuple[Real, Real]=(3,4),
    dot_colour:list[tuple[str, Real]]=[('grey',0), ('black',1)],
    dot_size:list[Real] | list[tuple[Real, Real]]=[4, 8],
    dot_transparency:list[Real] | list[tuple[Real, Real]]=[0.9, 1.0],
    line_colour:tuple[str, str]=('lightgrey', 'lightgrey'),
    lw:tuple[float, float]=(0.3, 0.3),
    tick_lab_size:tuple[float, float]=(4.5, 4.5),
    tick_len:tuple[float,float]=(2.0, 2.0),
    tick_w:tuple[float,float]=(0.3, 0.3),
    margins:tuple[float,float] | None = None,
    grid_position:Literal['outline', 'centre'] | None = 'centre',
    ax:plt.Axes | None = None,
    break_limits:tuple[float, float] = (-np.inf, np.inf),
    size_data: pd.DataFrame | None = None,
    transparency_data: pd.DataFrame | None = None,
    kwargs_scatter_dict:dict[Any,Any] | None = None,
    kwargs_vline_dict:dict[Any,Any] | None = None,
    kwargs_hline_dict:dict[Any,Any] | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """
    Draw a categorical heatmap to visualise an incidence matrix.
    
    This function plots a square grid where each cell is populated
    with a dot, based on the value in the input matrix. Dot colour, size,
    and transparency are mapped to user-defined thresholds, allowing flexible
    binary or ordinal heatmap-style visualisations for presence/absence or
    category membership.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        A matrix of shape (n_rows, n_columns). Index and column labels are used
        for the y-axis and x-axis ticks, respectively. Values are mapped to
        dot attributes based on `dot_colour`.
    fsize : `tuple` [`float`, `float`], default (6.0, 6.0)
        Width and height of the figure in inches.
    dot_colour : `list` [`tuple` [`str`, `float`]], default [('grey', 0), ('black', 1)]
        A list of (colour, upper bound) tuples defining dot appearance by value.
        Each dot is coloured according to the first `cut` for which the value is
        less than or equal to `cut` and greater than the previous break.
        
        The default: [('grey',0), ('black',1)], colours dots grey for value in
        (\\infinity, 0], and colours dots black for values in (0, 1].
    line_colour : `tuple` [`str`, `str`], default ('lightgrey', 'lightgrey')
        Colours of vertical and horizontal grid lines.
    dot_size : `list` [`float`], default [4, 8]
        Size of dots corresponding to each threshold in `dot_colour`. Can also
        be supplied a list of tuple similar to `dot_colour`. The cut-offs
        can be based on the `data` values or on a separately supplied
        `size_data` of equal dimmension to `data`.
    dot_transparency : `list` [`float`], default [0.9, 1.0]
        Alpha transparency values for dots in each category. Can also be
        supplied a list of tuple similar to `dot_colour`. The cut-offs
        can be based on the `data` values or on a separately supplied
        `transparency_data` of equal dimmension to `data`.
    lw : tuple [`float`, `float`], default (0.3, 0.3)
        Line width for vertical and horizontal grid lines.
    tick_lab_size : `tuple` [`float`, `float`], default (4.5, 4.5)
        Font size of x- and y-axis tick labels.
    tick_len : `tuple` [`float`, `float`], default (2, 2)
        Tick length for x- and y-axes.
    tick_w : `tuple` [`float`, `float`], default (0.3, 0.3)
        Tick width for x- and y-axes.
    margins : `tuple` [`float`, `float`], optional
        Margins to apply along the x- and y-axes.
    grid_position : {'centre', 'outline'}, default 'centre'
        Whether to draw lines through cell centres or between cells.
    ax : `plt.axes` or `None`, default `None`
        If provided, the plot is drawn on this axis. Otherwise, a new figure
        and axis are created.
    break_limits : `tuple` [`float`, `float`], default (-np.inf, np.inf)
        Lower and upper bounds for the first and final break. Used to define
        open-ended ranges in dot colouring. Currently only uses the lower
        bound.
    kwargs_*_dict : `dict` [`any`, `any`] or `None`, default None
        Optional arguments supplied to the various plotting functions:
            kwargs_scatter_dict        --> ax.scatter
            kwargs_vline_dict          --> ax.vline
            kwargs_hline_dict          --> ax.hline
        
    Returns
    -------
    fig : `matplotlib.figure.Figure`
        The matplotlib figure containing the plot.
    ax : `matplotlib.axes.Axes`
        The axis containing the plotted incidence matrix.
    
    Notes
    -----
    The appearance of the matrix is governed by the breakpoints defined in
    `dot_colour`, and optionally `dot_size` and `dot_transparency. The latter
    two can take a list of floats to be applied at the same cut-offs as
    `dot_colour`.  One can also provide fewer values than `len(dot_colour)`
    for `dot_size` or `dot_transparency`, these are automatically broadcast.
    A list with tuples can be used to define custom cut-points for size and
    transparency.
    
    Missing or non-matching entries in the input matrix will be ignored.
    """
    SHAPE_ERR = ('`data` and `{0}` should have the same shapes '
                 'not: {1} and {2}, respectively.')
    # check inputs
    is_type(dot_size, list)
    is_type(dot_colour, list)
    is_type(dot_transparency, list)
    is_type(ax,(type(None), plt.Axes))
    is_df(data)
    is_type(grid_position, (str, type(None)))
    is_type(size_data, (type(None), pd.DataFrame))
    is_type(transparency_data, (type(None), pd.DataFrame))
    # check literals
    EXP_GRID = [NamesIM.GRID_POS_B, NamesIM.GRID_POS_O]
    if grid_position is not None and not grid_position in EXP_GRID:
        raise ValueError(
            Error_MSG.INVALID_STRING.format(
                'grid_position', EXP_GRID))
    # make sure all the data have the same shape
    if size_data is not None and data.shape != size_data.shape:
        raise IndexError(
            SHAPE_ERR.format('size_data', data.shape, size_data.shape
                             ))
    if transparency_data is not None and data.shape != transparency_data.shape:
        raise IndexError(
            SHAPE_ERR.format('transparency_data', data.shape,
                             transparency_data.shape
                             ))
    # transpose - hack to make the output match the input row,col and order.
    data = data.iloc[::-1].T
    if transparency_data is not None:
        transparency_data = transparency_data.iloc[::-1].T
    if size_data is not None:
        size_data = size_data.iloc[::-1].T
    # map None to dict
    kwargs_scatter_dict = kwargs_scatter_dict or {}
    kwargs_vline_dict = kwargs_vline_dict or {}
    kwargs_hline_dict = kwargs_hline_dict or {}
    # if one value is supplied, multiply the number of dot_colour elements
    ndots = len(dot_colour)
    if len(dot_size) == 1:
        dot_size = dot_size * ndots
    if len(dot_transparency) ==1:
        dot_transparency = dot_transparency * ndots
    # # further tests
    # same_len(dot_colour, dot_size, ['dot_colour','dot_size'])
    # same_len(dot_colour, dot_transparency, ['dot_colour','dot_transparency'])
    # do we need to make an axis
    if ax is None:
        f, ax = plt.subplots(figsize=(fsize[0], fsize[1]))
    else:
        f = ax.figure
    # get colour maps
    dot_colours_arr = _map_attributes(data, dot_colour,
                                      break_limits=break_limits)
    # get size maps
    size_input = size_data if size_data is not None else data
    if all(isinstance(x, Real) for x in dot_size) == True:
        new_dot_size = [(n, i[1]) for n, i in zip(dot_size, dot_colour)]
    else:
        new_dot_size = dot_size
    dot_size_arr = _map_attributes(size_input, new_dot_size,
                                   break_limits=break_limits)
    # get transparency maps
    transparency_input = (
        transparency_data if transparency_data is not None else data)
    if all(isinstance(x, Real) for x in dot_transparency) == True:
        new_dot_transparency=\
            [(n, i[1]) for n, i in zip(dot_transparency, dot_colour)]
    else:
        new_dot_transparency = dot_transparency
    dot_transparency_arr = _map_attributes(
        transparency_input, new_dot_transparency,
        break_limits=break_limits)
    # the x and y coordinates
    M, N = data.shape
    x, y = np.meshgrid(np.arange(M), np.arange(N))
    xv = x.T.ravel()
    yv = y.T.ravel()
    col_flat = dot_colours_arr.ravel()
    size_flat = dot_size_arr.ravel().astype(float)
    alpha_flat = dot_transparency_arr.ravel().astype(float)
    ################
    # plot dots, size, and alpha
    for col in np.unique(col_flat):
        mask = col_flat == col
        if not np.any(mask):
            continue
        # sort out kwargs
        new_scatter_kwargs = _update_kwargs(update_dict=kwargs_scatter_dict,
                                            edgecolor='black',
                                            linewidths=0.0,
                                            s=size_flat[mask],
                                            alpha=alpha_flat[mask],
                                            c=col, zorder=3,
                                            )
        ax.scatter(
            xv[mask], yv[mask],
            **new_scatter_kwargs,)
    ################
    # adding grid lines
    if grid_position is not None:
    # if grid_position is not None and grid_position == 'centre':
        new_vline_kwargs = _update_kwargs(update_dict=kwargs_vline_dict,
                                          c=line_colour[1], linestyle='-',
                                          linewidth=lw[1], zorder=1,
                                          )
        _draw_grid(x, ax, axis = 'y', grid_position=grid_position,
                   **new_vline_kwargs)
        new_hline_kwargs = _update_kwargs(update_dict=kwargs_hline_dict,
                                          c=line_colour[0], linestyle='-',
                                          linewidth=lw[0], zorder=1,
                                          )
        _draw_grid(x, ax, axis = 'x', grid_position=grid_position,
                   **new_hline_kwargs)
    # ticks
    ax.set(xticks=np.arange(x.shape[1]), yticks=np.arange(x.shape[0]),
           xticklabels=data.index, yticklabels=data.columns)
    ax.tick_params(axis="x", labelsize=tick_lab_size[0], length=tick_len[0],
                   width=tick_w[0], rotation=90)
    ax.tick_params(axis="y", labelsize=tick_lab_size[1], length=tick_len[1],
                   width=tick_w[1])
    # trim margin
    if not margins is None:
        ax.margins(x=margins[0], y=margins[1])
    # return the figure and axes
    return f, ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _map_attributes(data:pd.DataFrame, list_map: list[tuple[Any, Real]],
                    break_limits:tuple[float, float] = (-np.inf, np.inf),
                    ) -> np.ndarray:
    """
    Map values from a DataFrame to discrete attributes based on thresholds.
    
    This function assigns each element in the input `data` a corresponding
    attribute (e.g., colour, size, or alpha) using a list of thresholded
    rules provided in `list_map`. Each rule is a tuple of the form
    `(attribute_value, upper_bound)`, and values are mapped according to
    which threshold interval they fall into.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        A numeric matrix of shape (N, M) to be mapped.
    list_map : `list` [`tuple` [`any`, `real`]]
        A list of (attribute, upper_bound) pairs. Each value in the input
        data is mapped to the `attribute` if it lies in the open-closed
        interval (previous_bound, upper_bound]. The list is automatically
        sorted by `upper_bound`.
    break_limits : `tuple` [`float`, `float`], default (-np.inf, np.inf)
        Tuple specifying the lower and upper bounds for the mapping. The first
        threshold interval begins just above `break_limits[0]`. The upper bound
        is not currently used, but is included for future expansion.
    
    Returns
    -------
    np.ndarray
        A NumPy array of the same shape as `data`, with each element replaced
        by the mapped attribute.
    
    Notes
    -----
    The rules are applied sequentially after sorting by `upper_bound`, and
    values outside the defined breakpoints are assigned `np.nan`.
    
    Examples
    --------
    >>> data = pd.DataFrame([[0.2, 0.6], [1.2, 2.5]])
    >>> rules = [('grey', 0.5), ('black', 1.5), ('red', 3)]
    >>> _map_attributes(data, rules)
    array([['grey', 'black'],
           ['black', 'red']], dtype=object)
    """
    # check input
    is_type(list_map, list)
    is_type(break_limits, tuple)
    is_df(data)
    # get values
    vals = data.to_numpy()
    # sortting the rule based on the second tuple element
    rule_sorted = sorted(list_map, key=lambda x: x[1])
    # apply rule
    mapped_vals = np.full_like(vals, np.nan, dtype=object)
    cut_low = break_limits[0]
    for col, cut_high in rule_sorted:
        sel = (vals > cut_low) & (vals <= cut_high)
        mapped_vals[sel] = col
        cut_low = cut_high
    # return
    return mapped_vals

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _draw_grid(arr:np.ndarray, ax:plt.Axes,
               axis:Literal['x','y','both'] = 'both',
               grid_position: Literal['centre', 'outline'] = 'centre',
               **kwargs,) -> None:
    """
    Draws grid lines across or around the provide coordinates.
    
    Parameters
    ----------
    arr : `np.ndarray`
        A 2D array off coordinates.
    ax : `matplotlib.axes.Axes`
        The axis on which to draw the grid lines.
    axis : {'x', 'y', 'both'}, default 'both'
        Which axis to draw grid lines for.
    grid_position : {'centre', 'outline'}, default 'centre'
        Whether to draw lines through cell centres or between cells.
    **kwargs
        Additional keyword arguments passed to `ax.axvline` and/or
        `ax.axhline`.
    
    Returns
    -------
    None
    """
    # check input
    is_type(arr, np.ndarray)
    is_type(ax,plt.Axes)
    EXP_GRID = [NamesIM.GRID_POS_B, NamesIM.GRID_POS_O]
    if grid_position is not None and not grid_position in EXP_GRID:
        raise ValueError(
            Error_MSG.INVALID_STRING.format(
                'grid_position', EXP_GRID))
    EXP_AXIS = [NamesIM.AXIS_X, NamesIM.AXIS_Y, NamesIM.AXIS_B]
    if not axis in EXP_AXIS:
        raise ValueError(
            Error_MSG.INVALID_STRING.format(
                'axis', EXP_AXIS))
    # what type of grid - the first type will plot across the dot centers
    # the second type will place the grid around the dots.
    x_vals = (np.arange(arr.shape[1]) if grid_position == 'centre'
              else np.arange(-0.5, arr.shape[1], 1.0))
    y_vals = (np.arange(arr.shape[0]) if grid_position == 'centre'
              else np.arange(-0.5, arr.shape[0], 1.0))
    # finally set grid
    if axis in ['x', 'both']:
        for xv in x_vals:
            ax.axvline(x=xv, **kwargs)
    if axis in ['y', 'both']:
        for xy in y_vals:
            ax.axhline(y=xy, **kwargs)

