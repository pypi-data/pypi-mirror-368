"""
This module provides functions and classes to construct forest plots,
annotated side tables, and compatibility (empirical support) plots.

Results are returned as structured result classes, and plotting functions
allow fine-grained control via `kwargs_*_dict` arguments passed directly to
matplotlib primitives.

Classes
-------
ForestPlot
    A class to draw a forest plot, with point estimates and confidence
    intervals.

EmpericalSupport
    A class to compute and visualise empirical support (or compatibility)
    intervals for a given estimate and standard error across a range of
    alpha (i.e. type 1 error) values.

EmpericalSupportPlotResults
    Stores the full results table and estimate from an empirical support plot.

Functions
---------
plot_table
    Annotate a matplotlib axes with a table aligned to a forest plot.

set_y_coordinates
    Assigns y-axis coordinates to rows of a dataframe based on groupings
    and spacing rules.

"""

# imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import warnings
from scipy.stats import norm
from typing import (
    Any,
    Literal,
    Sequence,
)
from plot_misc.utils.utils import (
    _update_kwargs,
    plot_span,
    segment_labelled,
    Results,
)
from plot_misc.constants import (
    ForestNames as FNames,
    Real,
)
from plot_misc.errors import (
    is_type,
    is_df,
    is_series_type,
    are_columns_in_df,
    InputValidationError,
    Error_MSG,
)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Class

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class EmpericalSupportPlotResults(Results):
    """
    Results container for empirical support visualisations.
    
    This class stores results from the `EmpericalSupport` visualisation
    workflow, including the point estimate and the full data table used for
    plotting.
    
    Attributes
    ----------
    estimate : `float`
        The point estimate.
    data_table : `pd.DataFrame`
        A DataFrame with the following columns:
        
        - `estimate` : The repeated point estimate.
        - `lower` : The lower bound of the confidence interval for each alpha.
        - `upper` : The upper bound of the confidence interval for each alpha.
        - `p_value` : The input alpha value (type I error).
        - `ci` : The corresponding confidence level, i.e. `1 - alpha`.
    """
    SET_ARGS = [
        FNames.ESTIMATE,
        FNames.data_table,
    ]
    # /////////////////////////////////////////////////////////////////////////
    # Initiation the class
    def __init__(self, **kwargs):
        super().__init__(set_args=self.SET_ARGS, **kwargs)

