"""
Figure templates for visualising performance and interpretability of
machine learning models.

This module provides reusable plotting utilities for common visualisations in
machine learning workflows, including lollipop charts for feature importance,
calibration plots for model reliability assessment, and decision curve
analysis (DCA) plots for evaluating clinical utility.

Functions
---------
lollipop(values, labels, ...)
    Draws a lollipop chart (dot-and-line plot) for visualising feature
    importance or effect sizes.

Classes
-------
Calibration
    A plotting template for comparing observed and predicted risk, with
    optional confidence intervals and calibration curves.

DecisionCurve
    A class to compute and plot DCA, evaluating net benefit of prediction
    models across varying risk thresholds.

"""

# imports
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# import matplotlib as mpl
from plot_misc.constants import (
    NamesDecisionCurves as NamesDC,
    NamesMachineLearnig as NamesML,
    Real,
)
from plot_misc.errors import (
    is_type,
    is_df,
    are_columns_in_df,
    same_len,
    InputValidationError,
    string_to_list,
    number_to_list,
)
from plot_misc.utils.utils import (
    change_ticks,
    _update_kwargs,
    
)
from typing import (
    Any,
    Callable,
    Union,
    Self,
)
from statsmodels.nonparametric.smoothers_lowess import lowess
# from packaging import version
# if version.parse('3.4.0') < version.parse(mpl._version.version):
#     from matplotlib.colorbar import Colorbar as colorbar_factory
# else:
#     from matplotlib.colorbar import colorbar_factory

# #############################################################################

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def lollipop(values:np.ndarray, labels:np.ndarray,
             line_colour:str='tab:orange', dot_color:str='deeppink',
             linewidth:float=1, dot_edge_color:str='black', dot_size:float=4,
             dot_edge_size:float=0.5,
             importance_margin:float | None =0,
             importance_limit:tuple[float,float] | None=None,
             reverse_feature_order:bool=False,
             vertical:bool=False,
             figsize:tuple=(6, 6),
             ax:plt.Axes | None=None,
             kwargs_lines_dict:dict[Any,Any] | None=None,
             kwargs_plot_dict:dict[Any,Any] | None=None,
             ) -> tuple[plt.Axes, plt.Figure]:
    """
    Plots a lollipop chart.
    
    A visual alternative to a bar chart, drawing a horizontal line for each
    observation and ending in a dot. Primarily used for ranked feature
    importance, effect sizes, or similar vector-valued summaries.
    
    Parameters
    ----------
    values : `np.ndarray`
        Values determining the length of each line.
    labels : `np.ndarray`
        Labels for each feature.
    line_colour: `str`, default `tab:orange`
        The line colour.
    linewidth : `float`, default 1
        The linewidth.
    dot_color : `str`, default `deeppink`
        The dot colour.
    dot_edge_color : `str`, default `black`
        Colour of the dot edges.
    dot_size : `float`, default 4
        The size of the dot.
    dot_edge_size : `float`, default 0.5
        Width of the dot edge outline.
    reverse_feature_order : `bool`, default `False`
        Plots the features in opposite order.
    importance_margin : `float`, default 0
        Padding on the axis representing the feature importance value.
        Set to `None` to use matplotlib defaults.
    importance_limit : `tuple` [`float`,`float`], default `NoneType`
        Explicit x-axis limits. If None, inferred automatically.
    vertical : `bool`, default `True`
        If True, draws vertical lines with feature labels on the y-axis.
        If False, draws horizontal lines with feature labels on the x-axis.
        This effectively transposes the chart orientation and can be used
        to better accommodate long labels or large feature sets.
    ax : `plt.Axes`, default `NoneType`
        Matplotlib Axes to plot on. If None, a new figure and axes are created.
    figsize : `tuple` [`float`,`float`], default `(10, 10)`
        The figure size in inches when ax is `NoneType`.
    kwargs_lines_dict : `dict` [`str`, `any`] or `None`, default `None`
        Additional keyword arguments passed to `ax.hlines`.
    kwargs_plot_dict : `dict` [`str`, `any`] or `None`, default `None`
        Additional keyword arguments passed to `ax.plot` for dot rendering.
    
    Returns
    -------
    figure : `matplotlib.figure.Figure`
        The matplotlib Figure object.
    ax : `matplotlib.axes.Axes`
        The matplotlib Axes object with the plot drawn on.
    
    Notes
    -----
    When `vertical=True`, values are shown on the y-axis, and labels appear
    along the x-axis. This is suitable for ranking large numbers of features.
    For long text labels, set `vertical=False` to flip the axes.
    """
    
    # ################### Check input
    is_type(ax, (type(None), plt.Axes))
    is_type(line_colour, str)
    is_type(linewidth, (int, float))
    is_type(dot_color, str)
    is_type(dot_edge_color, str)
    is_type(dot_size, (int, float))
    is_type(dot_edge_size, (int, float))
    is_type(vertical, bool)
    same_len(values, labels)
    # map None to empty dict
    kwargs_lines_dict = kwargs_lines_dict or {}
    kwargs_plot_dict = kwargs_plot_dict or {}
    # ################### process input
    # create a axes if needed
    if ax is None:
        f, ax = plt.subplots(figsize=figsize)
    else:
        f = ax.figure
    # get index index to numeric
    index = range(values.shape[0])
    # ################### plot lines and dots, first updating the kwargs
    new_lines_dict = _update_kwargs(kwargs_lines_dict, color=line_colour,
                                    linewidth=linewidth)
    new_plot_dict = _update_kwargs(kwargs_plot_dict,
                                   marker='o',
                                   linestyle='None',
                                   c=dot_color,
                                   markeredgecolor=dot_edge_color,
                                   markersize=dot_size,
                                   markeredgewidth=dot_edge_size,
                                   )
    if vertical == True:
        # #### vertical lines
        ax.vlines(x=index, ymin=0, ymax=values, **new_lines_dict,
                  )
        ax.plot(index, values,  **new_plot_dict,
                )
        change_ticks(ax=ax, ticks=list(index), labels=list(labels), axis='x')
        #  margins
        value_lim = ax.get_ylim()
        if not importance_margin is None:
            ax.margins(y=importance_margin)
        if importance_limit is None:
            ax.set_ylim(0, value_lim[1]*1.05)
        else:
            ax.set_ylim(importance_limit)
        #  invert feature axis
        if reverse_feature_order == True:
            ax.invert_xaxis()
    else:
        # #### horizontal lines
        ax.hlines(y=index, xmin=0, xmax=values, **new_lines_dict,
                  )
        ax.plot(values, index, **new_plot_dict,
                )
        change_ticks(ax=ax, ticks=list(index), labels=list(labels), axis='y')
        #  margins
        value_lim = ax.get_xlim()
        if not importance_margin is None:
            ax.margins(x=importance_margin)
        if importance_limit is None:
            ax.set_xlim(0, value_lim[1]*1.05)
        else:
            ax.set_xlim(importance_limit)
        #  invert feature axis
        if reverse_feature_order == True:
            ax.invert_yaxis()
    # hide spines
    try:
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
    except AttributeError:
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)
    # return the figure and axis
    return f, ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Calibration(object):
    """
    Calibration plot for evaluating the agreement between predicted and
    observed risks.
    
    This class provides a plotting interface to assess model calibration by
    comparing predicted risks (typically from a statistical or machine learning
    model) with observed event rates, optionally including confidence intervals
    and smooth calibration curves.
    
    Attributes
    ----------
    data : `dict` [`pd.DataFrame`]
        A dictionary or single DataFrame containing binned calibration data,
        with at least columns for predicted and observed risks.
    ax : `plt.Axes`
        The axes object.
    figure : `plt.Figure`
        The top level figure container.
    curves_data_ : `dict` [`str`, `np.ndarry'] or `None`
        The smoothed calibration curve data added via `add_curves`.
    
    Parameters
    ----------
    data : `pd.DataFrame` or `dict` [`pd.DataFrame`]
        Binned data containing predicted risks and observed outcomes per bin.
        If multiple models are provided, use a dictionary of DataFrames.
    ax : `plt.Axes`, default `NoneType`
        Optional matplotlib axis to draw on. If None, a new figure and axis are
        created.
    figsize : `tuple` [`float`, `float`], default (6.0, 6.0),
        Figure size in inches if `ax` is not supplied.
    
    Notes
    -----
    This class expects that the input data consists of the pre-computed
    x- and y-coordinates. Typically these reflect observed risk per bin and the
    mean predicted risk per bin, but no default choice in enforced. Smoothed
    curves can be drawn based on individual participant level data.
    """
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def __init__(self, data:pd.DataFrame, ax:plt.Axes | None = None,
                 figsize:tuple[float,float]=(6.0, 6.0),
                 ):
        """
        Copies the data internally.
        """
        is_type(data, (dict, pd.DataFrame))
        is_type(ax, (type(None), plt.Axes))
        # create a axes if needed
        if ax is None:
            f, ax = plt.subplots(figsize=figsize)
        else:
            f = ax.figure
        # creating a dictionary if needed
        if not isinstance(data, dict):
            data = {'dataset1': data}
        # assign to self
        self.figure = f
        self.ax = ax
        self._plot = False
        self.curves_data_ = None
        self.data = data.copy()
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def __str__(self) -> str:
        NAME = type(self).__name__
        if isinstance(self.data, dict):
            keys = ', '.join(map(str, self.data.keys()))
            return f"{NAME} for {len(self.data)} models: {keys}"
        else:
            return f"{NAME} for a single model: {self.data.shape[0]} rows"
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def __repr__(self) -> str:
        NAME = type(self).__name__
        data_type = (
            f"dict[{len(self.data)}]" if isinstance(self.data, dict)
            else f"DataFrame[{self.data.shape[0]}x{self.data.shape[1]}]"
        )
        ax_type = type(self.ax).__name__
        fig_size = tuple(round(x, 1) for x in self.figure.get_size_inches())
        return (
            f"{NAME}("
            f"data={data_type}, "
            f"ax={ax_type}, "
            f"figure=Figure(size={fig_size}))"
        )
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def plot(self,
        observed:str, predicted:str,
        lower_observed:str | None = None,
        upper_observed:str | None = None,
        ci_colour:str | list[str] | None = ['lightcoral'],
        ci_linewidth:float | list[float] | None = [0.5],
        dot_marker:str | list[str] = ['o'],
        dot_colour:str | list[str] = ['lightcoral'],
        line_colour:str | list[str] = ['lightcoral'],
        line_linewidth:float | list[float] = [0.7],
        line_linestyle:str | list[str] =['--'],
        figsize:tuple[float,float]=(6, 6),
        diagonal_colour:str='black',
        diagonal_linewidth:float=0.5,
        diagonal_linestyle:str='-',
        margins:tuple[float, float]=(0.01, 0.01),
        kwargs_ci_dict:dict[Any,Any] | None = None,
        kwargs_dot_dict:dict[Any,Any] | None = None,
        kwargs_line_dict:dict[Any,Any] | None = None,
        kwargs_diagonal_dict:dict[Any,Any] | None = None,
             ) -> Self:
        """
        Plots the actual calibration plot.
        
        Parameters
        ----------
        observed : `str`
            A column name in `data` representing the observed risk
            (between 0 and 1).
        predicted : `str`
            A column name in `data` representing the predicted risk
            (between 0 and 1).
        lower_observed : `str` or `None`, default `NoneType`
            An optional column name in `data` representing the lower bound of
            the observed risk. For example this can be a confidence interval
            limit.
        upper_observed : `str` or `None`, default `NoneType`
            An optional column name in `data` representing the upper bound of
            the observed risk. For example this can be a confidence interval
            limit.
        ci_colour : `str` or `list` [`str`]
            The colours the interval limits.
        ci_linewidth : `float` or `list` [`float`]
            The linewidth the the interval limits.
        dot_marker : `str` or `list` [`str`]
            The marker for the average agreement between observed and predicted
            risk.
        dot_colour : `str` or `list` [`str`]
            The marker colour.
        line_colour : `str` or `list` [`str`]
            The colour of the line connecting the dots.
        line_linestyle : `str` or `list` [`str`]
            The linestyle of the line connecting the dots.
        line_linewidth : `float` or `list` [`float`]
            The linewidth of the line connecting the dots.
        diagonal_colour : `str`
            The colour of the diagonal line.
        diagonal_linestyle : `str`
            The linestyle of the diagonal line.
        diagonal_linewidth : `float`
            The width of the diagonal line.
        margins : `tuple` [`float`,`float`], default (0.01, 0.01)
            Additional space around the plot boundaries (x and y).
        kwargs_ci_dict : `dict` [`str`, `any`] or `None`, default None
            Additional keyword arguments for `ax.plot` used for the interval
            lines.
        kwargs_dot_dict : `dict` [`str`, `any`] or `None`, default None
            Additional keyword arguments for `ax.scatter` used for the markers.
        kwargs_line_dict : `dict` [`str`, `any`] or `None`, default None
            Additional keyword arguments for `ax.plot` used for the connecting
            lines.
        kwargs_diagonal_dict : `dict` [`str`, `any`] or `None`, default None
            Additional keyword arguments for the reference line (`ax.axline`).
        
        Returns
        -------
        self : Calibration
            The same instance with the plot rendered.
        """
        # ################### check input
        is_type(observed, str)
        is_type(predicted, str)
        is_type(lower_observed, (str, type(None)))
        is_type(upper_observed, (str, type(None)))
        is_type(ci_colour, (str,list, type(None)))
        is_type(ci_linewidth, (str, list, type(None)))
        is_type(dot_marker,(str, list))
        is_type(dot_colour, (str, list))
        is_type(line_colour, (str, list))
        is_type(line_linewidth, (float, list))
        is_type(line_linestyle, (str, list))
        is_type(figsize, tuple)
        is_type(diagonal_linewidth, float)
        is_type(diagonal_colour, str)
        is_type(diagonal_linestyle, str)
        is_type(margins, tuple)
        # #### map None to empty dict
        kwargs_ci_dict = kwargs_ci_dict or {}
        kwargs_dot_dict = kwargs_dot_dict or {}
        kwargs_line_dict = kwargs_line_dict or {}
        kwargs_diagonal_dict = kwargs_diagonal_dict or {}
        # #### testing column content
        # combined the columns
        columns = [predicted, observed]
        if not lower_observed is None:
            columns = columns + [lower_observed]
        if not upper_observed is None:
            columns = columns + [upper_observed]
        [are_columns_in_df(d, columns) for d in self.data.values()]
        # #### compare plt params to dict len
        # NOTE if None simply repeat for the number of datasets
        if not ci_colour is None:
            same_len(self.data, ci_colour, [NamesML.DATA, NamesML.CI_COLOUR])
        else:
            ci_colour = [None] * len(self.data)
        # NOTE if None simply repeat for the number of datasets
        if not ci_linewidth is None:
            same_len(self.data, ci_linewidth, [NamesML.DATA,NamesML.CI_LINEWIDTH])
        else:
            ci_linewidth = [None] * len(self.data)
        # ################### making lists
        ci_linewidth = number_to_list(ci_linewidth)
        ci_colour = string_to_list(ci_colour)
        dot_marker = string_to_list(dot_marker)
        dot_colour = string_to_list(dot_colour)
        self.line_colour = string_to_list(line_colour)
        self.line_linewidth = number_to_list(line_linewidth)
        self.line_linestyle = string_to_list(line_linestyle)
        # further test
        same_len(self.data, dot_colour, [NamesML.DATA,NamesML.DOT_COLOUR])
        same_len(self.data, dot_marker, [NamesML.DATA,NamesML.DOT_MARKER])
        same_len(self.data, line_colour, [NamesML.DATA,NamesML.LINE_LINESTYLE])
        same_len(self.data, line_linewidth, [NamesML.DATA,NamesML.LINE_LINEWIDTH])
        same_len(self.data, line_linestyle, [NamesML.DATA,NamesML.LINE_LINESTYLE])
        # ################### Plotting
        # Add the diagonal line, first updating the kwargs
        new_diagonal_dict =\
            _update_kwargs(kwargs_diagonal_dict, lw=diagonal_linewidth,
                           ls=diagonal_linestyle, c=diagonal_colour)
        self.ax.axline(xy1=(0, 0), slope=1, **new_diagonal_dict,
                  )
        # ################### loop over dict
        for idx, (key, val) in enumerate(self.data.items()):
            # unpack data
            x_bin = val[predicted]
            y_bin = val[observed]
            # set lb and ub to the same y-values, and update based on avail data
            y_bin_lb = val[observed]
            y_bin_ub = val[observed]
            if not lower_observed is None:
                y_bin_lb = val[lower_observed]
            if not upper_observed is None:
                y_bin_ub = val[upper_observed]
            # set confidence intervals
            y_ci = [y_bin_lb, y_bin_ub]
            x_ci = [x_bin, x_bin]
            # add line connecting the dots, first updating the kwargs
            new_line_dict =\
                _update_kwargs(kwargs_line_dict, c=self.line_colour[idx],
                               linewidth=self.line_linewidth[idx],
                               linestyle=self.line_linestyle[idx],
                               )
            self.ax.plot(x_bin, y_bin, **new_line_dict,
                    )
            # plot confidence interval, first updating the kwargs
            new_ci_dict =\
                _update_kwargs(kwargs_ci_dict, c=ci_colour[idx],
                               linewidth=ci_linewidth[idx],
                               )
            self.ax.plot(x_ci, y_ci, **new_ci_dict,
                    )
            # plot dots, first updating the kwargs
            new_dot_dict =\
                _update_kwargs(kwargs_dot_dict, c=dot_colour[idx],
                               marker=dot_marker[idx],
                               )
            self.ax.scatter(x_bin, y_bin, **new_dot_dict,
                       )
        # ################### set the plot params
        # making sure the axis is square
        # axes_min = min(ax.get_xlim()[0], ax.get_ylim()[0])
        # NOTE this is slightly opinionated thinking that the lower limit should
        # always start at zero.
        axes_max = max(self.ax.get_xlim()[1], self.ax.get_ylim()[1])
        self.ax.set_xlim(0, axes_max)
        self.ax.set_ylim(0, axes_max)
        # hide the right and top spines
        self.ax.spines.right.set_visible(False)
        self.ax.spines.top.set_visible(False)
        # margins around the both x and y
        self.ax.margins(margins[0], margins[1])
        # ################### return the figure and axis
        self._plot = True
        return self
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def add_curves(self, data: pd.DataFrame | dict[str, pd.DataFrame],
                   smoother: Callable | None = None,
                   line_colour:str | list[str] | None = None,
                   line_linewidth:float | list[float] | None = None,
                   line_linestyle:str | list[str]  | None = None,
                   kwargs_smoother: dict[str, Any] | None = None,
                   kwargs_curve: dict[str, Any] | None = None,
                   ) -> Self:
        """
        Adds smoothed or empirical calibration curves to the existing plot.
        
        This method supplements the primary calibration plot with one or more
        continuous calibration curves, typically generated using
        individual-level data and a smoothing function such as LOWESS. It
        supports overlaying model-specific calibration trends using consistent
        or custom aesthetics.
        
        Parameters
        ----------
        data : `pd.DataFrame` or `dict` [`pd.DataFrame`]
            A DataFrame or dictionary of DataFrames, where each table includes two
            columns: the first with binary outcomes (0 or 1) and the second with
            predicted probabilities (ranging from 0 to 1). Each table will
            internally be mapped to a numpy array and sorted by the second
            column.
        smoother : `callable` or `None`, default `None`
            A smoothing function such as `lowess` from `statsmodels`, or any
            user-defined callable accepting `y`, `x`, and keyword arguments.
            The function should return the predicted y on the risk scale. If
            `None`, the raw y-values will be plotted against the predicted
            scores. This can be used to plot pre-computed data.
        line_colour : `str`, `list` [`str`], or `None`, default `None`
            The colour of the curve(s), set to None to re-use this parameter.
        line_linestyle : `str`, `list` [`str`], or `None`, default `None`
            The linestyle of the curve(s), set to None to re-use this
            parameter.
        line_linewidth : `float`, `list` [`float`], or `None`, default `None`
            The linewidth of the curve(s), set to None to re-use this parameter.
        kwargs_smoother: `dict` [`str`, `any`] or `None`, default `None`
            keyword arguments passed to the `smoother`.
        kwargs_curve: `dict` [`str`, `any`] or `None`, default `None`
            keyword arguments passed to the plot function (i.e. ax.plot).
        
        Returns
        -------
        self : Calibration
            The modified instance with curves added to the existing axes.
        
        Notes
        -----
        The data should be individual-level (not binned). The first column is
        assumed to contain the observed binary outcomes (0 or 1), and the second
        column the predicted probabilities. Each dataset will be sorted by
        predicted risk prior to plotting.
        
        Raises
        ------
        RuntimeError
            If `plot()` has not been called prior to adding curves.
        """
        if self._plot == False:
            raise RuntimeError('Please run the `plot` method prior to adding '
                               'curves.')
        # check input
        is_type(data, (dict, pd.DataFrame))
        is_type(smoother, (type(None), Callable))
        is_type(line_linestyle, (str, list, type(None)))
        is_type(line_colour, (str, list, type(None)))
        is_type(line_linewidth, (str, list, type(None)))
        # map to dict
        kwargs_smoother = kwargs_smoother or {}
        kwargs_curve = kwargs_curve or {}
        # creating a dictionary if needed
        if not isinstance(data, dict):
            data_c = {'dataset1': data}
        else:
            data_c = data
        # check if line is None or not
        if line_colour is None:
            line_colour = self.line_colour
        if line_linestyle is None:
            line_linestyle = self.line_linestyle
        if line_linewidth is None:
            line_linewidth = self.line_linewidth
        # making lists
        line_colour = string_to_list(line_colour)
        line_linestyle = string_to_list(line_linestyle)
        line_linewidth = number_to_list(line_linewidth)
        same_len(data_c, line_colour, [NamesML.DATA,NamesML.LINE_LINESTYLE])
        same_len(data_c, line_linewidth, [NamesML.DATA,NamesML.LINE_LINEWIDTH])
        same_len(data_c, line_linestyle, [NamesML.DATA,NamesML.LINE_LINESTYLE])
        # ################### add a curve
        curves_res = {}
        for idx, (nam, data_cu) in enumerate(data_c.items()):
            # sort by x-axis value - the second column
            curves_data = data_cu.to_numpy()
            curves_data = curves_data[curves_data[:, 1].argsort()]
            c_x = curves_data[:,1]
            c_y = curves_data[:,0]
            # do we need to fit a model
            if smoother is not None:
                y_pred=smoother(c_y, c_x, **kwargs_smoother)
            else:
                y_pred = c_y
            # plot the cruves
            kwargs_curve = _update_kwargs(
                update_dict=kwargs_curve,
                c=line_colour[idx],
                linewidth=line_linewidth[idx],
                linestyle=line_linestyle[idx],
            )
            self.ax.plot(c_x, y_pred, **kwargs_curve
                    )
            # save predictions
            curves_res[nam] = np.column_stack((y_pred, c_x))
        # add curves_res to self
        self.curves_data_ = curves_res
        # return
        return self

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Decision Curves
class DecisionCurve(object):
    """
    Implements decision curve analysis (DCA) to evaluate the clinical utility
    of predictive models.
    
    Decision curve analysis quantifies the net benefit of a model across a
    range of risk thresholds, helping assess its usefulness in a clinical
    context. The method compares model-based decision strategies against
    interventions on all or none, accounting for false positives, true
    positives, and optional model-associated harm.
    
    Attributes
    ----------
    data : `pd.DataFrame`
        The original dataset containing predicted risks and binary outcomes.
    TICK_WIDTH : `float`
        The width ticks.
    TICK_LAB_SIZE : `float`
        The fontsize of the tick labels.
    TICK_LEN : `float`
        The tick length.
    LABEL_FONT_SIZE : `float`
        The fontsize of the axes labels.
    LABEL_PAD : `float`
        The padding of the axes labels.
    MODEL_NAMES : `list` [`str`]
        The names of the available models, including the internally
        generated: `None model` and `All model`.
    NUMBER_OF_MODELS : `int`
        The number of available models.
    NET_BENEFIT : `pd.DataFrame`
        The net benefit table.
    CALCULATED : `bool`
        Whether the net benefit table has been calculated.
    
    Parameters
    ----------
    data: `pd.DataFrame`
        Data containing model predictions and binary outcomes. Columns must
        include at least one predicted risk score (between 0 and 1) and a
        binary outcome variable.
    
    Methods
    -------
    calc_net_benefit(...)
        Computes the net benefit across a range of thresholds for one or more
        models.
    plot(...)
        Visualises the decision curves, with optional smoothing and style
        customisation.
    
    Notes
    -----
    This implementation is adapted from the `dcurves` Python package
    [https://github.com/MSKCC-Epi-Bio/dcurves], but has been refactored for
    improved readability, style consistency, and integration with custom plotting.
    Currently supports binary outcomes only. Survival-based extensions are
    not (yet) included.
    
    References
    ----------
    Vickers, A. J., & Elkin, E. B. (2006). Decision curve analysis: a novel
    method for evaluating prediction models. *Medical Decision Making*,
    26(6), 565–574.
    """
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def __init__(self,
                 data:pd.DataFrame,
                 ):
        """
        Copies the data internally.
        """
        is_df(data)
        self.data = data.copy()
        # adding plotting params
        self.TICK_WIDTH = 0.6
        self.TICK_LAB_SIZE = 4.5
        self.TICK_LEN = 3
        self.LABEL_FONT_SIZE=6
        self.LABEL_PAD=1.2
        self.CALCULATED = False
        self.MODEL_NAMES = None
        self.NUMBER_OF_MODELS = None
        self.NET_BENEFIT = None
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def __str__(self):
        return f"DecisionCurve instance with data=\n{self.data.__str__()}"
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def __repr__(self):
        return f"DecisionCurve(data=\n{self.data.__repr__()})"
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    @staticmethod
    def calc_rates(data: pd.DataFrame, outcome:str, model:str,
                    thresholds: list[Real], prevalence: Real,
    ) -> pd.DataFrame:
        """
        Computes true positive and false positive rates for a given model across
        a range of threshold probabilities.
        
        This method calculates, for each threshold, the proportion of true and
        false positives among those classified as high risk by the model.
        
        Parameters
        ----------
        data: `pd.DataFrame`
            A dataframe including `outcome` and `model` as a column.
        outcome: `str`
            Column name in `data` of outcome/target of interest.
        model : `str`
            Column name from `data` that contain model risk score. Note the
            risk score should contain values between 0 and 1.
        thresholds : `list` [`int` | `float`]
            The probability values the net benefit will be calculated for.
        prevalence : `int` or `float`
            Value that indicates the prevalence among the population. Can
            either be estimated from the data or for external sources (e.g.
            based on the case-control sampling scheme).
        
        Returns
        -------
        pd.DataFrame
            A DataFrame indexed by `threshold` with the following columns:
            - 'true_positive_rate' : Prevalence-adjusted true positive rate
            - 'false_positive_rate' : Prevalence-adjusted false positive rate
        Raises
        ------
        ValueError
            If required columns are missing from the input DataFrame.
        
        Notes
        -----
        True positives are defined as individuals with outcome = 1 and model
        prediction ≥ threshold.
        
        False positives are defined as individuals with outcome = 0 and model
        prediction ≥ threshold.
        
        These rates are scaled by the assumed prevalence to allow valid
        comparisons across populations with different case/control ratios.
        
        Code addapted from
        `here <https://github.com/MSKCC-Epi-Bio/dcurves/blob/main/dcurves/dca.py>`_.
        
        Hash: 007c64b
        """
        
        is_type(outcome, str)
        is_type(model, str)
        is_type(thresholds, list)
        is_type(prevalence, (float, int))
        is_df(data)
        # check if the necessary columns are there
        are_columns_in_df(data, expected_columns=[model, outcome])
        # #### True positives
        selected_rows = data[data[outcome].isin([True])].copy()
        true_outcome = selected_rows[[model]].copy()
        tp_rate = []
        for threshold in thresholds:
            true_tf_above_thresh_count = sum(true_outcome[model] >= threshold)
            tp_rate.append(
                (true_tf_above_thresh_count/len(true_outcome[model])) * prevalence
            )
            # NOTE the above is equivalent to: true_tf_above_thresh_count/n
        # #### False postives
        false_outcome = data[data[outcome].isin([False])][[model]]
        fp_rate = []
        for threshold in thresholds:
            fp_counts = sum(false_outcome[model] >= threshold)
            fp_rate.append(
                fp_counts/len(false_outcome[model]) * (1-prevalence)
            )
        # ### create pandas dataframe
        rates = pd.DataFrame({NamesDC.TP_RATE: tp_rate,
                              NamesDC.FP_RATE: fp_rate},
                             index=thresholds)
        rates.index.name = NamesDC.THRESHOLD
        return rates
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    def calc_net_benefit(self,
                         outcome: str, modelnames: str | list[str],
                         thresholds: list[float] | None = None,
                         harm: dict[str,float] | None = None,
                         prevalence:  Real | None = None,
                         ):
        """
        Calculates net benefit across a range of risk thresholds for one or
        more prediction models.
        
        Decision curve analysis estimates the clinical value of predictive
        models by computing the net benefit for each risk threshold, taking
        into account true positives, false positives, and optional
        model-associated harms.
        
        Parameters
        ----------
        outcome: `str`
            Column name in `data` of outcome/target of interest.
        modelnames : `str` or `list` [`str`]
            Column names from `data` that contain model risk scores or values.
        thresholds : `list` [`float`] or `None`, default `NoneType`
            The probability values the net benefit will be calculated for. If
            `NoneType` will default to a list between 0 and 1 with 100 equally
            spaced values.
        harm : `dict` [`str`,`float`] or `None`, default `NoneType`
            An optional dictionary, supplied with a `key` referring tot a
            `modelnames` entry and a float value between 0 and 1. Will be
            skipped if `NoneType`. Harm represents the burden of model might
            entail, and its value is subtracted from the crude net benefit.
        prevalence : `int`,`float` or `None, default `NoneType`
            Optional value indicating the outcome prevalence, primarily for
            case-control correction. If None, will be estimated from `data`.
        
        Returns
        -------
        None
            The results are stored internally in `self.NET_BENEFIT` and made
            available for plotting.
        
        Raises
        ------
        ValueError
            If model predictions are outside the [0, 1] range, or thresholds
            are not within valid bounds.
        Warning
            If predictions contain exact 0 or 1 values, which are adjusted
            internally to avoid division issues.
        
        Notes
        -----
        Net benefit is defined as:
            NB = (TP / N) - (FP / N) * (threshold / (1 - threshold)) - harm
        
        Two default strategies are always included:
            - "All": assume everyone receives an intervention.
            - "None": assume no one receives an intervention.
        
        The resulting table can be visualised using the `plot()` method.
        
        Code addapted from:
        `here <https://github.com/MSKCC-Epi-Bio/dcurves/blob/main/dcurves/dca.py>`_
        
        Hash: 007c64b
        """
        # ### check input
        is_type(outcome, str)
        is_type(modelnames, (str, list))
        is_type(thresholds, (list, type(None)))
        is_type(harm, (dict, type(None)))
        is_type(prevalence, (float, int, type(None)))
        # set modelnames to list if needed
        if isinstance(modelnames, str):
            modelnames = [modelnames]
        # check if the necessary columns are there
        are_columns_in_df(self.data, expected_columns=modelnames + [outcome])
        # set threshold if not supplied
        if thresholds is None:
            thresholds = list(np.linspace(0,1,100, endpoint=False))
        # ### check if supplied values are correct
        # thresholds are within 0 and 1
        mint = min(thresholds); maxt=max(thresholds)
        thresholds_msg=\
            '`thresholds` should be between 0 and 1, the current ' + \
            'min/max: {0}/{1}.'
        if (mint < 0) or (maxt > 1):
            raise ValueError(thresholds_msg.format(mint,maxt))
        # check if score values are within 0 and 1
        non_risk_scores = []
        score_msg=\
            'The following `models` have a value outside of the expect ' +\
            '0 and 1 range: `{0}`.'
        for m in modelnames:
            maxm = np.max(self.data[m])
            minm = np.min(self.data[m])
            # check if outside 0 or 1
            if (maxm > 1) or (minm < 0):
                non_risk_scores = non_risk_scores + [m]
            # check if exactly 0 or 1
            if (maxm == 1) or (minm == 0):
                warnings.warn(
                    '`{}` contains risk(s) of exactly 1 or 0, these will '
                    'be truncated.'.format(m))
                # self.data[m]=\
                #     [r + sys.float_info.epsilon if r == 0 else r for r in
                #      self.data[m]]
                # self.data[m]=\
                #     [r - sys.float_info.epsilon if r == 1 else r for r in
                #      self.data[m]]
                # NOTE confirm this work and then delete the above
                eps = sys.float_info.epsilon
                self.data[m] = self.data[m].apply(
                    lambda r: r + eps if r == 0 else (r - eps if r == 1 else r)
                )
        if len(non_risk_scores) > 0:
            raise ValueError(score_msg.format(', '.join(non_risk_scores)))
        # ### calculating the prevalence
        if prevalence is None:
            prevalence=np.mean(self.data[outcome])
        # ### calculate true positive rate
        # NOTE 1 loop over the various models and run the calc_rates function
        # NOTE 2 for the 'all' and 'none' models use a run with a score of 1 or 0.
        # NOTE 3 column-bind the results
        self.data[NamesDC.ALL_MODEL] = 1
        self.data[NamesDC.NONE_MODEL] = 0
        modelnames_w_standard = modelnames +\
            [NamesDC.ALL_MODEL, NamesDC.NONE_MODEL]
        rates_dict = {}
        for m in modelnames_w_standard:
            rates_dict[m] = self.calc_rates(self.data, outcome, m, thresholds,
                                            prevalence)
            rates_dict[m][NamesDC.MODEL] = m
            rates_dict[m][NamesDC.THRESHOLD] = rates_dict[m].index
            # add harm
            if harm is not None:
                if m in harm.keys():
                    rates_dict[m][NamesDC.HARM] = harm[m]
                else:
                    rates_dict[m][NamesDC.HARM] = 0
            else:
                rates_dict[m][NamesDC.HARM] = 0
        # make frame
        results = pd.concat(rates_dict, ignore_index=True)
        results.set_index(NamesDC.MODEL, inplace=True)
        # For None model set rates to zero
        # NOTE fix this in the `calc_rates` function
        results.loc[NamesDC.NONE_MODEL, [NamesDC.TP_RATE, NamesDC.FP_RATE]] = 0
        # #### calculate the net benefit
        results[NamesDC.NETBENEFIT] = (
            results[NamesDC.TP_RATE] -\
            (results[NamesDC.THRESHOLD] / (1 - results[NamesDC.THRESHOLD])) *\
            results[NamesDC.FP_RATE] - results[NamesDC.HARM]
        )
        # #### finished
        self.MODEL_NAMES = modelnames + [NamesDC.NONE_MODEL, NamesDC.ALL_MODEL]
        self.NUMBER_OF_MODELS = len(self.MODEL_NAMES)
        self.NET_BENEFIT = results
        self.CALCULATED=True
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # NOTE add smoother paramter to allow for a different smoothing function.
    def plot(self,
             ax: plt.Axes | None = None,
             col_dict: dict[str,str] | None = None,
             line_dict: dict[str,str] | None = None,
             smoother: Callable | None = lowess,
             linewidth:float=0.8,
             figsize:tuple[float,float]=(6, 6),
             kwargs_smoother:dict[str,Any] | None = None,
             kwargs_plot:dict[str,Any] | None = None,
             ) -> tuple[plt.Figure, plt.Axes]:
        """
        Plots decision curves for one or more models.
        
        Visualises the net benefit across risk thresholds for each prediction
        model, allowing direct comparison of model utility relative to 'treat all'
        and 'treat none' strategies. Curves can optionally be smoothed with
        LOWESS, and all visual properties are customisable.
        
        Parameters
        ----------
        ax : `plt.axes` or `None`, default `NoneType`
            An optional matplotlib axis. If supplied the function works on the
            axis. Otherwise will internally generate a figure and axes pair.
        col_dict: `dict` [`str`,`str`] or `None`, default `NoneType`
            A dictionary with the model names as keys and the colours as values.
            Set to `Nonetype` to plot each line in black.
        line_dict: `dict` [`str`,`str`], default `NoneType`
            A dictionary with the model names as keys and the linetypes as values.
            Set to `Nonetype` to use a solid line for all models.
        linewidth : `float`, default 0.8
            Width of the decision curve lines.
        smoother : `callable` or `None`, default `lowess`
            A smoothing function such as `lowess` from `statsmodels`, or any
            user-defined callable accepting `y`, `x`, and keyword arguments.
            The function should return the predicted y on the risk scale. If
            `None`, the raw y-values will be plotted against the predicted
            scores. This can be used to plot pre-computed data.
        figsize : `tuple` [`float`,`float`], default (6, 6),
            The figure size in inches, when ax is `None`.
        kwargs_smoother : `dict` [`str`,`any`] or `None`, default None
            Additional keyword arguments passed to a `smoother` function
            (e.g., `it`, `delta`, `return_sorted`).
        kwargs_plot : `dict` [`str`,`any`] or `None`, default None
            Additional keyword arguments passed to `ax.plot`.
        
        
        Returns
        -------
        fig : matplotlib.figure.Figure
            The created or inherited figure object.
        ax : matplotlib.axes.Axes
            The axis containing the rendered decision curves.
        
        Raises
        ------
        RuntimeError
            If `calc_net_benefit()` has not been called before plotting.
        InputValidationError
            If the number of colours or line styles does not match the number of
            models.
        
        Notes
        -----
        - The y-axis represents net benefit.
        - The x-axis represents risk thresholds (typically between 0 and 1).
        """
        
        # make sure net_benefit is available
        if self.CALCULATED == False:
            raise RuntimeError('calc_net_benefit must be run before plotting.')
        # #### check input
        is_type(ax, (type(None), plt.Axes))
        is_type(line_dict, (type(None), dict))
        is_type(col_dict, (type(None), dict))
        is_type(smoother, (type(None), Callable))
        if line_dict is None:
            line_dict = {j:'-' for j in self.MODEL_NAMES }
        if self.NUMBER_OF_MODELS != len(line_dict):
            raise InputValidationError(
                'Please include a dictionary with exactly {} entries, '
                'to match the number of models. '
                'Current number supplied for `line_dict` is {}.'.format(
                    self.NUMBER_OF_MODELS, len(line_dict)
                )
            )
        if col_dict is None:
            col_dict ={k:'black' for k in self.MODEL_NAMES}
        if self.NUMBER_OF_MODELS != len(col_dict):
            raise InputValidationError(
                'Please include a dictionary with exactly {} entries, '
                'to match the number of models. '
                'Current number supplied for `col_dict` is {}.'.format(
                    self.NUMBER_OF_MODELS, len(col_dict)
                )
            )
        # map None to empty dict
        kwargs_smoother = kwargs_smoother or {}
        kwargs_plot = kwargs_plot or {}
        # #### should we create a figure and axis
        if ax is None:
            f, ax = plt.subplots(figsize=figsize)
        else:
            f = ax.figure
        # #### plot stuff
        self.NET_BENEFIT[NamesDC.COL] = pd.Series(col_dict)
        self.NET_BENEFIT[NamesDC.LTY] = pd.Series(line_dict)
        # how many models are there?
        modelnames = list(self.NET_BENEFIT.index.unique())
        # plot a line per model
        for model in modelnames:
            single_model_df = self.NET_BENEFIT.loc[model]
            # sorting ascending
            single_model_df = single_model_df.sort_values(
                by=NamesDC.THRESHOLD)
            X = single_model_df[NamesDC.THRESHOLD].to_numpy()
            Y = single_model_df[NamesDC.NETBENEFIT].to_numpy()
            # do we need to use a lowess
            if smoother is not None:
                if smoother is lowess:
                    # making sure we get a single vector
                    kwargs_smoother = _update_kwargs(
                        update_dict=kwargs_smoother,
                        return_sorted=False,
                    )
                Y_PLOT=smoother(Y, X,
                              **kwargs_smoother,
                              )
                # raising an error if needed
                if hasattr(Y_PLOT, 'shape'):
                    if len(Y_PLOT.shape) == 2 and Y_PLOT.shape[1] != 1:
                        raise IndexError(
                            '`Y_PLOT` should be a column vector '
                            f'the current shape is: {Y_PLOT.shape}.'
                        )
            else:
                Y_PLOT = Y
            # The actual plotting
            new_kwargs_plot = _update_kwargs(
                update_dict=kwargs_plot,
                linestyle=single_model_df[NamesDC.LTY].iloc[0],
                color=single_model_df[NamesDC.COL].iloc[0],
                lw=linewidth,
            )
            ax.plot( X, Y_PLOT,
                    **new_kwargs_plot,
                    )
        # ##### some light tweaks to the axes
        # ticks
        ax.tick_params(axis="x",
                               rotation=0,
                               labelsize=self.TICK_LAB_SIZE,
                               length=self.TICK_LEN,
                               width=self.TICK_WIDTH,
                               )
        ax.tick_params(axis="y",
                               rotation=0,
                               labelsize=self.TICK_LAB_SIZE,
                               length=self.TICK_LEN,
                               width=self.TICK_WIDTH,
                               )
        # limits
        YSPAN=ax.get_ylim()
        YSPAN=np.abs(YSPAN[1] - YSPAN[0])
        ax.set_xlim(0, ax.get_xlim()[1])
        ax.set_ylim(0 - np.max((0.01,0.01*YSPAN)), ax.get_ylim()[1])
        # add lables
        ax.set_ylabel('Net benefit',
                      fontsize=self.LABEL_FONT_SIZE,
                      labelpad=self.LABEL_PAD,
                      )
        ax.set_xlabel('Threshold',
                      fontsize=self.LABEL_FONT_SIZE,
                      labelpad=self.LABEL_PAD,
                      )
        # Hide the right and top spines
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)
        # ##### returns
        return f, ax