# #############################################################################
# functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def order_row(data:pd.DataFrame, order_outer:dict[str,list[str]],
              order_inner:dict[str,list[str]] | None = None
              ) -> pd.core.frame.DataFrame:
    """
    Order rows in a DataFrame according to custom group and subgroup lists.
    
    This function reorders a DataFrame by one or two hierarchical levels
    (e.g., outer group then inner subgroup), based on user-specified ordering
    lists. Only one outer and one inner ordering level are allowed.
    For example, a table can be ordered by study and within study by outcome.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        The DataFrame to reorder.
    oder_outer : `dict` [`str`, `list` [`str`]]
        A dictionary with a single key representing the outer grouping column,
        and a list defining the desired order of values in that column.
    order_inner : `dict` [`str`, `list` [`str`]] or `None`, default `None`
        A dictionary with a single key representing a secondary grouping column,
        and a list defining the desired within-group order.
    
    Returns
    -------
    pd.DataFrame
        A reordered copy of the original DataFrame.
    
    Raises
    ------
    AttributeError
        If more than one key is provided in either `order_outer` or `order_inner`.
    IndexError
        If the shape of the output differs from the input.
    """
    # check input
    AE_MSG = 'Please supply a `dict` of length one.'
    is_type(data, pd.DataFrame)
    is_type(order_outer, dict)
    is_type(order_inner, (type(None), dict))
    if len(order_outer) > 1:
        raise AttributeError(AE_MSG)
    if not order_inner is None:
        if len(order_inner) > 1:
            raise AttributeError(AE_MSG)
    # ### algorithm
    size_in = data.shape
    outer_col = list(order_outer.keys())[0]
    outer_lst = list(order_outer.values())[0]
    order_data = pd.DataFrame()
    # loop over outer order
    for sel_outer in outer_lst:
        slice_outer = data.loc[data[outer_col] == sel_outer]
        # do we have an inner order
        if not order_inner is None:
            inner_col = list(order_inner.keys())[0]
            inner_lst = list(order_inner.values())[0]
            inner_data = pd.DataFrame()
            for sel_inner in inner_lst:
                slice_inner = slice_outer.loc[
                    slice_outer[inner_col] == sel_inner]
                inner_data = pd.concat([inner_data, slice_inner])
                #end loop
            slice_outer = inner_data
            # end inner
        order_data = pd.concat([order_data, slice_outer])
    # ### check output
    if order_data.shape != size_in:
        IndexError('Input and output shape are distinct!')
    # return
    return order_data

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def set_y_coordinates(data:pd.DataFrame,
                      group: str | None = None,
                      strata_within_group: str | None = None,
                      within_pad:Real=2,
                      between_pad:Real= 4,
                      start:Real=1,
                      new_col:str='y_axis',
                      sort_dict:Literal['skip'] | dict[str, int] | None = 'skip',
                      ) -> pd.DataFrame:
    """
    Assigns numeric y-axis coordinates to rows, with optional grouping and
    padding.
    
    This function adds a new column (default 'y_axis') to the DataFrame, giving
    each row a numeric y-coordinate. Grouped entries are spaced using different
    padding for within-group and between-group spacing. Optionally supports
    strata within groups and custom sorting.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        The dataframe to which you want to add y-coordinates.
    group : `str` or `None`, default `Nonetype`
        A column in `data` recording the group memberships. Will assign
        `within_pad` to rows that have the same group membership, and
        `between_pad` between distinct group values.
        
        >>> `for within_pad = 2; between_pad = 4; start = 1`
        >>> group   y
            x       1
            x       3
            y       7
            y       9
            
    strata_within_group : `str` or `None` , default `NoneType`
        A column in `data` providing additional grouping information.
        Use this to ensure that rows with distinct strata values but the same
        group value receive the same y-coordinate.
        
        >>> `for within_pad = 2; between_pad = 4; start = 1`
        >>> group       strata_within_group     y # pragma: no cover
            x           a                       1
            x           a                       3
            x           b                       1
            x           b                       3
            y           a                       7
            y           a                       9
            y           b                       7
            y           b                       9
        
    within_pad : `float`, default 2.0
        The distance between point estimates.
    between_pad : `float`, default 4.0
        The distance between groups of point estimates. This is the y-axis
        distance that will be skipped between the last y-axis coordinate in the
        previous group and the starting y-axis coordinate of the current group.
    start : `float` or `int`, default 1
        The starting position of the sequence.
    new_col : `str`, default `y_axis`
        The name of the column that will be added to `data`.
    sort_dict : `dict`, `str`, `None`, default `skip`
        Supply a key:value-float combination dictionary to sort the rows on
        `group` membership. Set to `NoneType` to order rows by
        `[order, strata]`. Set to `skip` to not sort.
    
    Returns
    -------
    pd.DataFrame
        Copy of the input DataFrame with the added `new_col` column.
    
    Raises
    ------
    ValueError
        If `strata_within_group` is provided without `group`, or if `sort_dict`
        is invalid.
    KeyError
        If the input index is not unique.
    """
    df = data.copy()
    # check input
    is_df(df)
    is_type(group, (type(None), str))
    is_type(strata_within_group, (type(None), str))
    is_type(new_col, str)
    is_type(start, (int, float))
    is_type(within_pad, (int, float))
    is_type(between_pad, (int, float))
    is_type(sort_dict, (type(None), dict, str))
    cols = []
    if isinstance(sort_dict, str) and sort_dict != 'skip':
        raise ValueError('`sort_dict` string values is restricted to `skip`.')
    # raise warning if duplicate index
    if df.index.has_duplicates:
        raise KeyError('`data.index` contains duplicate values, please '
                       'ensure the index is unique: `data.reset_index`.')
    # check group and group_by_strata
    if group is not None:
        cols = [group]
    if (strata_within_group is not None) & (group is None):
        raise ValueError('please also provide `group` when using '
                         '`strata_within_group`.')
    if strata_within_group is not None:
        cols = cols + [strata_within_group]
    are_columns_in_df(df, expected_columns=cols)
    # sort index to group column values together
    if sort_dict is None:
        # sort by group value
        df.sort_values(by=cols, inplace=True)
    elif sort_dict == 'skip':
        # do nothing
        pass
    else:
        # sort by custom order
        order=FNames.order_col
        df[order] = df[group].map(sort_dict)
        # by_list
        by_list = [order]
        if strata_within_group is not None:
            by_list.append(strata_within_group)
        # sort by values
        df.sort_values(by=by_list, inplace=True)
        del df[order]
    # ### setting the y_coordinates
    y_coords = pd.Series(index=df.index, dtype=float)
    current_y = start
    if group is None:
        # NO group
        for idx in df.index:
            y_coords[idx] = current_y
            current_y +=within_pad
    elif strata_within_group is None:
        # ONLY GROUP, NO STRATA
        for g in df[group].unique():
            sub = df[df[group] == g]
            for idx in sub.index:
                y_coords[idx] =  current_y
                current_y +=within_pad
            # update after group finished
            current_y = y_coords.max() + between_pad
    else:
        # GROUP AND STRATA
        # temporarily order if needed.
        if isinstance(sort_dict, dict) == False:
            ORG_ORDER = '_original_order'
            df[ORG_ORDER] = range(len(df))
            df.sort_values(by=cols, inplace=True)
        # get y-coordinates
        y_coords = pd.Series(index=df.index, dtype=float)
        current_y = start
        for g in df[group].unique():
            sub = df[df[group] == g]
            for s in sub[strata_within_group].unique():
                strat = sub[sub[strata_within_group] == s]
                # update start after each strata itt.
                start = current_y
                for idx in strat.index:
                    y_coords[idx] =  current_y
                    current_y +=within_pad
                    # record the maximum value
                # reset after strata finished
                current_y = start
            # update after the group
            # NOTE simply taking the max value of the recorded y_coords
            current_y = y_coords.max() + between_pad
        # revert original order
        if isinstance(sort_dict, dict) == False:
            df.sort_values(by=ORG_ORDER, inplace=True)
            df.drop(columns=[ORG_ORDER], inplace=True)
    # ### add to df
    df[new_col] = y_coords
    # return stuff
    return df

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ForestPlot(object):
    """
    A class to create a forest plot using matplotlib.
    
    This plot displays point estimates with optional confidence intervals on a
    Cartesian coordinate system. It can display grouped estimates, optionally
    connected by line segments when their vertical position (`y_col`) is shared.
    Horizontal spans may be included to visually distinguish groups.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        The input data containing the Cartesian coordinates and labels used
        for plotting.
    x_col : `str`
        The column name of the x-axis values (e.g. point estimates).
    y_col : `str`, default `y_axis`
        Column with y-axis coordinates for each estimate (must be numeric).
    lb_col : `str` or `None`, default None
        The column name of the lower bound of an confidence interval.
    ub_col : `str` or `None`, default None
        The column name of the upper bound of an confidence interval.
    g_col : `str` or `None`, default `NoneType`
        The column name of the group indicator; often the outcome or study
        indicator.  This column will be used to provide y-axis ticklabels.
        If None, a column with a unique value for each row will be
        added - so there are no groups.
    ax : `plt.axes` or `None`, default `NoneType`
        Optional existing axis to plot on. If None, a new figure and axis are
        created.
    figsize : `tuple` [`real`, `real`], default (6.0,6.0),
        The figure size in inches, when ax is set to None.
    
    Attributes
    ----------
    figure : matplotlib.figure.Figure
        The figure object used for plotting.
    ax : matplotlib.axes.Axes
        The axes object used for plotting.
    span_dict : dict[int, dict[str, Any]]
        A dictionary specifying vertical spans (e.g., for grouping rows or adding
        shaded bands in a forest plot). Each key represents a group index or
        identifier. The value must be a dictionary containing:
        
        - 'min' : float
            The lower bound of the span in data coordinates.
        - 'max' : float
            The upper bound of the span in data coordinates.
        - 'kwargs' : dict
        A dictionary of keyword arguments to be passed to the span plotting
        function (e.g., `ax.axhspan()`), such as `facecolor`, `alpha`,
        `zorder`, etc.
    
    Notes
    -----
    To render the plot, call the `.plot()` method after instantiation.
    """
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def __init__(self, data:pd.DataFrame,
                 x_col:str, y_col:str='y_axis',
                 lb_col:str | None = None,
                 ub_col:str | None = None,
                 g_col:str | None = None,
                 ax:plt.Axes | None = None,
                 figsize:tuple[Real,Real]=(6.0, 6.0),
                 ):
        """
        Sets up the figure and axes objects, and performs the first input
        checks.
        """
        # ### check input
        is_df(data)
        is_type(ax, (type(None), plt.Axes))
        is_type(x_col, str)
        is_type(y_col, str)
        is_type(lb_col, (type(None), str))
        is_type(ub_col, (type(None), str))
        is_type(g_col, (type(None),str))
        # ### confirm column content
        are_columns_in_df(data, [x_col, y_col, lb_col, ub_col, g_col])
        is_series_type(data[x_col], (float, int))
        try:
            is_series_type(data[y_col], (float, int))
        except InputValidationError: # pragma: no cover
            raise InputValidationError(
                '`y_col` should refer to a column containing '
                'integers or floats. These are used to as '
                'y-value in a Cartesian coordinates system. '
                'Please refer to: '
                'https://en.wikipedia.org/wiki/Cartesian_coordinate_system .'
            )
        # if (ub_col is not None) and (lb_col is not None):
        #     is_series_type(data[[ub_col, lb_col]], (float, int))
        if ub_col is not None:
            is_series_type(data[ub_col], (float, int))
        if lb_col is not None:
            is_series_type(data[lb_col], (float, int))
        # ### create an axes if needed
        if ax is None:
            f, ax = plt.subplots(figsize=figsize)
        else:
            f = ax.figure
        # ### assign to self
        self.figure = f
        self.ax = ax
        self._plot = False
        setattr(self, FNames.forest_data, data.copy())
        self.x_col = x_col
        self.y_col = y_col
        self.lb_col = lb_col
        self.ub_col = ub_col
        self.g_col = g_col
        # set to defaults
        self.span_dict: dict[int, dict[str, Any]] = {}
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def _marker_aesthetics(self, s_col, c_col, a_col, verbose:bool=False,
                           ) -> list[str]:
        """
        Ensure shape, colour, and alpha columns exist in the dataset.
         
        If the specified shape, colour, or alpha columns are not found in the
        dataset, this function adds them with the provided fallback values.
        
        Parameters
        ----------
        s_col : `str`
            Shape marker or column name for marker style.
        c_col : `str`
            Colour or column name for marker colour.
        a_col : `float` or `str`
            Alpha value or column name for transparency.
        verbose : 'bool', default False
            If True, will emit warnings for each column that is created.
        
        Returns
        -------
        list of str
            Names of the columns used for shape, colour, and alpha.
        """
        s_col_name = (s_col, FNames.s_col)
        c_col_name = (c_col, FNames.c_col)
        a_col_name = (a_col, FNames.a_col)
        new_names = []
        for cn, n_cn in [s_col_name, c_col_name, a_col_name]:
            if cn not in getattr(self, FNames.forest_data).columns:
                getattr(self, FNames.forest_data)[n_cn] = cn
                # update name
                new_names.append(n_cn)
                if verbose == True:
                    warnings.warn(f"`{cn}` not found in `data`, creating `{n_cn}` "
                                  f"column with value `{cn}`.", RuntimeWarning)
            else:
                new_names.append(cn)
        # return
        return new_names
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def plot(self, s_col:str='o', s_size_col: str | Real = 40,
             c_col:str='black', a_col: float | str = 1,
             ci_lwd:float=2, ci_colour:str='indianred',
             connect_shape:bool = False, connect_shape_colour:str='black',
             connect_shape_lwd:float=1,
             span:bool = True, span_colour:list[str] = ['white','lightgrey'],
             reverse_y:bool=True, verbose:bool=False,
             ylim:tuple[float,float] | None = None,
             kwargs_scatter_dict:dict[Any,Any] | None = None,
             kwargs_plot_ci_dict:dict[Any,Any] | None = None,
             kwargs_connect_segments_dict:dict[Any,Any] | None = None,
             kwargs_span_dict:dict[Any,Any] | None = None,
             ) -> tuple[plt.Figure, plt.Axes]:
        """
        Generate a forest plot using the stored configuration and data.
        
        This method draws points and their confidence intervals, with options
        for custom styling, background spans, and segment connections.
        
        Parameters
        ----------
        s_col : `str`, default `o`
            The column name of the shape indicators.
            If string is not found in `self.data` the string value will be
            added to an `s_col` column.
        s_size_col : `str`, or `real` , default 40
            The column name of the `shape size` value for each point. Can also
            simply supply a `float` for a uniform shape.
        c_col : `str`, default `black`
            The column name of the shape colour indicators. If string is not
            found in `self.data` the string value will be added to a
            `c_col` column.
        a_col : float or str, default 1
            The column name of the alpha value for each point. If the string is
            not found in `self.data`, the float will be added to an `a_col`
            column.
        ci_lwd : `float`, default 1
            The line width of the confidence intervals.
        ci_colour : `float`, default 'indianred'
            The line colour of the confidence intervals
        connect_shape : `bool`, default `False`
            If the point estimates should be connected with a line.
            Only relevant when estimates have the same y-axis value.
        connect_shape_colour : `str`, default `grey`
            The line colour.
        connect_shape_lwd : `float`, default 1.0
            The line width.
        span : `bool`, default `True`
            Whether an colour-interchanging horizontal background segment
            should be added
        span_colour : `list` [`str`, `str`], default ['white', 'lightgrey']
            The colours of the span.
        ylim : `tuple` [`float`, `float`] or `None`, default `NoneType`
            Overwrite the default standard y-limits.
        reverse_y : `bool`, default `True`
            inverts the y-axis.
        kwargs_scatter_dict : `dict` [`any`,`any`], or `None`, default `None`
            Extra arguments passed to `ax.scatter`.
        kwargs_plot_ci_dict : `dict` [`any`,`any`], or `None`, default `None`
            Extra arguments passed to `ax.plot` for CI lines.
        kwargs_connect_segments_dict : `dict` [`any`,`any`], or `None`, default `None`
            Extra arguments passed to `ax.plot` for shape connectors.
        kwargs_span_dict : `dict` [`any`,`any`], or `None`, default `None`
            Extra arguments passed to `ax.axhspan` for background bands.
        
        Returns
        -------
        matplotlib.figure.Figure
            The matplotlib figure object.
        matplotlib.axes.Axes
            The matplotlib axes containing the forest plot.
        """
        # ### check input
        is_type(s_col, str)
        is_type(c_col, str)
        is_type(a_col, (int,float, str))
        is_type(s_size_col, (str,int,float))
        is_type(ci_lwd, (int, float))
        is_type(ci_colour, str)
        is_type(connect_shape, bool)
        is_type(span, bool)
        is_type(connect_shape_lwd, (int, float))
        is_type(connect_shape_colour, str)
        is_type(span_colour, list)
        is_type(reverse_y, bool)
        is_type(ylim, (type(None), tuple))
        # ### set defauls
        # replace None by empty dict
        kwargs_scatter_dict = kwargs_scatter_dict or {}
        kwargs_plot_ci_dict = kwargs_plot_ci_dict or {}
        kwargs_connect_segments_dict = kwargs_connect_segments_dict or {}
        kwargs_span_dict = kwargs_span_dict or {}
        # set default shape and colour and alpha
        s_col_name, c_col_name, a_col_name =\
            self._marker_aesthetics(s_col, c_col, a_col, verbose=verbose)
        # make each row a single group if needed.
        if self.g_col is None:
            self.g_col = FNames.g_col
            getattr(self, FNames.forest_data)[self.g_col] =\
                range(getattr(self, FNames.forest_data).shape[0])
        # set marker size column `s_size_col`
        if isinstance(s_size_col, str):
            # STEP 1: is it a string then it is assumed to be in `data`
            are_columns_in_df(getattr(self, FNames.forest_data), s_size_col)
            shape_size_name = s_size_col
        else:
            # STEP 2: if a number set default column name and assign to data
            shape_size_name = 'shape_size'
            getattr(self, FNames.forest_data)[shape_size_name] = s_size_col
        # ################## plot points and errors
        for _, row in getattr(self, FNames.forest_data).iterrows():
            # coordinates
            xs = row[self.x_col]
            ys = row[self.y_col]
            # updating kwargs dict
            new_scatter_kwargs = _update_kwargs(update_dict=kwargs_scatter_dict,
                                                s=row[shape_size_name],
                                                marker=row[s_col_name],
                                                c=row[c_col_name],
                                                alpha=row[a_col_name],
                                                zorder=2,
                                                )
            self.ax.scatter(x=xs, y=ys, **new_scatter_kwargs,
                       )
            # add confidene intervals
            # if none replace with the point estimate
            if self.lb_col is None:
                lb = xs
            else:
                lb = row[self.lb_col]
            if self.ub_col is None:
                ub = xs
            else:
                ub = row[self.ub_col]
            # plot
            x_values = [lb, ub]
            y_values = [ys, ys]
            # updating kwargs dict
            new_plot_ci_kwargs = _update_kwargs(update_dict=kwargs_plot_ci_dict,
                                                c=ci_colour, linewidth=ci_lwd,
                                                )
            self.ax.plot(x_values, y_values, **new_plot_ci_kwargs,
                    )
        # ################## aggregate coordinates
        # NOTE define min, max, mean as constants at the start
        group_y = getattr(self, FNames.forest_data).\
            groupby(self.y_col).agg({self.x_col: [FNames.min,FNames.max]}
                                                )
        y_locations = getattr(self, FNames.forest_data).groupby(
            self.g_col).agg({self.y_col: [FNames.mean,FNames.min,FNames.max]}
                                        )
        # ################## segments between points
        if connect_shape ==True:
            xg_value = [ [min, max] for min, max in zip(
                group_y[self.x_col,FNames.min],
                group_y[self.x_col,FNames.max])
                        ]
            yg_value = [ [yval, yval] for yval in  group_y.index]
            for xg, yg in zip(xg_value, yg_value):
                # only add segments if there are two distinct x-values
                if np.unique(xg).shape[0] == 2:
                    new_connect_segments_kwargs = _update_kwargs(
                        update_dict=kwargs_connect_segments_dict,
                        c=connect_shape_colour, linewidth=connect_shape_lwd,
                        zorder=1
                    )
                    self.ax.plot(xg, yg, **new_connect_segments_kwargs,
                            )
                else:
                    if verbose:
                        warnings.warn('The line segments have the same x-axis '
                                      'value, the line plotting will be '
                                      'skipped.', RuntimeWarning)
        # ################### calculate y-axis mid points
        y_locations = y_locations[self.y_col].sort_values(FNames.min)
        y_mid = []
        for r in range(y_locations.shape[0]):
            maxy = y_locations.iloc[r][FNames.max]
            try:
                miny = y_locations.iloc[r+1][FNames.min]
            except IndexError:
                miny = np.nan
            # get mid
            y_mid.append(np.nanmean([maxy, miny]))
        # ################### adjust y margins
        # adjust margin
        mima =list(getattr(self, FNames.forest_data).sort_values(
            self.y_col)[self.y_col])[:2]
        diff = mima[1] - mima[0]
        new_margins = [
            min(getattr(self, FNames.forest_data)[self.y_col]) - diff/2,
            max(getattr(self, FNames.forest_data)[self.y_col]) + diff/2]
        if ylim is not None:
            self.ax.set_ylim(ylim)
        else:
            self.ax.set_ylim(new_margins)
        # add the starting and endpoints
        y_mid.insert(0, y_locations.iloc[0][FNames.min])
        y_mid[-1] = self.ax.get_ylim()[1] # replace with y-axis limit
        # ################### Add horizontal segments
        # to store the span y-axis coordiniates, colours
        if span ==True:
            span_dict = {}
            # add segments
            for t in range(len(y_mid)-1):
                ymin = y_mid[t]
                try:
                    ymax = y_mid[t+1]
                except IndexError:
                    ymax = y_mid[t]
                # change every second step
                if t % 2 == 0:
                    col = span_colour[0]
                else:
                    col = span_colour[1]
                # plot
                new_span_kwargs = _update_kwargs(
                    update_dict=kwargs_span_dict,
                    color=col, zorder=0
                )
                plot_span(ymin, ymax, ax=self.ax,
                          **new_span_kwargs,
                           )
                # populate the span_dict
                span_dict[t] = {FNames.min:ymin, FNames.max:ymax,
                                FNames.kwargs:new_span_kwargs,
                                }
            # update attribute
            self.span_dict = span_dict
        # ################### add y-axis labels
        self.ax.set_yticks(y_locations[FNames.mean])
        self.ax.set_yticklabels(y_locations.index)
        # ################### invert y-axis
        if reverse_y == True:
            self.ax.invert_yaxis()
        # ################### return the figure, axis, and other
        return self.figure, self.ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def plot_table(
    data: pd.core.frame.DataFrame,
    ax: plt.Axes, string_col: str, xloc:Real=0.5, xloc_header:Real=0.5,
    halignment_text:str="center", halignment_header:str="center",
    valignment_text:str="center", valignment_header:str="center",
    negative_padding:Real=1.0, size_text:Real=10,
    size_header:Real=10, size_yticklabel:Real=10, y_col:str='y_axis',
    yticklabel: Sequence[str] | None = None,
    ytickloc: Sequence[Real] | None = None,
    l_yticklab_pad:str | None = None,
    r_yticklab_pad:str | None = None,
    annoteheader: str | None = None,
    span:dict[int, dict[str, Any]] | None =None,
    span_start:str='min',
    span_stop:str='max',
    span_kwargs:str='kwargs',
    kwargs_text_dict:dict[Any,Any] | None = None,
    kwargs_header_dict:dict[Any,Any] | None = None,
    kwargs_yticklabel_dict:dict[Any,Any] | None = None,
) -> plt.Axes:
    """
    Plot a side-aligned annotation table alongside a forest plot or similar
    y-structured figure, using `ax.text` and y-axis coordinates.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        Pandas DataFrame containg `string_col` that should be plotted.
        margin of error, etc.
    ax : plt.axes
            Axes to operate on.
    string_col : `str`,
            The the column name that should be plotted. Should contain a
            `string` value.
    y_col : `str`, default 'y_axis'
        Column in `dataframe` containing the vertical coordinates.
    xloc: `real`, default 0.5
        The position of the text **orthogonal to the axis**, given in **axes
        coordinates** (0 = bottom/left of axis, 1 = top/right). Negative values
        place the label outside the axis bounds.
    annoteheaders : `str` or `None`, default `NoneType`
        string to annotate the table column.
    xloc_header: `real`, 0.5
        Same as `xloc`.
    halignment_text : `str`, default "center"
        Horizontal alignment of the table text (`left`, `center`, `right`).
    halignment_header : `str`, default "center"
        Horizontal alignment of the header text.
    valignment_text : `str`, default "center"
        Vertical alignment of the table text (`top`, `center`, `bottom`).
    valignment_header : `str`, default "center"
        Vertical alignment of the header text.
    negative_padding : `real`, default 1.0
        Distance between the top of the axis and the table header in data
        coordinates. Determines the y-coordinate of the table header as:
        `ax.get_ylim()[1] - ngative_padding`
    size_text : `real`, default 10
        The font size for the table text.
    size_header : `real`, default 10
        The font size for the table header.
    size_yticklabel : `real`, default 10
        Font size of the y-axis tick labels (if used).
    yticklabel : `list` [`str`] or `None`, default `None`
        A list of string containing the y-axis labels. Should match the length
        of `ytickloc`.
    ytickloc : `list` [`real`] or `None`, default `None`
        A list of real values defining the y-axis locations for the ticks.
    l_yticklab_pad : str or `None`, default `None`
        Optional prefix to be added to each y-axis label.
    r_yticklab_pad : str or `None`, default `None`
        Optional suffix to be added to each y-axis label.
    annoteheader : `str` or `None`, default `None`
        Header label to display at the top of the table.
    span : `dict` [`int`, `dict` [`str`, `any`]] or `None`, default `NoneType`
        Whether you want to add an optional span. Supply a dictionary with
        k many unique keys and next dictionaries containing `min` and
        `max` coordinates and `kwargs`. This will all be supplied to
        `merit_helper.utils.utils.plot_span`.
    kwargs_text_dict : `dict` [`any`,`any`] or `None`, default `None`
        Additional arguments passed to `ax.text` for table entries.
    kwargs_header_dict : `dict` [`any`,`any`] or `None`, default `None`
        Additional arguments passed to `ax.text` for the header entry.
    kwargs_yticklabel_dict : `dict` [`any`,`any`] or `None`, default `None`
        Additional arguments passed to `ax.set_yticklabels`.
    
    Returns
    -------
    plt.Axes
        The axis object with the table rendered.
    """
    # ################### do check and set defaults
    is_df(data)
    is_type(y_col, str)
    is_type(ax, plt.Axes)
    is_type(string_col, str)
    is_type(xloc, (float, int))
    is_type(xloc_header, (float, int))
    is_type(annoteheader, (type(None), str))
    is_type(halignment_text, str)
    is_type(valignment_text, str)
    is_type(halignment_header, str)
    is_type(valignment_header, str)
    is_type(size_header, (float, int))
    is_type(size_text, (int, float))
    is_type(negative_padding, (float, int))
    is_type(l_yticklab_pad, (type(None), str))
    is_type(r_yticklab_pad, (type(None), str))
    is_type(yticklabel, (type(None), list))
    is_type(ytickloc, (type(None), list))
    is_type(span, (type(None), dict))
    # check if columns are in dataframe
    are_columns_in_df(data, expected_columns=[string_col, y_col])
    # set None to dict
    kwargs_text_dict = kwargs_text_dict or {}
    kwargs_header_dict = kwargs_header_dict or {}
    kwargs_yticklabel_dict = kwargs_yticklabel_dict or {}
    # ################### remove spines
    ax.spines[['top', 'right', 'bottom', 'left']].set_visible(False)
    # remove lables
    ax.xaxis.set_ticklabels([])
    # remove ticks
    ax.set_xticks([])
    # ################### add y-labels
    if (not yticklabel is None) and (ytickloc is None):
        raise ValueError('`ytickloc` should be supplied if `yticklabel` is defined.')
    if (yticklabel is None) and (not ytickloc is None):
        raise ValueError('`yticklabel` should be supplied if `ytickloc` is defined.')
    if (not yticklabel is None) and (not ytickloc is None):
        if len(yticklabel) != len(ytickloc):
            raise IndexError('`yticklabel` and `ytickloc` containts distinct values.')
        # add optional label padding
        if not l_yticklab_pad is None:
            yticklabel = [l_yticklab_pad + str(s) for s in yticklabel]
        if not r_yticklab_pad is None:
            yticklabel = [str(s) + r_yticklab_pad for s in yticklabel]
        # plot y-tick labels
        ax.set_yticks(ytickloc)
        # update kwargs for labels
        new_yticklabel_kwargs = _update_kwargs(
            update_dict=kwargs_yticklabel_dict,
            weight=FNames.fontweight,
            size=size_yticklabel,
        )
        ax.yaxis.set_ticklabels(yticklabel,
                                **new_yticklabel_kwargs,
                                )
        # remove the actual tick
        ax.tick_params(left=False)
    else:
        # remove y ticks
        ax.yaxis.set_ticklabels([])
        ax.set_yticks([])
    # ################### plot string column
    # mapping the x-axis to the 0 and 1 range.
    # NOTE get_yaxis_transform maps the x-axis to [0, 1] and the
    # y-axis to the data coordinate system.
    transform = ax.get_yaxis_transform()
    # tick labels
    for _, row in data.iterrows():
        yticklabel1 = row[y_col]
        yticklabel2 = row[string_col]
        if pd.isna(yticklabel2):
            yticklabel2 = ""
        # update the kwargs
        new_text_kwargs = _update_kwargs(
            update_dict=kwargs_text_dict,
            size=size_text,
            horizontalalignment=halignment_text,
            verticalalignment=valignment_text,
        )
        # plotting table text
        ax.text(
            x=xloc,
            y=yticklabel1,
            s=yticklabel2,
            transform=transform,
            **new_text_kwargs,
        )
    # ################### add header
    if annoteheader is not None:
        # update the kwargs
        new_header_kwargs = _update_kwargs(
            update_dict=kwargs_header_dict,
            size=size_header,
            horizontalalignment=halignment_header,
            verticalalignment=valignment_header,
            fontweight=FNames.fontweight,
        )
        ax.text(
            x=xloc_header,
            y=ax.get_ylim()[1] - negative_padding,
            s=annoteheader,
            transform=transform,
            **new_header_kwargs,
        )
    # ################### add optional span
    if span is not None:
        for s in span:
            plot_span(span[s][span_start],
                      span[s][span_stop],
                      ax=ax,
                      **span[s][span_kwargs],
                      )
    # ################### return
    return ax

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Supported parameter space
class EmpericalSupport(object):
    """
    A class to calculate and plot a somewhat historic empirical support plot,
    also referred to as a `compatibility` plot.
    
    This class provides methods to construct and visualise the full range of
    confidence intervals associated with a given point estimate and standard
    error, as a function of alpha.
    
    Parameters
    ----------
    estimate : `float`
        The point estimate (e.g. a mean difference or log-transformed odds ratio).
    standard_error : `float`
        The standard error of the point estimate.
    alpha : `list` [`float`]
        A list of alpha's (i.e. type 1 error rate) between 0 and 1, used
        to generate confidence interval levels. For example,
        `np.linspace(0.001, 0.999, 1000)`.
    
    Attributes
    ----------
    estimate : `float`
        The point estimate provided at instantiation.
    standard_error : `float`
        The associated standard error.
    alpha : `list` [`float`]
        The alpha values used to compute confidence intervals.
    table : `pd.DataFrame`
        The calculated support table, containing lower and upper bounds,
        p-values, and CI coverage.
    results_ : `EmpericalSupportResults`
        An EmpericalSupportResults instance.
    
    Methods
    -------
    calc_empirical_support(estimate, standard_error, alpha)
        Computes the range of confidence intervals and compatibility metrics
        over the supplied alpha values.
    
    plot_tree(...)
        Creates a 'tree plot' summarising the parameter space supported by
        the data, with options for CI and estimate annotations.
    
    _plot_empirical_support(...)
        Generates a visualisation of confidence intervals and their overlap
        across varying alpha values.
    
    Notes
    -----
    This implementation is based on the concept of compatibility (or
    confidence) curves, which visualise the range of parameter values supported
    by the data across a continuum of alpha levels [1]_, [2]_.
    
    References
    ----------
    .. [1] Amrhein, V., Greenland, S., & McShane, B. B. (2019).
       Scientists rise up against statistical significance.
       *Nature*, 567(7748), 305–307. https://doi.org/10.1038/d41586-019-00857-9
    
    .. [2] Van der Burg, S. H., & Gelman, A. (2020).
       Empirical support plots and compatibility intervals.
       *BMC Medical Research Methodology*, 20, Article 109.
       https://doi.org/10.1186/s12874-020-01105-9
    """
    
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def __init__(self,
                 estimate:float, standard_error:float, alpha:list[float],
                 ):
        '''
        Setting up kwargs for `calc_empirical_support` and
        `_plot_empirical_support`.
        '''
        # confirm input
        is_type(estimate, (int, float))
        is_type(standard_error, (int, float))
        is_type(alpha, (list, np.ndarray))
        # asign
        self.estimate=estimate
        self.standard_error=standard_error
        self.alpha=alpha
        self.table = None
        setattr(self, FNames.EmpericalSupportResults, None)
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def __str__(self) -> str:
        """
        Return a readable summary of the instance.
        """
        return (
            f"{type(self).__name__} instance\n"
            f"  Estimate        : {self.estimate:.4f}\n"
            f"  Standard Error  : {self.standard_error:.4f}\n"
            f"  Alpha Range     : [{min(self.alpha):.3f}, {max(self.alpha):.3f}] "
            f"(n={len(self.alpha)})"
        )
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def __repr__(self) -> str:
        """
        Return a formal string representation for debugging.
        """
        return (
            f"{type(self).__name__}(estimate={self.estimate!r}, "
            f"standard_error={self.standard_error!r}, "
            f"alpha=[{min(self.alpha):.3f}, ..., {max(self.alpha):.3f}] "
            f"({len(self.alpha)} values))"
        )
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    @staticmethod
    def calc_empirical_support(
        estimate:float, standard_error:float, alpha:list[float],
                          ) -> pd.DataFrame:
        """
        Compute empirical support across a sequence of alpha values.
        
        For a given point estimate and standard error, this function calculates
        a table of confidence intervals and p-values across the supplied list
        alpha levels.
        
        Parameters
        ----------
        estimate : `float`,
            The point estimate, e.g. a mean difference or log odds ratio.
        standard_error : `float`,
            The standard error of the point estimate.
        alpha : `list` [`float`]
            A list of alpha's (i.e., type 1 error rate) between 0 and 1.
            Typically should be around a 1000 values, for example generated
            using np.linspace.
        
        Returns
        -------
        pd.DataFrame
            A table with columns for the lower and upper bounds of the
            confidence interval, as well as the p-value and confidence interval
            coverage.
        
        Raises
        ------
        ValueError
            If any value in `alpha` is not in the interval (0, 1).
        
        Notes
        -----
        The confidence intervals are computed using the normal approximation:
        `estimate ± z * standard_error`, where `z` is the (1 - alpha/2)
        quantile of the standard normal distribution.
        """
        # check input
        ERROR='`{}` should not {} {}, current {}: {}.'
        is_type(estimate, (int,float))
        is_type(standard_error, (int, float))
        is_type(alpha, (list, np.ndarray))
        is_series_type(pd.Series(alpha), float)
        if max(alpha) > 1:
            raise ValueError(
                ERROR.format('alpha', 'exceed', '1', 'maximum', str(max(alpha)))
            )
        if min(alpha) < 0:
            raise ValueError(
                ERROR.format('alpha', 'be smaller than', '0', 'minimum',
                             str(min(alpha)))
            )
        # coverage
        lb, ub = ( [] for _ in range(2) )
        for a in alpha:
            lb.append(estimate - standard_error*norm.ppf(1-a/2))
            ub.append(estimate + standard_error*norm.ppf(1-a/2))
        # table
        n = len(lb)
        table = pd.DataFrame({
            FNames.ESTIMATE : [estimate] * n,
            FNames.LOWER_BOUND: lb,
            FNames.UPPER_BOUND: ub,
            FNames.PVALUE: alpha,
            FNames.CI: [1-a for a in alpha],
        })
        # return
        return table
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    @staticmethod
    def _plot_empirical_support(
        data:pd.DataFrame, lb_col:str, ub_col:str, support_col:str,
        line_c:str='black', linewidth:Real=1, linestyle:str='-',
        estimate:Real | None = None, estimate_size:Real=40,
        estimate_shape: str | mpath.Path = mpath.Path.unit_circle(),
        estimate_c:str='orangered',
        area_c:str | None = None,
        area_a:float = 0.7,
        ax:plt.Axes | None = None,
        figsize:tuple[Real, Real]=(10, 10),
        reverse_y:bool=False,
        kwargs_plot:dict[Any,Any] | None = None,
        kwargs_dot:dict[Any,Any] | None = None,
        kwargs_fill:dict[Any,Any] | None = None,
    ) -> tuple[plt.Figure, plt.Axes]:
        """
        Creates an empirical support plot.
        
        This function visualises the range of confidence intervals across a
        continuum of alpha values, forming a compatibility curve. The plot
        displays the lower and upper confidence bounds as a function of
        support (e.g. `1 - alpha`), and optionally includes shaded intervals
        and point estimate annotations.
        
        Parameters
        ----------
        data : `pd.DataFrame`
            A pandas DataFrame containing the lower and upper bounds, as well
            as indicator of support (plotted on the y-axis).
        lb_col : `str`
            The column name of the lower bound.
        ub_col : `str`
            The column name of the upper bound.
        support_col : `str`
            The column name of the support values. Typically this will
            be a column with confidence interval floats, or a column of
            p-values/alpha's.
        line_c : `str`, default `black`
            The colour of the confidence interval curves.
        linewidth : `float`, default `1.0`
            The size of the confidence interval curves.
        linestyle : `str`, default `-`
            The linestyle of the confidence interval curves.
        estimate : `float`, or `None` default `NoneType`
            If provided plots the estimate as a marker on top of the graph.
        estimate_size : `float`, default `1.0`
            The size of the estimate marker.
        estimate_shape : `str`, default `o`
            The estimate marker shape.
        estimate_c : `str`, default `orangered`
            The color of the estimate marker.
        area_c: `str` or `None`, default `NoneType`
            The colour of the area between the confidence intervals. This
            is mapped to the facecolor parameter. Set to `NoneType` to skip.
        area_a: `float`, default `0.7`
            The proportion of opacity of the area between the curves.
        ax : `plt.axes` or `None`, default `NoneType`
            An optional matplotlib axis. If supplied the function works on the
            axis, otherwise the function will create an axis object internally.
        figsize : `tuple` [`float`,`float`], default (10, 10),
            The figure size, when ax==None.
        reverse_y : `bool`, default `True`
            inverts the y-axis.
        kwargs_plot : `dict` [`str`, `any`] or `None`, default `None`
            Extra keyword arguments passed to `ax.plot()` for CI lines.
        kwargs_dot : `dict` [`str`, `any`] or `None`, default `None`
            Extra keyword arguments passed to `ax.scatter()` for the estimate.
        kwargs_fill : `dict` [`str`, `any`] or `None`, default `None`
            Extra keyword arguments passed to `ax.fill_betweenx()`.
        
        Returns
        -------
        plt.Figure
            The matplotlib Figure object.
        plt.Axes
            The matplotlib Axes object with the empirical support plot.
        """
        # ################## check input
        is_df(data)
        is_type(lb_col, str)
        is_type(ub_col, str)
        is_type(support_col, (str, type(None)))
        is_type(line_c, str)
        is_type(linewidth, (int, float))
        is_type(linestyle, str)
        is_type(estimate, (Real, type(None)))
        is_type(estimate_size, Real)
        is_type(estimate_c, str)
        is_type(area_c, (type(None),str))
        is_type(area_a, (int, float))
        is_type(ax, (type(None), plt.Axes))
        is_type(figsize, tuple)
        is_type(reverse_y, bool)
        # Mapping None to dict
        kwargs_plot = kwargs_plot or {}
        kwargs_dot = kwargs_dot or {}
        kwargs_fill = kwargs_fill or {}
        # kwargs_plot, kwargs_dot, kwargs_fill = _assign_empty_default(
        #     [kwargs_plot, kwargs_dot, kwargs_fill], dict)
        # ################## should we create a figure and axis
        if ax is None:
            f, ax = plt.subplots(figsize=figsize)
        else:
            f = ax.figure
        # ################## annotate point
        if estimate is not None:
            # find location where lb == ub
            try:
                mask = np.isclose(data[lb_col], data[ub_col], atol=1e-12)
                center = data.loc[mask, support_col].to_list()[0]
                # center=data[data[lb_col] == data[ub_col]][support_col].to_list()[0]
            except IndexError:
                raise IndexError('Could not find the row where the lower and '
                                 'upper confidence intervals are equal. Please '
                                 'inspect the data table.')
            new_dot_kwargs = _update_kwargs(update_dict=kwargs_dot,
                                            c=estimate_c,
                                            s=estimate_size,
                                            marker=estimate_shape,
                                            zorder=2,
                                            )
            ax.scatter(y=center, x=estimate,
                       **new_dot_kwargs)
        # ################## plots lines
        new_plot_kwargs = _update_kwargs(update_dict=kwargs_plot,
                                         c=line_c,
                                         linewidth=linewidth,
                                         linestyle=linestyle,
                                         zorder=1,
                                         )
        yval=data[support_col].to_numpy()
        for xval in [lb_col, ub_col]:
            x = data[xval].to_numpy()
            ax.plot(x, yval,
                    **new_plot_kwargs)
        # ################### colour the area
        if area_c is not None:
            new_fill_kwargs = _update_kwargs(update_dict=kwargs_fill,
                                             facecolor=area_c,
                                             alpha=area_a,
                                             zorder=0,
                                             )
            ylimits=np.linspace(1,0, data.shape[0])
            # create the xaxis limits
            xleft=data[lb_col].to_numpy(); xright=data[ub_col].to_numpy()
            ax.fill_betweenx(ylimits, xleft, xright,
                             **new_fill_kwargs)
        # ################### invert y-axis
        if reverse_y == True:
            ax.invert_yaxis()
        # ################### return the figure, and axis
        return f, ax
    # /////////////////////////////////////////////////////////////////////////
    # main function
    def plot_tree(self,
                  support:Literal['coverage','compatibility']='coverage',
                  annotate_estimate:bool=False,
                  annotate_ci:list[Real] | None = None,
                  line_c:str='black', linewidth:float=0.5, linestyle:str='-',
                  estimate_size:Real=20, estimate_c:str='orangered',
                  estimate_shape:str | mpath.Path = mpath.Path.unit_circle(),
                  area_c:str | None = None,
                  area_a:float=1.0,
                  reverse_y:bool | None = None,
                  ax:plt.Axes | None = None,
                  figsize:tuple[Real,Real]=(10,10),
                  kwargs_plot:dict[Any,Any] | None = None,
                  kwargs_dot:dict[Any,Any] | None = None,
                  kwargs_fill:dict[Any,Any] | None = None,
                  kwargs_xlabel:dict[Any,Any] | None = None,
                  kwargs_ylabel:dict[Any,Any] | None = None,
                  kwargs_segment:dict[Any,Any] | None = None,
                  kwargs_text:dict[Any,Any] | None = None,
                  )-> tuple[plt.Figure, plt.Axes]:
        """
        Plots an Emperical Support graph based on either `coverage` (iterating
        the confidence interval coverage percentage), or `compatibility`
        (iterating the p-value). Due to its Christmas tree like shape this
        type of illustration is refered to as a `tree plot`.
        
        Parameters
        ----------
        support : `str`, default `coverage`
            Determines what is plotted on the y-axis. If 'coverage', plots
            confidence level from 0 to 1. If 'compatibility', plots p-values
            from 1 to 0.
        annotate_estimate: `bool`, default `False`
            Whether to include the estimate as a dot at the point where lower
            and upper bounds converge.
        annotate_ci : `list` [`float`] or `None`, default `NoneType`
            A list of confidence levels for which to annotate labelled
            horizontal segments, using `segment_labelled`.
        line_c : `str`, default `black`
            The colour of the confidence interval curves.
        linewidth : `float`, default `1.0`
            The size of the confidence interval curves.
        linestyle : `str`, default `-`
            The linestyle of the confidence interval curves.
        estimate_size : `float`, default `20`
            The size of the estimate marker.
        estimate_shape : `str`, default `o`
            The estimate marker.
        estimate_c : `str`, default `orangered`
            The color of the estimate marker.
        area_c : `str` or `None`, default `NoneType`
            The colour of the area between the confidence intervals. This
            is mapped to the facecolor parameter.
        area_a : `float`, default `1.0`
            The proportion of opacity of the area between the curves.
        ax : `plt.axes` or `None`, default `NoneType`
            An optional matplotlib axis. If supplied the function works on the
            axis, otherwise the function will create an axis object internally.
        reverse_y : `bool`, default `NoneType`
            Inverts the y-axis.  Set to `False` or `True` to overwrite internal
            behaviour.
        kwargs_plot : `dict` [`str`,`any`] or `None`, default `None`
            Keyword arguments passed to `ax.plot()` for CI lines.
        kwargs_dot : `dict` [`str`,`any`] or `None`, default `None`
            Keyword arguments passed to `ax.scatter()` for the estimate marker.
        kwargs_fill : `dict` [`str`,`any`] or `None`, default `None`
            Keyword arguments passed to `ax.fill_betweenx()` for shaded area.
        kwargs_xlabel : `dict` [`str`,`any`] or `None`, default `None`
            Keyword arguments passed to `ax.set_xlabel()`.
        kwargs_ylabel : `dict` [`str`,`any`] or `None`, default `None`
            Keyword arguments passed to `ax.set_ylabel()`.
        kwargs_segment : `dict` [`str`,`any`] or `None`, default `None`
            Keyword arguments passed to `ax.plot()` for annotation segments.
        kwargs_text : `dict` [`str`,`any`] or `None`, default `None`
            Keyword arguments passed to `ax.text()` for annotation labels.
        
        Returns
        -------
        matplotlib.figure.Figure
            The matplotlib Figure object.
        matplotlib.axes.Axes
            The Axes object containing the tree plot.
        
        Notes
        -----
        This method modifies the object in-place by setting the following attributes:
        
        - `self.table` : a DataFrame of estimated intervals across alpha values
        - `self.support_col` : name of the y-axis support column
        - `self.ylabel` : label for the y-axis
        - `self.EmpericalSupportPlotResults` : a container with estimate and results
        
        These attributes may be accessed after the plot call if a reference to the
        object is retained.
        """
        # ################### input
        is_type(support, str)
        is_type(annotate_estimate, bool)
        is_type(annotate_ci, (type(None), list))
        if (support != FNames.EmpericalSupport_Coverage) &\
                (support != FNames.EmpericalSupport_Compatability):
            raise InputValidationError(
                Error_MSG.INVALID_STRING.format(
                    'support', FNames.EmpericalSupport_Coverage + ' or ' +
                    FNames.EmpericalSupport_Compatability
                )
            )
        # set None to dict
        kwargs_plot = kwargs_plot or {}
        kwargs_dot = kwargs_dot or {}
        kwargs_fill = kwargs_fill or {}
        kwargs_xlabel = kwargs_xlabel or {}
        kwargs_ylabel = kwargs_ylabel or {}
        kwargs_segment = kwargs_segment or {}
        kwargs_text = kwargs_text or {}
        # ################### calculate support
        self.table = self.calc_empirical_support(
            estimate=self.estimate, standard_error=self.standard_error,
            alpha=self.alpha,
        )
        # ################### plot support
        # do we need a figure and axis
        if ax is None:
            f, ax = plt.subplots(figsize=figsize)
        else:
            f = ax.figure
        if support == FNames.EmpericalSupport_Coverage:
            self.support_col = FNames.CI
            self.ylabel = 'Coverage'
            self.table =self.table.sort_values(
                by=[self.support_col], ascending=False)
            self.reverse_y=True
        else:
            self.support_col = FNames.PVALUE
            self.ylabel = 'Compatibility\n(p-value)'
            self.reverse_y=False
        if reverse_y is not None:
            self.reverse_y=reverse_y
        # do we annotate the point
        if annotate_estimate == True:
            plot_estimate=self.estimate
        else:
            plot_estimate=None
        # ################### plot
        f, ax = self._plot_empirical_support(
            data=self.table, support_col=self.support_col,
            lb_col=FNames.LOWER_BOUND, ub_col=FNames.UPPER_BOUND,
            estimate=plot_estimate, estimate_size=estimate_size,
            estimate_shape=estimate_shape, estimate_c=estimate_c,
            line_c=line_c, linewidth=linewidth, linestyle=linestyle,
            area_c=area_c, area_a=area_a,
            ax=ax, figsize=figsize,
            reverse_y=self.reverse_y,
            kwargs_plot=kwargs_plot,
            kwargs_dot=kwargs_dot,
            kwargs_fill=kwargs_fill,
        )
        # ################### add ci annotations
        if annotate_ci is not None:
            for val in annotate_ci:
                # finding the CI with the smallest difference compared to val
                idx = (self.table[FNames.CI]-val).abs().argsort().iloc[1]
                # getting the x and y values
                x_seg = self.table.iloc[idx][[FNames.LOWER_BOUND,
                                         FNames.UPPER_BOUND]].to_list()
                # which y_value to use
                if support == FNames.EmpericalSupport_Coverage:
                    Y_COL = FNames.CI
                else:
                    Y_COL = FNames.PVALUE
                y_seg = self.table.iloc[idx][[Y_COL]].to_list()*2
                # getting the string
                val_str="{:.2f}".format(np.round(val, 2))
                segment_labelled(x=x_seg, y=y_seg, label=val_str,
                                 ax=ax,
                                 # will be a line
                                 overrule_angle=0,
                                 kwargs_segment=kwargs_segment,
                                 kwargs_text=kwargs_text,
                                 )
        # set label
        ax.set_xlabel('Point estimate', **kwargs_xlabel)
        ax.set_ylabel(self.ylabel, **kwargs_ylabel)
        # ################### return
        results_dict={FNames.ESTIMATE   : self.estimate,
                      FNames.data_table : self.table,
                      }
        setattr(self,
                FNames.EmpericalSupportResults,
                EmpericalSupportPlotResults(**results_dict),
                )
        return f, ax

